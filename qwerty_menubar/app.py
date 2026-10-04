"""Native AppKit menu-bar UI. No timers, keyboard hooks, or network activity."""

import fcntl
from pathlib import Path

import objc
from AppKit import (
    NSApp,
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSImage,
    NSImageAlignCenter,
    NSImageScaleProportionallyUpOrDown,
    NSImageView,
    NSMakeRect,
    NSMakeSize,
    NSMenu,
    NSMenuItem,
    NSObject,
    NSPopover,
    NSPopoverBehaviorTransient,
    NSRectEdgeMinY,
    NSRightMouseUp,
    NSScreen,
    NSStatusBar,
    NSVariableStatusItemLength,
    NSView,
    NSViewController,
)
from Foundation import NSBundle

from qwerty_menubar.layout import PADDING, asset_path, popover_size

BUNDLE_ID = "dev.zimfelix.qwerty-menubar"
APP_NAME = "QWERTY Menu Bar"


class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        if hasattr(self, "status_item"):
            return
        self.popover = None
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
        button.setToolTip_("QWERTY-Tastatur · Klick zum Anzeigen · Rechtsklick zum Beenden")
        button.setAccessibilityLabel_("QWERTY-Tastatur")
        button.setTarget_(self)
        button.setAction_("toggleKeyboard:")
        button.sendActionOn_((1 << 2) | (1 << 4))  # left/right mouse-up, not global hooks

    @objc.python_method
    def _create_menu(self):
        self.menu = NSMenu.alloc().initWithTitle_(APP_NAME)
        title = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(APP_NAME, None, "")
        title.setEnabled_(False)
        self.menu.addItem_(title)
        self.menu.addItem_(NSMenuItem.separatorItem())
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Beenden", "quit:", "q")
        quit_item.setTarget_(self)
        self.menu.addItem_(quit_item)

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
        self.popover.setContentViewController_(controller)

    @objc.python_method
    def _resize_popover(self):
        screen = self.status_item.button().window().screen() or NSScreen.mainScreen()
        width, height = popover_size(screen.visibleFrame().size.width)
        self.popover.setContentSize_(NSMakeSize(width, height))
        self.image_view.setFrame_(
            NSMakeRect(PADDING, PADDING, width - 2 * PADDING, height - 2 * PADDING)
        )

    def toggleKeyboard_(self, sender):
        event = NSApp.currentEvent()
        if event is not None and event.type() == NSRightMouseUp:
            if self.popover:
                self.popover.performClose_(sender)
            self.status_item.popUpStatusItemMenu_(self.menu)
            return
        if self.popover and self.popover.isShown():
            self.popover.performClose_(sender)
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
            window.makeKeyWindow()

    def popoverDidClose_(self, notification):
        # Returning focus avoids stealing keyboard input after the reference closes.
        NSApp.hide_(None)

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
