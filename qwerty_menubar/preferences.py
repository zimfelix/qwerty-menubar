"""Small, validated JSON preferences; atomic writes, no polling."""

import json
import os
import tempfile
from pathlib import Path

from qwerty_menubar.constants import BUNDLE_ID
from qwerty_menubar.shortcuts import Shortcut, ShortcutError


class PreferencesError(ValueError):
    pass


class Preferences:
    def __init__(self, path=None):
        self.path = (
            Path(path)
            if path is not None
            else (Path.home() / "Library" / "Application Support" / BUNDLE_ID / "settings.json")
        )

    def load_shortcut(self):
        if not self.path.exists():
            return None
        try:
            value = json.loads(self.path.read_text())
            if (
                not isinstance(value, dict)
                or set(value) != {"version", "hotkey"}
                or type(value["version"]) is not int
                or value["version"] != 1
            ):
                raise PreferencesError("Unbekanntes Einstellungsformat.")
            return Shortcut.from_dict(value["hotkey"]) if value.get("hotkey") is not None else None
        except (OSError, ValueError, KeyError, ShortcutError) as error:
            raise PreferencesError(
                f"Einstellungen konnten nicht geladen werden: {error}"
            ) from error

    def save_shortcut(self, shortcut):
        value = {"version": 1, "hotkey": shortcut.as_dict() if shortcut else None}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".settings-", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w") as handle:
                json.dump(value, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            Path(temporary).unlink(missing_ok=True)

    def remove(self):
        self.path.unlink(missing_ok=True)
        try:
            self.path.parent.rmdir()
        except OSError:
            pass  # leave unrelated files alone
