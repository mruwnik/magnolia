from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget

from ui import Ui_MainWindow
from meristem import Meristem


class Prog(QMainWindow):
    def __init__(self):
        super().__init__();
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        meristem = Meristem()
        self.ui.mainCanvas.add(meristem)

        timer = QTimer(self)
        timer.timeout.connect(self.ui.mainCanvas.update)
        timer.start(20)

def main():
    import sys
    Program = QApplication(sys.argv);
    MyProg=Prog();
    MyProg.show();
    Program.exec_();

if __name__=='__main__':
    main();
