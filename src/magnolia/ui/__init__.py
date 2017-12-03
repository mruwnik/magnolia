from collections import OrderedDict

from magnolia.ui.forms import Ui_MainWindow
from magnolia.ui.canvas import OGLCanvas
from magnolia.ui.objloader import MeshData, OBJReader
from magnolia.ui.drawables import Drawable, MeshDrawable, MultiDrawable
from magnolia.ui.flat import FlatStem
from magnolia.ui.signals import signaler
from magnolia.ui.widgets import RingSegment, DecreasingRingSegment


positioners = OrderedDict((
    (RingSegment.name, RingSegment),
    (DecreasingRingSegment.name, DecreasingRingSegment),
))

__all__ = [
    Drawable, MeshDrawable, MultiDrawable, FlatStem,
    Ui_MainWindow, OGLCanvas, MeshData, OBJReader,
    signaler, positioners
]
