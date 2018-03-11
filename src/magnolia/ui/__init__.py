from collections import OrderedDict

from magnolia.ui.forms import Ui_MainWindow
from magnolia.ui.canvas import OGLCanvas
from magnolia.ui.objloader import MeshData, OBJReader
from magnolia.ui.drawables import Drawable, MeshDrawable, MultiDrawable, LineDrawable
from magnolia.ui.flat import FlatStem
from magnolia.ui.signals import signaler
from magnolia.ui.widgets import (
    RingSegment, DecreasingRingSegment, LowestAvailableSegment, VariableLowestAvailableSegment
)


positioners = OrderedDict((
    (RingSegment.name, RingSegment),
    (DecreasingRingSegment.name, DecreasingRingSegment),
    (LowestAvailableSegment.name, LowestAvailableSegment),
    (VariableLowestAvailableSegment.name, VariableLowestAvailableSegment),
))

__all__ = [
    Drawable, LineDrawable, MeshDrawable, MultiDrawable, FlatStem,
    Ui_MainWindow, OGLCanvas, MeshData, OBJReader,
    signaler, positioners,
]
