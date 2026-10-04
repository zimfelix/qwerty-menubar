import json

import pytest

from qwerty_menubar.preferences import Preferences, PreferencesError
from qwerty_menubar.shortcuts import parse_shortcut


def test_missing_preferences_default_to_no_hotkey(tmp_path):
    preferences = Preferences(tmp_path / "settings.json")
    assert preferences.load_shortcut() is None
    assert not preferences.path.exists()


def test_preferences_roundtrip_and_clear(tmp_path):
    preferences = Preferences(tmp_path / "config" / "settings.json")
    shortcut = parse_shortcut("ctrl+alt+cmd+k")
    preferences.save_shortcut(shortcut)
    assert preferences.load_shortcut() == shortcut
    assert preferences.path.stat().st_mode & 0o777 == 0o600
    preferences.save_shortcut(None)
    assert preferences.load_shortcut() is None


@pytest.mark.parametrize(
    "data",
    [
        "not json",
        "[]",
        '{"version":2}',
        '{"version":1,"hotkey":{"keycode":55}}',
        '{"version":1}',
        '{"version":true,"hotkey":null}',
    ],
)
def test_corrupt_settings_do_not_silently_reset(tmp_path, data):
    preferences = Preferences(tmp_path / "settings.json")
    preferences.path.write_text(data)
    with pytest.raises(PreferencesError):
        preferences.load_shortcut()
    assert preferences.path.read_text() == data


def test_failed_atomic_write_preserves_previous_settings(tmp_path, monkeypatch):
    preferences = Preferences(tmp_path / "settings.json")
    preferences.save_shortcut(parse_shortcut("ctrl+alt+cmd+k"))
    before = preferences.path.read_bytes()

    def fail_replace(source, target):
        raise OSError("disk failure")

    monkeypatch.setattr("qwerty_menubar.preferences.os.replace", fail_replace)
    with pytest.raises(OSError):
        preferences.save_shortcut(None)
    assert preferences.path.read_bytes() == before
    assert list(tmp_path.glob(".settings-*")) == []
    assert json.loads(before)["hotkey"] is not None


def test_remove_leaves_unrelated_files_untouched(tmp_path):
    folder = tmp_path / "config"
    preferences = Preferences(folder / "settings.json")
    preferences.save_shortcut(None)
    unrelated = folder / "notes.txt"
    unrelated.write_text("keep")
    preferences.remove()
    assert not preferences.path.exists()
    assert unrelated.read_text() == "keep"
