from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication, QMainWindow

from magnolia.ui import Ui_MainWindow, signaler, positioners, LineDrawable
from magnolia.positioners import (
    RingPositioner, ChangingRingPositioner, LowestAvailablePositioner
)
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

    def add_positioner(self, pos_name):
        """
        Add a positioner.

        The positioner will apply to the top of the meristem. The type is taken
        from the positioners selector.

        :param str pos_name: the name pf the positioner to be used
        """
        positioner_classes = {
            'Ring positioner': RingPositioner,
            'Decreasing ring positioner': ChangingRingPositioner,
            'Lowest available space positioner': LowestAvailablePositioner,
            'Variable lowest available space positioner': LowestAvailablePositioner,
        }
        segment = positioners[pos_name](
            positioner_classes[pos_name],
            self.ui.mainWidget
        )
        self.used_positioners.append(segment)

        # add the new segment setter to the displayed list
        segment.setObjectName(pos_name)
        self.ui.positioner_settings_container.insertWidget(0, segment)

        # setup the delete button to remove the segment if desired
        def remove_segment(*args):
            self.ui.positioner_settings_container.removeWidget(segment)
            self.used_positioners.remove(segment)
            segment.setParent(None)

        segment.delete_button.pressed.connect(remove_segment)

    def redraw(self):
        """Reposition all buds according to the current settings."""
        buds = self.meristem.next_or_new()
        angle, height, radius, scale = 0, 0, 0, 0
        current_front = []

        for pos_setter in self.used_positioners:
            positioner = pos_setter.positioner(angle, height, front=current_front)
            for angle, height, radius, scale in positioner.n_positions(pos_setter.to_add):
                next(buds).update_pos(angle, height, radius, scale)
            angle, height, radius, scale = positioner._next_pos()
            current_front = positioner.current_front

        self.meristem.truncate(sum(p.to_add for p in self.used_positioners))
        signaler.refresh_needed.emit()

    def connect_views(self):
        signaler.drawable_selected.connect(self.bud_selected)
        self.ui.redrawButton.pressed.connect(self.redraw)
        self.ui.positioners.activated['QString'].connect(self.add_positioner)

    def bud_selected(self, bud):
        """Handle a bud being selected. It displays the selected bud's neighbours."""
        if not bud:
            return

        # Reset all colours
        for b in self.meristem.objects:
            b.colours = b.BLUE

        # show axes if enabled
        if self.ui.show_bud_axes.isChecked():
            for line in self.meristem.axis_checkers(bud):
                for b in self.meristem.on_line(line):
                    b.colours = (1, 1, 0.5)

        # colour buds on axes, if enabled
        if self.ui.show_axes.isChecked():
            lines = [
                LineDrawable(helix(self.meristem.height), bud.RED)
                for helix in self.meristem.axes(bud)
            ]
        else:
            lines = []
        self.ui.mainCanvas._lines = self.ui.flatStem._lines = lines

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
