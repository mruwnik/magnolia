from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

from ui import Ui_MainWindow
from meristem import Meristem, Bud


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
        angle = i * 90.0/size
        # the offset is scaled so that the layers "fit in" to each other
        layer_height = height + i * scale
        buds += make_ring(start_angle=angle, height=layer_height, items=size, colour=colour)
    return buds


class Prog(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        meristem = Meristem()

        big_buds = make_buds(10, 7, (0.7, 0.0, 0.0))
        small_buds = make_buds(10, 30, (0.0, 0.7, 0.0), height=4.6)
        medium_buds = make_buds(10, 15, (0.0, 0.0, 0.7), height=5.7)

        buds = big_buds + small_buds + medium_buds
        meristem.add(*buds)

        self.ui.mainCanvas.add(meristem)

        timer = QTimer(self)
        timer.timeout.connect(self.ui.mainCanvas.update)
        timer.start(20)


def main():
    import sys
    Program = QApplication(sys.argv)
    MyProg = Prog()
    MyProg.show()
    Program.exec_()


if __name__ == '__main__':
    main()
