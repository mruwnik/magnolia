import array

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication, QMainWindow

from ui import Ui_MainWindow
from meristem import Meristem, Bud
from graph import get_reachable


def make_ring(start_angle, height, items, colour):
    """Make a ring of buds.

    :param float start_angle: how much the ring should be rotated clockwise
    :param float height: how high up the meristem the ring should be
    :param int items: how many items to add to the ring
    :param list colour: the colour of the buds
    """
    # calculate the angle between each consecutive bud
    angle_step = 360.0/items

    # always use the same radius for all rings - this makes a nice column
    base_radius = 3.0
    return [
        Bud(
            radius=base_radius,
            height=height,
            angle=start_angle + i*angle_step,  # move around the circle by angle_step degrees
            fill_colour=colour,
            scale=(base_radius + 1) / items  # scale the bud so that the more there are, the smaller they are
        ) for i in range(items)
    ]


def make_buds(layers, size, colour, height=0):
    """Make a couple of layers of buds.

    :param int layers: how many layers should be added
    :param int size: how many buds per layer.
    :param list colour: the colour of the created buds
    :param float height: the initial height of the layer
    """
    buds = []
    scale = 3 / size
    for i in range(layers):
        # step around by this many degrees
        angle = i * 120.0/size
        # the offset is scaled so that the layers "fit in" to each other
        layer_height = height + i * scale * 1.4
        buds += make_ring(start_angle=angle, height=layer_height, items=size, colour=colour)
    return buds


class Prog(QMainWindow):
    def __init__(self):
        """Initialise the whole program."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Make a dummy meristem with random buds in different colours
        self.meristem = Meristem()
        buds = make_buds(20, 15, (0.0, 0.0, 0.7), height=1)
        self.meristem.add(*buds)

        # set the OpenGL canvas up with the meristem
        self.ui.mainCanvas.add(self.meristem)
        self.ui.mainCanvas.drawable_selected.connect(self.bud_selected)

        # Set a timer to refresh the OpenGL screen every 20ms (50fps)
        timer = QTimer(self)
        timer.timeout.connect(self.ui.mainCanvas.update)
        timer.start(20)

    def bud_selected(self, bud):
        """Handle a bud being selected. It displays the selected bud's neighbours."""
        if not bud:
            return

        # Reset all colours
        for b in self.meristem.objects:
            b.colours = b.BLUE
            b.needsRefresh.emit('colours')

        # Loop through all reachable buds, colouring them relative to their distance
        for b in get_reachable(bud, self.meristem.closest(bud)):
            d = bud.distance(b)
            b.colours = (d/bud.radius, 1, 1 - d/bud.radius)

        bud.colours = bud.GREEN
        self.meristem.refresh_field('colours')


def main():
    import sys
    Program = QApplication(sys.argv)
    MyProg = Prog()
    MyProg.show()
    Program.exec_()


if __name__ == '__main__':
    main()
