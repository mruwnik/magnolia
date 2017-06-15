import math

import qtpy.QtGui
from qtpy.QtGui import QPen, QBrush
from qtpy.QtCore import Qt, QPoint
from qtpy.QtWidgets import QGraphicsView, QGraphicsScene
from ui.drawables import MeristemActions


class FlatStem(MeristemActions, QGraphicsView):

    def __init__(self, *args, **kwargs):
        self.scene = QGraphicsScene()
        super(FlatStem, self).__init__(self.scene, *args, **kwargs)

    def thin_line(self, colour=None):
        pen = QPen(colour) if colour else QPen()
        pen.setWidth(0)
        return pen

    def make_item(self, bud):
        """Add the given bud to the scene."""
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

    def redraw(self):
        """Redraw all objects on the scene."""
        for item in self.scene.items():
            self.scene.removeItem(item)

        # Draw all buds
        for obj in self.objects.objects:
            for bud in obj.objects:
                self.make_item(bud)

        # Draw the bounding lines of the meristem
        side_bar = self.thin_line(Qt.blue)
        for meristem in self.objects.objects:
            side_bar_pos = math.pi * meristem.radius
            self.scene.addLine(-side_bar_pos, 1, -side_bar_pos, -meristem.height - 2, side_bar)
            self.scene.addLine(side_bar_pos, 1, side_bar_pos, -meristem.height - 2, side_bar)

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
        self.drawable_selected.emit(self.objects.selected)
