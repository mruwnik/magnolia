from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication, QMainWindow

from magnolia.ui import Ui_MainWindow, signaler
from magnolia.meristem import Bud
from magnolia.graph import BudGraph


class Ringer:
    # always use the same radius for all rings - this makes a nice column
    BASE_RADIUS = 3.0

    def __init__(self, size, colour=(0.0, 0.0, 0.7), start_height=0):
        self.buds_per_layer = size
        self.default_colour = colour
        self.height = start_height
        self.angle = 0

    def make_ring(self, colour=None):
        """Make a ring of buds.

        :param list colour: the colour of the buds
        """
        # calculate the angle between each consecutive bud
        angle_step = 360.0/self.buds_per_layer
        # step around by this many degrees
        # the offset is scaled so that the layers "fit in" to each other
        self.angle = self.angle + 150.0/self.buds_per_layer

        scale = self.BASE_RADIUS / self.buds_per_layer
        self.height = self.height + scale * 1.5

        return [
            Bud(
                radius=self.BASE_RADIUS,
                height=self.height,
                # move around the circle by angle_step degrees
                angle=self.angle + i*angle_step,
                fill_colour=colour or self.default_colour,
                # scale the bud so that the more there are, the smaller they are
                scale=(self.BASE_RADIUS + 2) / self.buds_per_layer
            ) for i in range(self.buds_per_layer)
        ]

    def make_buds(self, layers):
        """Make a couple of layers of buds.

        :param int layers: how many layers should be added
        """
        buds = []
        for i in range(layers):
            buds += self.make_ring()
        return buds


class Prog(QMainWindow):
    def __init__(self):
        """Initialise the whole program."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connect_views()
        self.ringer = Ringer(15, (0.0, 0.0, 0.7), -1)

        self.ui.pushButton_2.pressed.connect(self.add_ring)

        # Make a dummy meristem with random buds in different colours
        self.meristem = BudGraph()
        buds = self.ringer.make_buds(20)
        self.meristem.add(*buds)

        # set the OpenGL canvas up with the meristem
        self.ui.mainCanvas.objects = self.meristem

        self.ui.flatStem.objects = self.meristem
        self.ui.flatStem.show()
        # Set a timer to refresh the OpenGL screen every 20ms (50fps)
        timer = QTimer(self)
        timer.timeout.connect(self.ui.mainCanvas.update)
        timer.start(20)

    def add_ring(self):
        buds = self.ringer.make_ring(colour=(0.7, 0, 0.1))
        self.meristem.add(*buds)
        signaler.refresh_needed.emit()

    def connect_views(self):
        signaler.drawable_selected.connect(self.bud_selected)

    def bud_selected(self, bud):
        """Handle a bud being selected. It displays the selected bud's neighbours."""
        if not bud:
            return

        # Reset all colours
        for b in self.meristem.objects:
            b.colours = b.BLUE

        # Loop through all reachable buds, colouring them relative to their distance
        for b in self.meristem.neighbours(bud):
            d = bud.distance(b)
            b.colours = (d/bud.radius, 1, 1 - d/bud.radius)

        for line in self.meristem.axes(bud):
            for b in self.meristem.on_line(line):
                b.colours = (1, 1, 0.5)

        bud.colours = bud.GREEN
        self.meristem.refresh_field('colours')
        signaler.refresh_needed.emit()


def main():
    import sys
    Program = QApplication(sys.argv)
    MyProg = Prog()
    MyProg.show()
    Program.exec_()


if __name__ == '__main__':
    main()
