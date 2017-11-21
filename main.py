import math

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication, QMainWindow

from magnolia.ui import Ui_MainWindow, signaler
from magnolia.positioners import RingPositioner


class Prog(QMainWindow):
    def __init__(self):
        """Initialise the whole program."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connect_views()

        self.ui.pushButton_2.pressed.connect(self.add_ring)

        # Make a dummy meristem with random buds in different colours
        self.meristem = RingPositioner(math.radians(60), 3)
        buds = [self.meristem.new() for _ in range(240)]
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
