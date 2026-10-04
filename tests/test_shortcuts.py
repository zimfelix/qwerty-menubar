import pytest

from qwerty_menubar.shortcuts import (
    COMMAND,
    CONTROL,
    OPTION,
    SHIFT,
    Shortcut,
    ShortcutError,
    conflict_reason,
    from_event,
    parse_shortcut,
)


@pytest.mark.parametrize("text", ["ctrl+alt+cmd+k", "control+option+command+K", "⌃⌥⌘K"])
def test_parse_combinations(text):
    shortcut = parse_shortcut(text)
    assert shortcut.identity == (40, COMMAND | CONTROL | OPTION)
    assert shortcut.title == "⌃⌥⌘K"
    assert Shortcut.from_dict(shortcut.as_dict()) == shortcut


@pytest.mark.parametrize(
    "text", ["", "k", "shift+k", "ctrl+ctrl+k", "meta+k", "ctrl+fn", "ctrl+two keys"]
)
def test_reject_invalid_combinations(text):
    with pytest.raises(ShortcutError):
        parse_shortcut(text)


@pytest.mark.parametrize(
    "text, code",
    [("ctrl+alt+space", 49), ("ctrl+alt+f12", 111), ("ctrl+alt+left", 123), ("ctrl+alt+tab", 48)],
)
def test_special_keys(text, code):
    assert parse_shortcut(text).keycode == code


def test_cocoa_flags_are_converted_and_extra_flags_are_ignored():
    shortcut = from_event(40, (1 << 18) | (1 << 19) | (1 << 20) | (1 << 16), "k")
    assert shortcut == parse_shortcut("ctrl+alt+cmd+k")


def test_reject_bare_keys_shift_only_and_modifier_only():
    for code, modifiers in [(40, 0), (40, SHIFT), (55, COMMAND), (63, OPTION)]:
        with pytest.raises(ShortcutError):
            Shortcut(code, modifiers, "K")


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"keycode": True, "modifiers": COMMAND, "key_label": "A"},
        {"keycode": 40, "modifiers": -1, "key_label": "K"},
        {"keycode": 40, "modifiers": CONTROL, "key_label": "\n"},
    ],
)
def test_reject_malformed_saved_values(value):
    with pytest.raises(ShortcutError):
        Shortcut.from_dict(value)


def test_enabled_system_shortcut_is_rejected_but_disabled_one_is_not():
    shortcut = parse_shortcut("ctrl+alt+cmd+k")
    entry = {
        "kHISymbolicHotKeyCode": 40,
        "kHISymbolicHotKeyModifiers": shortcut.modifiers,
        "kHISymbolicHotKeyEnabled": True,
    }
    assert "macOS" in conflict_reason(shortcut, [entry])
    entry["kHISymbolicHotKeyEnabled"] = False
    assert conflict_reason(shortcut, [entry]) is None


@pytest.mark.parametrize("text", ["cmd+c", "cmd+q", "cmd+shift+z", "alt+e", "ctrl+a"])
def test_common_app_and_text_shortcuts_are_reserved(text):
    assert conflict_reason(parse_shortcut(text), []) is not None


def test_uncommon_multi_modifier_combination_is_allowed():
    assert conflict_reason(parse_shortcut("ctrl+alt+cmd+k"), []) is None
