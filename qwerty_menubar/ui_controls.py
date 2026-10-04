"""Neutral icon button: generous hit area, no system-accent selection fill."""

import objc
from AppKit import (
    NSBezierPath,
    NSButton,
    NSButtonTypeMomentaryChange,
    NSColor,
    NSFocusRingTypeNone,
    NSImageOnly,
    NSImageScaleNone,
    NSNoCellMask,
    NSTrackingActiveAlways,
    NSTrackingArea,
    NSTrackingInVisibleRect,
    NSTrackingMouseEnteredAndExited,
)


class SettingsButton(NSButton):
    @objc.python_method
    def configure(self):
        self.hovered = False
        self.setButtonType_(NSButtonTypeMomentaryChange)
        self.setTitle_("")
        self.setImagePosition_(NSImageOnly)
        self.setBordered_(False)
        self.setFocusRingType_(NSFocusRingTypeNone)
        self.setImageScaling_(NSImageScaleNone)
        self.cell().setHighlightsBy_(NSNoCellMask)
        self.cell().setShowsStateBy_(NSNoCellMask)
        return self

    def updateTrackingAreas(self):
        if getattr(self, "hover_area", None):
            self.removeTrackingArea_(self.hover_area)
        self.hover_area = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
            self.bounds(),
            NSTrackingMouseEnteredAndExited | NSTrackingActiveAlways | NSTrackingInVisibleRect,
            self,
            None,
        )
        self.addTrackingArea_(self.hover_area)
        objc.super(SettingsButton, self).updateTrackingAreas()

    def mouseEntered_(self, event):
        self.hovered = True
        self.setNeedsDisplay_(True)

    def mouseExited_(self, event):
        self.hovered = False
        self.setNeedsDisplay_(True)

    def drawRect_(self, rect):
        pressed = self.cell().isHighlighted()
        if pressed or getattr(self, "hovered", False):
            NSColor.labelColor().colorWithAlphaComponent_(0.12 if pressed else 0.07).setFill()
            NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(self.bounds(), 8, 8).fill()
        if self.window() and self.window().firstResponder() == self:
            NSColor.secondaryLabelColor().colorWithAlphaComponent_(0.5).setStroke()
            outline = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(self.bounds(), 8, 8)
            outline.setLineWidth_(1)
            outline.stroke()
        objc.super(SettingsButton, self).drawRect_(rect)
