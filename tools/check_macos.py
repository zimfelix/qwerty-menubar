"""Opt-in native UI/resource check on a logged-in Mac. Briefly displays a popover."""

import argparse
import json
import os
import resource
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import objc
from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSBackingStoreBuffered,
    NSMakeRect,
    NSRectEdgeMinY,
    NSScreen,
    NSStatusBar,
    NSWindow,
    NSWindowStyleMaskBorderless,
)
from Foundation import NSDate, NSRunLoop

from qwerty_menubar.app import AppDelegate
from qwerty_menubar.preferences import Preferences


def pump(seconds):
    NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(seconds))


def rss_mib():
    output = subprocess.check_output(["ps", "-o", "rss=", "-p", str(os.getpid())], text=True)
    return int(output.strip()) / 1024


def cpu_seconds():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def create_delegate(display_id):
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    with tempfile.TemporaryDirectory(prefix="qwerty-popover-check-") as directory:
        preferences = Preferences(Path(directory) / "settings.json")
        preferences.save_shortcut(None)  # do not register a real/default user hotkey
        with patch("qwerty_menubar.settings.Preferences", return_value=preferences):
            app.finishLaunching()
            delegate.applicationDidFinishLaunching_(None)
    pump(0.5)  # let AppKit attach the status-item scene
    screen = next(
        s for s in NSScreen.screens() if s.deviceDescription()["NSScreenNumber"] == display_id
    )
    frame = screen.frame()
    anchor = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(
            frame.origin.x + frame.size.width - 400, frame.origin.y + frame.size.height - 30, 22, 16
        ),
        NSWindowStyleMaskBorderless,
        NSBackingStoreBuffered,
        False,
    )
    anchor.setReleasedWhenClosed_(False)
    anchor.setAlphaValue_(0)
    anchor.orderFrontRegardless()
    return app, delegate, anchor


def exercise_popover(delegate, anchor, cycles):
    delegate._create_popover()
    delegate._resize_popover()
    delegate.popover.setDelegate_(None)  # measure content lifecycle, not focus restoration

    def show():
        view = anchor.contentView()
        delegate.popover.showRelativeToRect_ofView_preferredEdge_(
            view.bounds(), view, NSRectEdgeMinY
        )

    show()
    pump(0.4)
    assert delegate.popover.isShown(), "Reference did not open"
    assert delegate.image_view.image() is not None, "Reference image missing"
    assert delegate.image_view.window() is not None, "Popover window missing"
    image = delegate.image_view.image()
    delegate.popover.setAnimates_(False)  # do not animate hundreds of times
    delegate.popover.close()
    pump(0.1)
    assert not delegate.popover.isShown(), "Reference did not close"
    baseline = rss_mib()
    for _ in range(cycles):
        with objc.autorelease_pool():
            show()
            pump(0.01)
            assert delegate.popover.isShown()
            delegate.popover.close()
            pump(0.01)
    assert delegate.image_view.image() is image, "Reopening reloads the image"
    return baseline, rss_mib()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--display-id",
        type=int,
        required=True,
        help="Explicit display ID; avoids interrupting the current monitor",
    )
    parser.add_argument("--cycles", type=int, default=100)
    parser.add_argument("--idle-seconds", type=float, default=10)
    args = parser.parse_args()
    app, delegate, anchor = create_delegate(args.display_id)
    try:
        baseline, after = exercise_popover(delegate, anchor, args.cycles)
        before_cpu, before_time = cpu_seconds(), time.monotonic()
        pump(args.idle_seconds)
        idle_cpu = 100 * (cpu_seconds() - before_cpu) / (time.monotonic() - before_time)
        report = {
            "cycles": args.cycles,
            "rss_baseline_mib": round(baseline, 2),
            "rss_after_cycles_mib": round(after, 2),
            "growth_mib": round(after - baseline, 2),
            "idle_cpu_percent": round(idle_cpu, 3),
        }
        print(json.dumps(report, indent=2))
        assert after < 160, "RSS exceeds the 160 MiB regression budget"
        assert after - baseline < 12, "Possible repeated-open memory growth"
        assert idle_cpu < 1, "Unexpected sustained idle CPU activity"
    finally:
        if delegate.popover:
            delegate.popover.close()
        delegate.settings.close()
        NSStatusBar.systemStatusBar().removeStatusItem_(delegate.status_item)
        anchor.close()
        app.setDelegate_(None)


if __name__ == "__main__":
    main()
