"""Opt-in native conflict checks. Temporary registrations are always released."""

import subprocess
import sys

from AppKit import NSApplication, NSApplicationActivationPolicyAccessory

from qwerty_menubar.hotkeys import CarbonBackend
from qwerty_menubar.shortcuts import ShortcutError, conflict_reason, parse_shortcut

CHILD = """
import ctypes, sys
from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
from qwerty_menubar.hotkeys import CarbonBackend, HotKeyID, Registration, SIGNATURE
from qwerty_menubar.shortcuts import parse_shortcut
app = NSApplication.sharedApplication()
app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
backend = CarbonBackend(lambda identifier, pressed: None)
shortcut = parse_shortcut('ctrl+alt+cmd+f19')
reference = ctypes.c_void_p()
status = backend.library.RegisterEventHotKey(shortcut.keycode, shortcut.modifiers,
    HotKeyID(SIGNATURE, 42), backend.library.GetApplicationEventTarget(), int(sys.argv[1]),
    ctypes.byref(reference))
print('READY' if status == 0 else 'ERROR:' + str(status), flush=True)
try:
    sys.stdin.readline()
finally:
    if status == 0:
        backend.unregister(Registration(reference, 42))
    backend.close()
"""


def check_collision(backend, exclusive):
    child = subprocess.Popen(
        [sys.executable, "-u", "-c", CHILD, str(int(exclusive))],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        ready = child.stdout.readline().strip()
        assert ready == "READY", f"Cannot reserve test combination: {ready}"
        try:
            registration = backend.register(parse_shortcut("ctrl+alt+cmd+f19"))
        except ShortcutError as error:
            assert "belegt" in str(error)
            print(f"Cross-process conflict rejected (exclusive={exclusive})")
        else:
            backend.unregister(registration)
            if exclusive:
                raise AssertionError("macOS accepted a conflicting exclusive hotkey")
            print(
                "Confirmed macOS limitation: shared hotkeys are not enumerable; "
                "no exclusive takeover"
            )
    finally:
        child.communicate("stop\n", timeout=10)


def main():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    backend = CarbonBackend(lambda identifier, pressed: None)
    try:
        system_keys = backend.system_hotkeys()
        assert len(system_keys) > 0
        print(f"Read {len(system_keys)} system shortcut definitions")
        assert conflict_reason(parse_shortcut("cmd+space"), system_keys)
        check_collision(backend, True)
        check_collision(backend, False)
    finally:
        backend.close()


if __name__ == "__main__":
    main()
