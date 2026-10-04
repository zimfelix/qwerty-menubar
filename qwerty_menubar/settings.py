"""Settings menu, login-item controls, shortcut editor and confirmed uninstall."""

from pathlib import Path

import objc
from AppKit import (
    NSAlert,
    NSAlertSecondButtonReturn,
    NSApp,
    NSControlStateValueMixed,
    NSControlStateValueOff,
    NSControlStateValueOn,
    NSMakePoint,
    NSMenu,
    NSMenuItem,
    NSObject,
    NSWorkspace,
)
from Foundation import NSURL, NSBundle, NSOperationQueue

from qwerty_menubar.constants import BUNDLE_ID
from qwerty_menubar.hotkeys import HotkeyManager
from qwerty_menubar.lifecycle import (
    LifecycleError,
    LoginItem,
    installed_bundle,
    remove_preferences_and_lock,
)
from qwerty_menubar.preferences import Preferences
from qwerty_menubar.settings_ui import ShortcutWindow


class SettingsMenu(NSObject):
    @objc.python_method
    def configure(self, delegate):
        self.delegate = delegate
        self.busy, self.shortcut_window, self.startup_error = False, None, None
        self.preferences, self.hotkeys = Preferences(), None
        bundle = NSBundle.mainBundle()
        self.bundle_path, self.identifier = bundle.bundlePath(), bundle.bundleIdentifier()
        try:
            self.installed_path = installed_bundle(self.bundle_path, self.identifier)
        except LifecycleError:
            self.installed_path = None
        self.login = LoginItem(self.bundle_path, self.identifier)
        try:
            self.hotkeys = HotkeyManager(delegate._hotkey_pressed)
            saved = self.preferences.load_shortcut()
            if saved:
                self.hotkeys.assign(saved, lambda shortcut: None)
        except (ValueError, OSError) as error:
            self.startup_error = str(error)
        self._build_menu()
        return self

    @objc.python_method
    def _item(self, title, action):
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, "")
        item.setTarget_(self)
        self.menu.addItem_(item)
        return item

    @objc.python_method
    def _build_menu(self):
        self.menu = NSMenu.alloc().initWithTitle_("Einstellungen")
        self.menu.setAutoenablesItems_(False)
        self._item("Einstellungen", None).setEnabled_(False)
        self.menu.addItem_(NSMenuItem.separatorItem())
        self.autostart_item = self._item("Autostart · Aus", "toggleAutostart:")
        self.approval_item = self._item("In macOS freigeben …", "openLoginSettings:")
        self.shortcut_item = self._item("Tastenkürzel festlegen …", "openShortcut:")
        self.menu.addItem_(NSMenuItem.separatorItem())
        self._item("Beenden", "quit:")
        self.uninstall_item = self._item("Deinstallieren …", "uninstall:")
        self.refresh()

    @objc.python_method
    def refresh(self):
        status = self.login.status()
        self.autostart_item.setState_(
            {1: NSControlStateValueOn, 2: NSControlStateValueMixed}.get(
                status, NSControlStateValueOff
            )
        )
        self.autostart_item.setTitle_(
            {1: "Autostart · Ein", 2: "Autostart · Freigabe nötig"}.get(status, "Autostart · Aus")
        )
        self.autostart_item.setEnabled_(self.installed_path is not None)
        self.approval_item.setHidden_(status != 2)
        shortcut = self.hotkeys.shortcut if self.hotkeys else None
        self.shortcut_item.setTitle_(
            f"Tastenkürzel: {shortcut.title} …" if shortcut else "Tastenkürzel festlegen …"
        )
        self.shortcut_item.setEnabled_(self.hotkeys is not None)
        self.uninstall_item.setEnabled_(self.installed_path is not None)

    @objc.python_method
    def show(self, sender):
        self.refresh()
        self.menu.popUpMenuPositioningItem_atLocation_inView_(None, NSMakePoint(0, -4), sender)

    @objc.python_method
    def has_auxiliary_window(self):
        return self.busy or (
            self.shortcut_window is not None and self.shortcut_window.panel.isVisible()
        )

    @objc.python_method
    def assign_shortcut(self, shortcut):
        if self.hotkeys is None:
            raise ValueError(self.startup_error or "Hotkey-Dienst nicht verfügbar.")
        self.hotkeys.assign(shortcut, self.preferences.save_shortcut)
        self.startup_error = None
        self.refresh()

    def openShortcut_(self, sender):
        self.busy = True
        screen = self.delegate.display_screen()
        if self.delegate.popover:
            self.delegate.popover.performClose_(sender)
        if self.shortcut_window is None:
            self.shortcut_window = ShortcutWindow.alloc().init().configure(self)
        NSApp.activateIgnoringOtherApps_(True)
        self.shortcut_window.show(screen)
        self.busy = False

    @objc.python_method
    def settings_window_closed(self):
        if not self.delegate.popover or not self.delegate.popover.isShown():
            NSApp.hide_(None)

    @objc.python_method
    def _alert(self, title, message, destructive=False):
        screen = self.delegate.display_screen()
        self.busy = True
        if self.delegate.popover:
            self.delegate.popover.performClose_(None)
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(message)
        alert.addButtonWithTitle_("Abbrechen" if destructive else "OK")
        if destructive:
            alert.addButtonWithTitle_("Deinstallieren")
            alert.buttons()[1].setKeyEquivalent_("")  # Return must never uninstall
        window = alert.window()
        frame = screen.visibleFrame()
        window.setFrameOrigin_(
            (
                frame.origin.x + (frame.size.width - window.frame().size.width) / 2,
                frame.origin.y + (frame.size.height - window.frame().size.height) / 2,
            )
        )
        NSApp.activateIgnoringOtherApps_(True)
        try:
            return alert.runModal()
        finally:
            self.busy = False
            if not self.has_auxiliary_window():
                NSApp.hide_(None)

    def toggleAutostart_(self, sender):
        try:
            self.login.set_enabled(self.login.status() not in (1, 2))
        except (ValueError, OSError) as error:
            self._alert("Autostart nicht geändert", str(error))
        self.refresh()

    def openLoginSettings_(self, sender):
        self.login.open_settings()

    def quit_(self, sender):
        self.delegate.quit_(sender)

    def uninstall_(self, sender):
        if self.installed_path is None:
            return
        result = self._alert(
            "QWERTY Menu Bar deinstallieren?",
            "Die laufende App wird in den Papierkorb verschoben. Autostart, Tastenkürzel und "
            "Einstellungen werden entfernt. Dein Quellprojekt und GitHub-Repo bleiben erhalten.",
            True,
        )
        if result != NSAlertSecondButtonReturn:
            return
        previous_status = self.login.status()
        try:
            bundle = installed_bundle(self.bundle_path, self.identifier)
            if previous_status in (1, 2):
                self.login.set_enabled(False)
        except (ValueError, OSError) as error:
            self._alert("Deinstallation abgebrochen", str(error))
            return
        self.busy = True
        url = NSURL.fileURLWithPath_isDirectory_(str(bundle), True)
        self.pending_recycle = lambda mapping, error: (
            NSOperationQueue.mainQueue().addOperationWithBlock_(
                lambda: self._recycled(error, previous_status)
            )
        )
        NSWorkspace.sharedWorkspace().recycleURLs_completionHandler_([url], self.pending_recycle)

    @objc.python_method
    def _recycled(self, error, previous_status):
        self.busy, self.pending_recycle = False, None
        if error:
            message = error.localizedDescription()
            if previous_status in (1, 2):
                try:
                    self.login.set_enabled(True)
                except ValueError as restore_error:
                    message += f"\nAutostart-Rücknahme fehlgeschlagen: {restore_error}"
            self._alert("App konnte nicht entfernt werden", message)
            return
        try:
            remove_preferences_and_lock(
                self.preferences, Path.home() / "Library" / "Caches" / BUNDLE_ID
            )
        except OSError as cleanup_error:
            self._alert(
                "App liegt im Papierkorb",
                f"Einstellungen konnten nicht vollständig entfernt werden: {cleanup_error}",
            )
        NSApp.terminate_(None)

    @objc.python_method
    def close(self):
        if self.hotkeys:
            self.hotkeys.close()
