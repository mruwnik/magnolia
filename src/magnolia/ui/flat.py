import math

import qtpy.QtGui
from qtpy.QtGui import QPen, QBrush
from qtpy.QtCore import Qt, QPoint
from qtpy.QtWidgets import QGraphicsView, QGraphicsScene
from magnolia.ui.drawables import MeristemDisplay


class FlatStem(MeristemDisplay, QGraphicsView):
    """A QTGraphics canvas to display a 2D (rolled out) view of a meristem."""

    def __init__(self, *args, **kwargs):
        self.scene = QGraphicsScene()
        super(FlatStem, self).__init__(self.scene, *args, **kwargs)

    def thin_line(self, colour=None):
        """Return a pen that draws a thin line in the given colour."""
        pen = QPen(colour) if colour else QPen()
        pen.setWidth(0)
        return pen

    def shadow_if_needed(self, bud):
        """Check if the bud crosses over the side bars, and if so draw a shadow bud on the opposite side."""
        angle = bud.angle2x(bud.angle + math.radians(self.viewing_angle[0]))
        if abs(angle) < math.pi * bud.radius - bud.scale:
            return

        if angle > 0:
            angle = angle - bud.scale - 2 * math.pi * bud.radius
        else:
            angle = angle - bud.scale + 2 * math.pi * bud.radius

        return self.scene.addEllipse(
            angle, -bud.height - bud.scale,
            bud.scale * 2, bud.scale * 2,
            self.thin_line(), QBrush(qtpy.QtGui.QColor(*(bud.html_colour + [100])))
        )

    def make_item(self, bud):
        """Add the given bud to the scene as a ball."""
        item = self.scene.addEllipse(
            bud.angle2x(bud.angle + math.radians(self.viewing_angle[0])) - bud.scale, -bud.height - bud.scale,
            bud.scale * 2, bud.scale * 2,
            self.thin_line(), QBrush(qtpy.QtGui.QColor(*bud.html_colour))
        )
        return item

    def set_scale(self):
        """Scale the view in accordance with the zoom level."""
        self.resetTransform()
        size = self.size()
        dist = math.sqrt(size.width() * size.height())/50.0
        zoom = math.pi * 300/(dist + self.zoom + 11)
        self.scale(zoom, zoom)

    def draw_side_bars(self):
        """Draw the bounding lines of the meristem."""
        if not self.displayables:
            return

        side_bar = self.thin_line(Qt.blue)
        top = max([b.radius for b in self.displayables if b.height < b.scale] or [0])
        for height in range(int(round(self.objects.height))):
            bottom = top
            top = max([b.radius for b in self.displayables if abs(b.height - height) < b.scale] or [0])

            bot_side_bar_pos = math.pi * bottom
            top_side_bar_pos = math.pi * top
            self.scene.addLine(-bot_side_bar_pos, -height + 0.5, -top_side_bar_pos, -height - 0.5, side_bar)
            self.scene.addLine(bot_side_bar_pos, -height + 0.5, top_side_bar_pos, -height - 0.5, side_bar)

    def redraw(self):
        """Redraw all objects on the scene."""
        for item in self.scene.items():
            self.scene.removeItem(item)

        # Draw all buds
        for bud in self.displayables:
            self.make_item(bud)
            self.shadow_if_needed(bud)

        self.draw_side_bars()

        self.set_scale()

    def select(self, event):
        """Select the item that is under the cursor (if enabled)."""
        if not self.can_select:
            return

        scene_pos = self.mapToScene(QPoint(event.x(), event.y()))
        x, y = scene_pos.x(), -scene_pos.y()
        offsets = (math.radians(self.viewing_angle[0]), 0)
        if self.objects.bounds_test(x, y, offsets) > 0:
            self.objects.select()

        # signal all and any slots that something new was selected
        self._signal_selected()
