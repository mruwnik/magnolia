from qtpy.QtCore import QObject, Signal


class DisplaySignals(QObject):
    """All signals that should be received by all meristem displays."""

    drawable_selected = Signal(QObject, name="drawableSelected")
    """A given drawable was selected."""

    view_rotated = Signal(float, float, name="viewRotated")
    """The view was rotated by the given angles (side, tilt)."""

    refresh_needed = Signal(name="refreshNeeded")
    """The display should be redrawn."""


signaler = DisplaySignals()
"""A singleton handler of all display signals."""
