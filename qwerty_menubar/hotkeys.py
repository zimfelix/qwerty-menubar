"""Event-driven Carbon hotkeys. No keyboard event tap or input-monitoring permission."""

import ctypes
import traceback
from dataclasses import dataclass

from qwerty_menubar.shortcuts import ShortcutError, conflict_reason

SIGNATURE = int.from_bytes(b"QWRT", "big")
KEYBOARD_CLASS = int.from_bytes(b"keyb", "big")
PRESSED = 5
RELEASED = 6


class HotKeyID(ctypes.Structure):
    _fields_ = [("signature", ctypes.c_uint32), ("id", ctypes.c_uint32)]


class EventType(ctypes.Structure):
    _fields_ = [("event_class", ctypes.c_uint32), ("event_kind", ctypes.c_uint32)]


@dataclass
class Registration:
    reference: ctypes.c_void_p
    identifier: int


class CarbonBackend:
    def __init__(self, callback):
        self.callback = callback
        self.library = ctypes.CDLL("/System/Library/Frameworks/Carbon.framework/Carbon")
        self.core = ctypes.CDLL(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
        self.handler = ctypes.c_void_p()
        self.serial = 0
        self._configure()
        self._install_handler()

    def _configure(self):
        pointer, uint, status = ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32
        signatures = {
            "GetApplicationEventTarget": ([], pointer),
            "RegisterEventHotKey": (
                [uint, uint, HotKeyID, pointer, uint, ctypes.POINTER(pointer)],
                status,
            ),
            "UnregisterEventHotKey": ([pointer], status),
            "InstallEventHandler": (
                [
                    pointer,
                    pointer,
                    uint,
                    ctypes.POINTER(EventType),
                    pointer,
                    ctypes.POINTER(pointer),
                ],
                status,
            ),
            "RemoveEventHandler": ([pointer], status),
            "GetEventKind": ([pointer], uint),
            "GetEventParameter": ([pointer, uint, uint, pointer, uint, pointer, pointer], status),
            "CopySymbolicHotKeys": ([ctypes.POINTER(pointer)], status),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.library, name)
            function.argtypes, function.restype = arguments, result
        self.core.CFRelease.argtypes = [pointer]
        self.core.CFRelease.restype = None

    def _install_handler(self):
        handler_type = ctypes.CFUNCTYPE(
            ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        )
        self.native_callback = handler_type(self._event)
        types = (EventType * 2)(
            EventType(KEYBOARD_CLASS, PRESSED), EventType(KEYBOARD_CLASS, RELEASED)
        )
        result = self.library.InstallEventHandler(
            self.library.GetApplicationEventTarget(),
            self.native_callback,
            2,
            types,
            None,
            ctypes.byref(self.handler),
        )
        if result:
            raise ShortcutError(f"Globaler Hotkey-Dienst nicht verfügbar (macOS {result}).")

    def _event(self, next_handler, event, context):
        try:
            identifier = HotKeyID()
            result = self.library.GetEventParameter(
                event,
                int.from_bytes(b"----", "big"),
                int.from_bytes(b"hkid", "big"),
                None,
                ctypes.sizeof(identifier),
                None,
                ctypes.byref(identifier),
            )
            if result or identifier.signature != SIGNATURE:
                return -9874  # eventNotHandledErr
            self.callback(identifier.id, self.library.GetEventKind(event) == PRESSED)
            return 0
        except Exception:
            traceback.print_exc()  # exceptions must never cross the native callback boundary
            return -9874

    def system_hotkeys(self):
        import objc

        result = ctypes.c_void_p()
        status = self.library.CopySymbolicHotKeys(ctypes.byref(result))
        if status or not result.value:
            raise ShortcutError(
                "macOS-Systemkürzel konnten nicht geprüft werden. Nicht gespeichert."
            )
        try:
            array = objc.objc_object(c_void_p=result.value)
            return [dict(item) for item in array]
        finally:
            self.core.CFRelease(result)

    def register(self, shortcut):
        # macOS only reports exclusive conflicts. Probe briefly, then release it.
        # A shared final registration never suppresses another app's shared hotkey.
        probe = self._register(shortcut, 1)
        self.unregister(probe)
        return self._register(shortcut, 0)

    def _register(self, shortcut, options):
        self.serial += 1
        reference = ctypes.c_void_p()
        result = self.library.RegisterEventHotKey(
            shortcut.keycode,
            shortcut.modifiers,
            HotKeyID(SIGNATURE, self.serial),
            self.library.GetApplicationEventTarget(),
            options,
            ctypes.byref(reference),
        )
        if result == -9878:
            raise ShortcutError(
                "Bereits von einem exklusiven globalen Hotkey belegt. Nicht gespeichert."
            )
        if result:
            raise ShortcutError(f"macOS hat diese Kombination abgelehnt ({result}).")
        return Registration(reference, self.serial)

    def unregister(self, registration):
        self.library.UnregisterEventHotKey(registration.reference)

    def close(self):
        if self.handler.value:
            self.library.RemoveEventHandler(self.handler)
            self.handler = ctypes.c_void_p()


class HotkeyManager:
    def __init__(self, callback, backend=None):
        self.callback = callback
        self.registration = None
        self.shortcut = None
        self.down = False
        self.backend = backend or CarbonBackend(self._event)

    def _event(self, identifier, pressed):
        if not self.registration or identifier != self.registration.identifier:
            return
        if pressed and not self.down:
            self.down = True
            self.callback()
        elif not pressed:
            self.down = False

    def assign(self, shortcut, persist):
        if shortcut is None:
            persist(None)
            self.clear()
            return
        reason = conflict_reason(shortcut, self.backend.system_hotkeys())
        if reason:
            raise ShortcutError(reason)
        if self.shortcut and self.shortcut.identity == shortcut.identity:
            persist(shortcut)
            self.shortcut = shortcut
            return
        candidate = self.backend.register(shortcut)
        try:
            persist(shortcut)
        except Exception:
            self.backend.unregister(candidate)
            raise
        previous = self.registration
        self.registration, self.shortcut, self.down = candidate, shortcut, False
        if previous:
            self.backend.unregister(previous)

    def clear(self):
        if self.registration:
            self.backend.unregister(self.registration)
        self.registration, self.shortcut, self.down = None, None, False

    def close(self):
        self.clear()
        self.backend.close()
