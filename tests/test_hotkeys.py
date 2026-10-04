import ctypes
from types import SimpleNamespace

import pytest

from qwerty_menubar.hotkeys import CarbonBackend, HotkeyManager
from qwerty_menubar.shortcuts import ShortcutError, parse_shortcut


class FakeCarbon:
    def __init__(self, failure=0):
        self.options, self.removed, self.failure = [], [], failure

    def GetApplicationEventTarget(self):
        return 123

    def RegisterEventHotKey(self, code, modifiers, identifier, target, options, out):
        self.options.append(options)
        if self.failure:
            return self.failure
        ctypes.cast(out, ctypes.POINTER(ctypes.c_void_p))[0] = 100 + len(self.options)
        return 0

    def UnregisterEventHotKey(self, reference):
        self.removed.append(reference.value)
        return 0


def test_native_backend_only_probes_exclusively_then_registers_shared():
    backend = CarbonBackend.__new__(CarbonBackend)
    backend.library, backend.serial = FakeCarbon(), 0
    registration = backend.register(parse_shortcut("ctrl+alt+cmd+k"))
    assert backend.library.options == [1, 0]
    assert backend.library.removed == [101]
    assert registration.reference.value == 102


def test_native_backend_exclusive_conflict_never_registers_shared():
    backend = CarbonBackend.__new__(CarbonBackend)
    backend.library, backend.serial = FakeCarbon(-9878), 0
    with pytest.raises(ShortcutError, match="exklusiven"):
        backend.register(parse_shortcut("ctrl+alt+cmd+k"))
    assert backend.library.options == [1]
    assert backend.library.removed == []


class FakeBackend:
    def __init__(self):
        self.entries, self.registered, self.removed = [], [], []
        self.failure = None

    def system_hotkeys(self):
        return self.entries

    def register(self, shortcut):
        if self.failure:
            raise self.failure
        registration = SimpleNamespace(identifier=len(self.registered) + 1)
        self.registered.append(registration)
        return registration

    def unregister(self, registration):
        self.removed.append(registration)

    def close(self):
        pass


def test_system_conflict_does_not_register_or_persist():
    backend = FakeBackend()
    backend.entries = [
        {
            "kHISymbolicHotKeyEnabled": True,
            "kHISymbolicHotKeyCode": 40,
            "kHISymbolicHotKeyModifiers": 6400,
        }
    ]
    manager = HotkeyManager(lambda: None, backend)
    with pytest.raises(ShortcutError, match="macOS"):
        manager.assign(parse_shortcut("ctrl+alt+cmd+k"), lambda value: pytest.fail("saved"))
    assert backend.registered == []


def test_registration_conflict_preserves_old_shortcut():
    backend = FakeBackend()
    manager = HotkeyManager(lambda: None, backend)
    old = parse_shortcut("ctrl+alt+cmd+k")
    manager.assign(old, lambda value: None)
    backend.failure = ShortcutError("already in use")
    with pytest.raises(ShortcutError):
        manager.assign(parse_shortcut("ctrl+alt+cmd+j"), lambda value: pytest.fail("saved"))
    assert manager.shortcut == old
    assert backend.removed == []


def test_failed_persistence_unregisters_only_candidate():
    backend = FakeBackend()
    manager = HotkeyManager(lambda: None, backend)
    old = parse_shortcut("ctrl+alt+cmd+k")
    manager.assign(old, lambda value: None)
    original = manager.registration

    def fail(value):
        raise OSError("cannot save")

    with pytest.raises(OSError):
        manager.assign(parse_shortcut("ctrl+alt+cmd+j"), fail)
    assert manager.registration is original
    assert manager.shortcut == old
    assert backend.removed == [backend.registered[-1]]


def test_success_replaces_registration_and_same_combo_does_not_duplicate():
    backend = FakeBackend()
    manager = HotkeyManager(lambda: None, backend)
    first, second = parse_shortcut("ctrl+alt+cmd+k"), parse_shortcut("ctrl+alt+cmd+j")
    manager.assign(first, lambda value: None)
    manager.assign(second, lambda value: None)
    assert manager.shortcut == second
    assert backend.removed == [backend.registered[0]]
    manager.assign(second, lambda value: None)
    assert len(backend.registered) == 2


def test_repeat_does_not_toggle_repeatedly_and_unrelated_events_are_ignored():
    backend, calls = FakeBackend(), []
    manager = HotkeyManager(lambda: calls.append("toggle"), backend)
    manager.assign(parse_shortcut("ctrl+alt+cmd+k"), lambda value: None)
    manager._event(999, True)
    manager._event(1, True)
    manager._event(1, True)
    assert calls == ["toggle"]
    manager._event(1, False)
    manager._event(1, True)
    assert len(calls) == 2
    manager.close()
    assert manager.shortcut is None


def test_failed_clear_preserves_active_hotkey():
    backend = FakeBackend()
    manager = HotkeyManager(lambda: None, backend)
    manager.assign(parse_shortcut("ctrl+alt+cmd+k"), lambda value: None)
    with pytest.raises(OSError):
        manager.assign(None, lambda value: (_ for _ in ()).throw(OSError("disk")))
    assert manager.shortcut is not None
    assert backend.removed == []
