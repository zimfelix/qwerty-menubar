"""Shortcut data and conservative conflict rules, without macOS imports."""

from dataclasses import dataclass

COMMAND = 1 << 8
SHIFT = 1 << 9
OPTION = 1 << 11
CONTROL = 1 << 12
MODIFIER_MASK = COMMAND | SHIFT | OPTION | CONTROL

KEY_NAMES = {
    0: "A",
    1: "S",
    2: "D",
    3: "F",
    4: "H",
    5: "G",
    6: "Z",
    7: "X",
    8: "C",
    9: "V",
    10: "§",
    11: "B",
    12: "Q",
    13: "W",
    14: "E",
    15: "R",
    16: "Y",
    17: "T",
    18: "1",
    19: "2",
    20: "3",
    21: "4",
    22: "6",
    23: "5",
    24: "=",
    25: "9",
    26: "7",
    27: "−",
    28: "8",
    29: "0",
    30: "]",
    31: "O",
    32: "U",
    33: "[",
    34: "I",
    35: "P",
    36: "↩",
    37: "L",
    38: "J",
    39: "'",
    40: "K",
    41: ";",
    42: "\\",
    43: ",",
    44: "/",
    45: "N",
    46: "M",
    47: ".",
    48: "⇥",
    49: "Leertaste",
    50: "`",
    51: "⌫",
    53: "⎋",
    64: "F17",
    79: "F18",
    80: "F19",
    90: "F20",
    96: "F5",
    97: "F6",
    98: "F7",
    99: "F3",
    100: "F8",
    101: "F9",
    103: "F11",
    105: "F13",
    106: "F16",
    107: "F14",
    109: "F10",
    111: "F12",
    113: "F15",
    114: "Hilfe",
    115: "↖",
    116: "⇞",
    117: "⌦",
    118: "F4",
    119: "↘",
    120: "F2",
    121: "⇟",
    122: "F1",
    123: "←",
    124: "→",
    125: "↓",
    126: "↑",
}


class ShortcutError(ValueError):
    """A rejected shortcut; the previously assigned shortcut stays unchanged."""


@dataclass(frozen=True)
class Shortcut:
    keycode: int
    modifiers: int
    key_label: str

    def __post_init__(self):
        if type(self.keycode) is not int or self.keycode not in KEY_NAMES:
            raise ShortcutError("Diese Taste wird nicht als Hotkey unterstützt.")
        if type(self.modifiers) is not int or self.modifiers & ~MODIFIER_MASK:
            raise ShortcutError("Ungültige Modifier-Tasten.")
        if not self.modifiers & (COMMAND | CONTROL | OPTION):
            raise ShortcutError("Mindestens ⌘, ⌃ oder ⌥ plus eine Taste verwenden.")
        if not isinstance(self.key_label, str) or not 1 <= len(self.key_label) <= 20:
            raise ShortcutError("Ungültige Tastenbeschriftung.")
        if not self.key_label.isprintable():
            raise ShortcutError("Ungültige Tastenbeschriftung.")

    @property
    def title(self):
        prefix = "".join(
            symbol
            for bit, symbol in [(CONTROL, "⌃"), (OPTION, "⌥"), (SHIFT, "⇧"), (COMMAND, "⌘")]
            if self.modifiers & bit
        )
        return prefix + self.key_label

    @property
    def identity(self):
        return self.keycode, self.modifiers

    def as_dict(self):
        return {"keycode": self.keycode, "modifiers": self.modifiers, "key_label": self.key_label}

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict) or set(value) != {"keycode", "modifiers", "key_label"}:
            raise ShortcutError("Ungültige gespeicherte Tastenkombination.")
        return cls(**value)


DEFAULT_SHORTCUT = Shortcut(35, COMMAND | CONTROL | SHIFT, "P")


def from_event(keycode, flags, characters):
    modifiers = sum(
        carbon
        for cocoa, carbon in [
            (1 << 17, SHIFT),
            (1 << 18, CONTROL),
            (1 << 19, OPTION),
            (1 << 20, COMMAND),
        ]
        if flags & cocoa
    )
    label = KEY_NAMES.get(keycode, "?")
    if keycode <= 50 and keycode not in (36, 48, 49) and characters:
        if len(characters) == 1 and characters.isprintable():
            label = characters.upper()
    return Shortcut(keycode, modifiers, label)


def parse_shortcut(text):
    aliases = {
        "cmd": COMMAND,
        "command": COMMAND,
        "⌘": COMMAND,
        "ctrl": CONTROL,
        "control": CONTROL,
        "⌃": CONTROL,
        "alt": OPTION,
        "option": OPTION,
        "opt": OPTION,
        "⌥": OPTION,
        "shift": SHIFT,
        "⇧": SHIFT,
    }
    text = text.strip()
    if not text or len(text) > 60:
        raise ShortcutError("Zum Beispiel ctrl+alt+cmd+k eingeben.")
    for symbol in "⌃⌥⇧⌘":
        text = text.replace(symbol, symbol + "+")
    parts = text.lower().split("+")
    modifiers = 0
    for part in parts[:-1]:
        bit = aliases.get(part.strip())
        if bit is None or modifiers & bit:
            raise ShortcutError("Modifier: ctrl, alt, shift, cmd; danach genau eine Taste.")
        modifiers |= bit
    keys = {name.lower(): code for code, name in KEY_NAMES.items()}
    keys.update(
        {
            "space": 49,
            "tab": 48,
            "enter": 36,
            "return": 36,
            "esc": 53,
            "escape": 53,
            "backspace": 51,
            "delete": 117,
            "left": 123,
            "right": 124,
            "up": 126,
            "down": 125,
            "-": 27,
            "home": 115,
            "end": 119,
        }
    )
    code = keys.get(parts[-1].strip())
    if code is None:
        raise ShortcutError("Unbekannte Taste. Beispiel: ctrl+alt+cmd+k oder ⌃⌥⌘K.")
    return Shortcut(code, modifiers, KEY_NAMES[code])


def conflict_reason(shortcut, system_hotkeys):
    for item in system_hotkeys:
        if item.get("kHISymbolicHotKeyEnabled"):
            code = int(item["kHISymbolicHotKeyCode"])
            modifiers = int(item["kHISymbolicHotKeyModifiers"]) & MODIFIER_MASK
            if (code, modifiers) == shortcut.identity:
                return "Bereits als aktiviertes macOS-Systemkürzel belegt."
    if shortcut.modifiers == COMMAND:
        return "Einfaches ⌘-Kürzel: für übliche App-Befehle reserviert. Einen Modifier ergänzen."
    common = {6, 9, 12, 13, 15, 17, 31, 35, 45, 46, 43}
    if shortcut.modifiers == COMMAND | SHIFT and shortcut.keycode in common:
        return (
            "Übliches App-Kürzel (z. B. Fenster, Tabs oder Rückgängig). Andere Kombination wählen."
        )
    if shortcut.modifiers == OPTION and shortcut.keycode <= 50:
        return "⌥ plus Zeichentaste wird für Sonderzeichen verwendet. Einen Modifier ergänzen."
    if shortcut.modifiers == CONTROL and shortcut.keycode in {
        0,
        1,
        2,
        3,
        4,
        8,
        14,
        16,
        32,
        37,
        40,
        45,
        35,
    }:
        return "Übliches Textbearbeitungs-/Terminal-Kürzel. Einen Modifier ergänzen."
    return None
