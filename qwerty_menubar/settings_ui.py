"""Compact native shortcut recorder. Captures keys only while its button has focus."""

import objc
from AppKit import (
    NSBackingStoreBuffered,
    NSBezelStyleRounded,
    NSButton,
    NSColor,
    NSFont,
    NSFontWeightMedium,
    NSLineBreakByWordWrapping,
    NSMakeRect,
    NSObject,
    NSPanel,
    NSTextField,
    NSWindowStyleMaskClosable,
    NSWindowStyleMaskTitled,
)

from qwerty_menubar.shortcuts import from_event, parse_shortcut


class ShortcutRecorder(NSButton):
    def acceptsFirstResponder(self):
        return True

    def keyDown_(self, event):
        if not getattr(self, "recording", False):
            objc.super(ShortcutRecorder, self).keyDown_(event)
            return
        if event.keyCode() == 53 and not event.modifierFlags() & (0xF << 17):
            self.owner.cancel_recording()
            return
        self.owner.receive_event(event)

    def performKeyEquivalent_(self, event):
        if getattr(self, "recording", False):
            self.keyDown_(event)
            return True  # prevent a captured ⌘ shortcut reaching menus
        return objc.super(ShortcutRecorder, self).performKeyEquivalent_(event)

    def resignFirstResponder(self):
        if getattr(self, "recording", False):
            self.owner.cancel_recording()
        return True


