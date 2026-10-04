"""Native, event-driven menu-bar UI. No polling or network activity."""

import fcntl
from pathlib import Path

import objc
from AppKit import (
    NSApp,
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSBox,
    NSBoxSeparator,
    NSColor,
    NSFont,
    NSFontWeightMedium,
    NSImage,
    NSImageAlignCenter,
    NSImageScaleProportionallyUpOrDown,
    NSImageSymbolConfiguration,
    NSImageView,
    NSMakeRect,
    NSMakeSize,
    NSObject,
    NSPopover,
    NSPopoverBehaviorTransient,
    NSRectEdgeMinY,
    NSRightMouseUp,
    NSScreen,
    NSStatusBar,
    NSTextField,
    NSVariableStatusItemLength,
    NSView,
    NSViewController,
)
from Foundation import NSBundle

from qwerty_menubar.constants import BUNDLE_ID, HEADER_HEIGHT
from qwerty_menubar.layout import PADDING, asset_path, popover_size
from qwerty_menubar.settings import SettingsMenu
from qwerty_menubar.ui_controls import SettingsButton


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        if hasattr(self, "status_item"):
            return
        self.popover, self.last_screen = None, None
        self._create_status_item()
        self._create_menu()

    @objc.python_method
    def _asset(self, name):
        return str(asset_path(name, NSBundle.mainBundle().resourcePath()))

    @objc.python_method
    def _create_status_item(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        button = self.status_item.button()
        icon = NSImage.alloc().initWithContentsOfFile_(self._asset("keyboard-status.png"))
        if icon is None:
            raise RuntimeError("Cannot load keyboard menu-bar icon")
        icon.setSize_(NSMakeSize(22, 16))
        icon.setTemplate_(True)
        button.setImage_(icon)
        button.setToolTip_("QWERTY-Tastatur · Klick zum Anzeigen · Rechtsklick für Einstellungen")
        button.setAccessibilityLabel_("QWERTY-Tastatur")
        button.setTarget_(self)
        button.setAction_("toggleKeyboard:")
        button.sendActionOn_((1 << 2) | (1 << 4))  # left/right mouse-up, not global hooks

    @objc.python_method
    def _create_menu(self):
        self.settings = SettingsMenu.alloc().init().configure(self)
        self.menu = self.settings.menu

    @objc.python_method
    def _create_popover(self):
        self.popover = NSPopover.alloc().init()
        self.popover.setBehavior_(NSPopoverBehaviorTransient)
        self.popover.setAnimates_(True)
        self.popover.setDelegate_(self)
        image = NSImage.alloc().initWithContentsOfFile_(self._asset("keyboard.png"))
        if image is None:
            raise RuntimeError("Cannot load QWERTY keyboard reference")
        self.image_view = NSImageView.alloc().initWithFrame_(NSMakeRect(0, 0, 1, 1))
        self.image_view.setImage_(image)
        self.image_view.setImageScaling_(NSImageScaleProportionallyUpOrDown)
        self.image_view.setImageAlignment_(NSImageAlignCenter)
        self.image_view.setAccessibilityLabel_("Logitech Mini mit QWERTY-Tastenbeschriftung")
        controller = NSViewController.alloc().init()
        controller.setView_(NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 1, 1)))
        controller.view().addSubview_(self.image_view)
        self.header_label = NSTextField.labelWithString_("QWERTY")
        self.header_label.setFont_(NSFont.systemFontOfSize_weight_(14, NSFontWeightMedium))
        self.header_label.setTextColor_(NSColor.labelColor())
        controller.view().addSubview_(self.header_label)
        self.header_separator = NSBox.alloc().initWithFrame_(NSMakeRect(0, 0, 1, 1))
        self.header_separator.setBoxType_(NSBoxSeparator)
        controller.view().addSubview_(self.header_separator)
        self.settings_button = (
            SettingsButton.alloc().initWithFrame_(NSMakeRect(0, 0, 36, 36)).configure()
        )
        symbol = NSImage.imageWithSystemSymbolName_accessibilityDescription_(
            "gearshape", "Einstellungen"
        )
        configuration = NSImageSymbolConfiguration.configurationWithPointSize_weight_(
            22, NSFontWeightMedium
        )
        self.settings_button.setImage_(symbol.imageWithSymbolConfiguration_(configuration))
        self.settings_button.setContentTintColor_(NSColor.labelColor())
        self.settings_button.setToolTip_("Einstellungen")
        self.settings_button.setAccessibilityLabel_("Einstellungen")
        self.settings_button.setTarget_(self)
        self.settings_button.setAction_("showSettings:")
        controller.view().addSubview_(self.settings_button)
        self.popover.setContentViewController_(controller)

    @objc.python_method
    def _resize_popover(self):
        width, image_height = popover_size(self.display_screen().visibleFrame().size.width)
        height = image_height + HEADER_HEIGHT
        self.popover.setContentSize_(NSMakeSize(width, height))
        self.image_view.setFrame_(
            NSMakeRect(PADDING, PADDING, width - 2 * PADDING, image_height - 2 * PADDING)
        )
        self.header_label.setFrame_(
            NSMakeRect(PADDING + 4, height - (HEADER_HEIGHT + 20) / 2, 160, 20)
        )
        self.settings_button.setFrame_(
            NSMakeRect(width - PADDING - 36, height - (HEADER_HEIGHT + 36) / 2, 36, 36)
        )
        self.header_separator.setFrame_(NSMakeRect(PADDING, image_height, width - 2 * PADDING, 1))

    @objc.python_method
    def display_screen(self):
        if self.popover and self.popover.isShown():
            window = self.image_view.window()
            if window is not None and window.screen():
                return window.screen()
        if self.last_screen:
            identifier = self.last_screen.deviceDescription()["NSScreenNumber"]
            self.last_screen = next(
                (
                    screen
                    for screen in NSScreen.screens()
                    if screen.deviceDescription()["NSScreenNumber"] == identifier
                ),
                None,
            )
        status_window = self.status_item.button().window()
        return (
            self.last_screen
            or (status_window.screen() if status_window else None)
            or NSScreen.mainScreen()
        )

    def showSettings_(self, sender):
        self.settings.show(sender)

    def toggleKeyboard_(self, sender):
        event = NSApp.currentEvent()
        if event is not None and event.type() == NSRightMouseUp:
            if self.popover:
                self.popover.performClose_(sender)
            self.settings.refresh()
            self.status_item.popUpStatusItemMenu_(self.menu)
            return
        self._toggle_keyboard()

    @objc.python_method
    def _hotkey_pressed(self):
        editor = self.settings.shortcut_window
        if editor and editor.panel.isVisible():
            if editor.recorder.recording:
                editor.cancel_recording()
                editor.set_feedback("Diese Kombination ist bereits dein aktives Tastenkürzel.")
                return
            editor.panel.close()
        self._toggle_keyboard()

    @objc.python_method
    def _toggle_keyboard(self):
        if self.popover and self.popover.isShown():
            self.popover.performClose_(None)
            return
        if self.popover is None:
            self._create_popover()
        self._resize_popover()
        NSApp.activateIgnoringOtherApps_(True)
        button = self.status_item.button()
        self.popover.showRelativeToRect_ofView_preferredEdge_(
            button.bounds(), button, NSRectEdgeMinY
        )

    def popoverDidShow_(self, notification):
        window = self.popover.contentViewController().view().window()
        if window is not None:
            self.last_screen = window.screen()
            window.makeKeyWindow()

    def popoverDidClose_(self, notification):
        if not self.settings.has_auxiliary_window():
            NSApp.hide_(None)

    def applicationWillTerminate_(self, notification):
        self.settings.close()

    def quit_(self, sender):
        NSApp.terminate_(sender)


def main():
    """Retain the delegate and an OS-released lock for the entire event loop."""
    cache = Path.home() / "Library" / "Caches" / BUNDLE_ID
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / "instance.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        delegate = AppDelegate.alloc().init()
        app.setDelegate_(delegate)
        app.run()
