"""Opt-in native settings checks with temporary preferences and a temporary app copy."""

import shutil
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from AppKit import NSApplication, NSApplicationActivationPolicyAccessory, NSStatusBar, NSWorkspace
from Foundation import NSURL, NSDate, NSRunLoop

from qwerty_menubar.app import AppDelegate
from qwerty_menubar.preferences import Preferences
from qwerty_menubar.settings_ui import ShortcutWindow
from qwerty_menubar.shortcuts import parse_shortcut


def check_recorder(delegate, folder):
    settings = delegate.settings
    settings.preferences = Preferences(folder / "settings.json")
    assert settings.installed_path is None, "Run this from source, not from a user-installed app"
    assert not settings.autostart_item.isEnabled()
    assert not settings.uninstall_item.isEnabled()
    editor = ShortcutWindow.alloc().init().configure(settings)
    good = SimpleNamespace(
        keyCode=lambda: 40,
        modifierFlags=lambda: (1 << 18) | (1 << 19) | (1 << 20),
        charactersIgnoringModifiers=lambda: "k",
    )
    bad = SimpleNamespace(
        keyCode=lambda: 49, modifierFlags=lambda: 1 << 20, charactersIgnoringModifiers=lambda: " "
    )
    editor.startRecording_(None)
    editor.receive_event(good)
    assert settings.hotkeys.shortcut == parse_shortcut("ctrl+alt+cmd+k")
    assert editor.recorder.title() == "⌃⌥⌘K"
    assert settings.preferences.load_shortcut() == settings.hotkeys.shortcut
    editor.startRecording_(None)
    editor.receive_event(bad)
    assert "macOS" in editor.feedback.stringValue()
    assert settings.hotkeys.shortcut == parse_shortcut("ctrl+alt+cmd+k")
    editor.clearShortcut_(None)
    assert settings.hotkeys.shortcut is None
    assert settings.preferences.load_shortcut() is None
    editor.panel.close()
    print("Native recorder: assign, reject system conflict, retain old key, clear: OK")


def check_recycle(folder):
    source = Path("dist/QWERTY Menu Bar.app").resolve()
    target = folder / "QWERTY Menu Bar.app"
    shutil.copytree(source, target, symlinks=True)
    url = NSURL.fileURLWithPath_isDirectory_(str(target), True)
    results = []

    def completion(mapping, error):
        results.append((mapping, error))

    NSWorkspace.sharedWorkspace().recycleURLs_completionHandler_([url], completion)
    deadline = time.monotonic() + 20
    while not results and time.monotonic() < deadline:
        NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))
    assert results, "No completion from native trash API"
    mapping, error = results[0]
    assert error is None, str(error)
    assert not target.exists() and source.exists(), "Only the temporary copy must move"
    destination = Path(mapping[url].path())
    assert destination.parent == Path.home() / ".Trash"
    shutil.move(destination, target)  # restore our test copy so temporary cleanup leaves no trash
    print("Native trash API: only temporary bundle recycled, original bundle preserved: OK")


def main():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    delegate.applicationDidFinishLaunching_(None)
    try:
        with tempfile.TemporaryDirectory(prefix="qwerty-settings-check-") as directory:
            folder = Path(directory)
            check_recorder(delegate, folder)
            check_recycle(folder)
    finally:
        delegate.settings.close()
        NSStatusBar.systemStatusBar().removeStatusItem_(delegate.status_item)
        app.setDelegate_(None)


if __name__ == "__main__":
    main()