class ShortcutWindow(NSObject):
    @objc.python_method
    def configure(self, owner):
        self.owner = owner
        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 410, 385),
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable,
            NSBackingStoreBuffered,
            False,
        )
        self.panel.setTitle_("Tastenkürzel")
        self.panel.setTitlebarAppearsTransparent_(True)
        self.panel.setMovableByWindowBackground_(True)
        self.panel.setFloatingPanel_(True)
        self.panel.setHidesOnDeactivate_(False)
        self.panel.setReleasedWhenClosed_(False)
        self.panel.setDelegate_(self)
        self._build_controls()
        return self

    @objc.python_method
    def _label(self, text, rect, size=12):
        label = NSTextField.labelWithString_(text)
        label.setFrame_(NSMakeRect(*rect))
        label.setFont_(NSFont.systemFontOfSize_(size))
        label.setLineBreakMode_(NSLineBreakByWordWrapping)
        label.setMaximumNumberOfLines_(0)
        self.panel.contentView().addSubview_(label)
        return label

    @objc.python_method
    def _build_controls(self):
        self._label("Tastatur ein- / ausblenden", (24, 337, 362, 25), 17)
        self._label("Klicken, dann eine Tastenkombination drücken.", (24, 310, 362, 22))
        self.recorder = ShortcutRecorder.alloc().initWithFrame_(NSMakeRect(24, 253, 362, 46))
        self.recorder.owner, self.recorder.recording = self, False
        self.recorder.setBezelStyle_(NSBezelStyleRounded)
        self.recorder.setFont_(NSFont.systemFontOfSize_weight_(17, NSFontWeightMedium))
        self.recorder.setTarget_(self)
        self.recorder.setAction_("startRecording:")
        self.recorder.setAccessibilityLabel_("Globales Tastenkürzel aufnehmen")
        self.panel.contentView().addSubview_(self.recorder)
        self._label(
            "Falls macOS den Tastendruck abfängt: manuell eingeben.", (24, 227, 362, 19), 11
        )
        self.manual = NSTextField.alloc().initWithFrame_(NSMakeRect(24, 193, 264, 27))
        self.manual.setPlaceholderString_("ctrl+alt+cmd+k")
        self.manual.setAccessibilityLabel_("Tastenkombination manuell eingeben")
        self.manual.setTarget_(self)
        self.manual.setAction_("submitManual:")
        self.panel.contentView().addSubview_(self.manual)
        check = NSButton.alloc().initWithFrame_(NSMakeRect(298, 191, 88, 30))
        check.setTitle_("Prüfen")
        check.setBezelStyle_(NSBezelStyleRounded)
        check.setTarget_(self)
        check.setAction_("submitManual:")
        self.panel.contentView().addSubview_(check)
        self.feedback = self._label("", (24, 130, 362, 55))
        note = self._label(
            "macOS-Kürzel und exklusive globale Hotkeys werden geprüft. "
            "Geteilte und app-interne Kürzel sind nicht vollständig erkennbar.",
            (24, 68, 362, 45),
            11,
        )
        note.setTextColor_(NSColor.secondaryLabelColor())
        for title, action, x, width in [
            ("Entfernen", "clearShortcut:", 24, 104),
            ("Fertig", "closeWindow:", 298, 88),
        ]:
            button = NSButton.alloc().initWithFrame_(NSMakeRect(x, 10, width, 30))
            button.setTitle_(title)
            button.setBezelStyle_(NSBezelStyleRounded)
            button.setTarget_(self)
            button.setAction_(action)
            self.panel.contentView().addSubview_(button)
        self.refresh()

    @objc.python_method
    def refresh(self):
        shortcut = self.owner.hotkeys.shortcut if self.owner.hotkeys else None
        self.recorder.setTitle_(shortcut.title if shortcut else "Kürzel festlegen …")
        self.recorder.setAccessibilityValue_(shortcut.title if shortcut else "Nicht zugewiesen")

    @objc.python_method
    def show(self, screen):
        frame = screen.visibleFrame()
        self.panel.setFrameOrigin_(
            (
                frame.origin.x + (frame.size.width - 410) / 2,
                frame.origin.y + (frame.size.height - 410) / 2,
            )
        )
        self.refresh()
        self.set_feedback(
            self.owner.startup_error
            or "⌘, ⌃ oder ⌥ plus eine Taste. Escape bricht die Aufnahme ab.",
            bool(self.owner.startup_error),
        )
        self.panel.makeKeyAndOrderFront_(None)

    @objc.python_method
    def set_feedback(self, message, error=False):
        self.feedback.setStringValue_(message)
        self.feedback.setTextColor_(
            NSColor.systemRedColor() if error else NSColor.secondaryLabelColor()
        )

    def startRecording_(self, sender):
        self.recorder.recording = True
        self.recorder.setTitle_("Tastenkombination drücken …")
        self.set_feedback(
            "Nur Modifier-Tasten allein werden nicht gespeichert. Escape = Abbrechen."
        )
        self.panel.makeFirstResponder_(self.recorder)

    @objc.python_method
    def cancel_recording(self):
        self.recorder.recording = False
        self.refresh()

    @objc.python_method
    def receive_event(self, event):
        try:
            shortcut = from_event(
                event.keyCode(), event.modifierFlags(), event.charactersIgnoringModifiers()
            )
            self.owner.assign_shortcut(shortcut)
        except (ValueError, OSError) as error:
            self.set_feedback(str(error), True)
            self.recorder.setTitle_("Andere Kombination drücken …")
            return  # remain in recording mode, keeping the previous hotkey
        self.cancel_recording()
        self.set_feedback(f"{shortcut.title} gespeichert. Globaler Hotkey ist aktiv.")
        self.panel.makeFirstResponder_(None)

    def submitManual_(self, sender):
        self.cancel_recording()
        try:
            shortcut = parse_shortcut(self.manual.stringValue())
            self.owner.assign_shortcut(shortcut)
        except (ValueError, OSError) as error:
            self.set_feedback(str(error), True)
            return
        self.refresh()
        self.set_feedback(f"{shortcut.title} gespeichert. Globaler Hotkey ist aktiv.")

    def clearShortcut_(self, sender):
        try:
            self.owner.assign_shortcut(None)
        except (ValueError, OSError) as error:
            self.set_feedback(str(error), True)
            return
        self.cancel_recording()
        self.set_feedback("Tastenkürzel entfernt.")

    def closeWindow_(self, sender):
        self.panel.close()

    def cancelOperation_(self, sender):
        if self.recorder.recording:
            self.cancel_recording()
        else:
            self.panel.close()

    def windowDidResignKey_(self, notification):
        self.cancel_recording()

    def windowWillClose_(self, notification):
        self.cancel_recording()
        self.owner.settings_window_closed()
