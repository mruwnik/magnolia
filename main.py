from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication, QMainWindow

from magnolia.ui import Ui_MainWindow, signaler, positioners
from magnolia.positioners import RingPositioner
from magnolia.graph import BudGraph


class Prog(QMainWindow):
    def __init__(self):
        """Initialise the whole program."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.positioners.addItems(positioners.keys())
        self.used_positioners = []

        self.connect_views()
        # Make a dummy meristem with random buds in different colours
        self.meristem = BudGraph()

        # set the OpenGL canvas up with the meristem
        self.ui.mainCanvas.objects = self.meristem

        self.ui.flatStem.objects = self.meristem
        self.ui.flatStem.show()
        # Set a timer to refresh the OpenGL screen every 20ms (50fps)
        timer = QTimer(self)
        timer.timeout.connect(self.ui.mainCanvas.update)
        timer.start(20)

    def add_positioner(self):
        pos_name = self.ui.positioners.currentText()
        positioner_classes = {
            'Ring positioner': RingPositioner
        }
        segment = positioners[pos_name](
            positioner_classes[pos_name],
            self.ui.mainWidget
        )
        self.used_positioners.append(segment)

        segment.setObjectName(pos_name)
        self.ui.positioner_settings_container.addWidget(segment)

        def remove_segment(*args):
            self.ui.positioner_settings_container.removeWidget(segment)
            self.used_positioners.remove(segment)
            segment.setParent(None)

        segment.delete_button.pressed.connect(remove_segment)

    def redraw(self):
        buds = self.meristem.next_or_new()
        i, angle, height, radius, scale = 0, 0, 0, 0, 0

        for pos_setter in self.used_positioners:
            positioner = pos_setter.positioner(angle, height + scale)
            for angle, height, radius, scale in positioner.n_positions(pos_setter.to_add):
                next(buds).update_pos(angle, height, radius, scale)
                i += 1

        self.meristem.truncate(i)
        signaler.refresh_needed.emit()

    def connect_views(self):
        signaler.drawable_selected.connect(self.bud_selected)
        self.ui.add_segment.pressed.connect(self.add_positioner)
        self.ui.redrawButton.pressed.connect(self.redraw)

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
