# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1304, 671)
        self.mainWidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainWidget.sizePolicy().hasHeightForWidth())
        self.mainWidget.setSizePolicy(sizePolicy)
        self.mainWidget.setAutoFillBackground(True)
        self.mainWidget.setObjectName("mainWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.mainWidget)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainCanvas = OGLCanvas(self.mainWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainCanvas.sizePolicy().hasHeightForWidth())
        self.mainCanvas.setSizePolicy(sizePolicy)
        self.mainCanvas.setMinimumSize(QtCore.QSize(0, 0))
        self.mainCanvas.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.mainCanvas.setMouseTracking(True)
        self.mainCanvas.setObjectName("mainCanvas")
        self.horizontalLayout.addWidget(self.mainCanvas)
        self.flatStem = FlatStem(self.mainWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.flatStem.sizePolicy().hasHeightForWidth())
        self.flatStem.setSizePolicy(sizePolicy)
        self.flatStem.setAutoFillBackground(True)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.flatStem.setBackgroundBrush(brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.NoBrush)
        self.flatStem.setForegroundBrush(brush)
        self.flatStem.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.flatStem.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.flatStem.setObjectName("flatStem")
        self.horizontalLayout.addWidget(self.flatStem)
        self.zoom = QtWidgets.QSlider(self.mainWidget)
        self.zoom.setMinimum(-10)
        self.zoom.setMaximum(89)
        self.zoom.setProperty("value", 10)
        self.zoom.setOrientation(QtCore.Qt.Vertical)
        self.zoom.setObjectName("zoom")
        self.horizontalLayout.addWidget(self.zoom)
        self.optionsContainer = QtWidgets.QVBoxLayout()
        self.optionsContainer.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.optionsContainer.setContentsMargins(11, 11, 11, 11)
        self.optionsContainer.setSpacing(6)
        self.optionsContainer.setObjectName("optionsContainer")
        self.mode_movement = QtWidgets.QRadioButton(self.mainWidget)
        self.mode_movement.setChecked(True)
        self.mode_movement.setObjectName("mode_movement")
        self.optionsContainer.addWidget(self.mode_movement)
        self.mode_selection = QtWidgets.QRadioButton(self.mainWidget)
        self.mode_selection.setObjectName("mode_selection")
        self.optionsContainer.addWidget(self.mode_selection)
        self.pushButton_2 = QtWidgets.QPushButton(self.mainWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.optionsContainer.addWidget(self.pushButton_2)
        self.widget = Segment(self.mainWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.optionsContainer.addWidget(self.widget)
        self.redrawButton = QtWidgets.QPushButton(self.mainWidget)
        self.redrawButton.setObjectName("redrawButton")
        self.optionsContainer.addWidget(self.redrawButton)
        self.horizontalLayout.addLayout(self.optionsContainer)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.mainWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1304, 19))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        self.mode_movement.toggled['bool'].connect(self.mainCanvas.allowMovement)
        self.mode_selection.toggled['bool'].connect(self.mainCanvas.allowSelection)
        self.zoom.valueChanged['int'].connect(self.mainCanvas.setZoom)
        self.zoom.valueChanged['int'].connect(self.flatStem.setZoom)
        self.mode_selection.toggled['bool'].connect(self.flatStem.allowSelection)
        self.mode_movement.toggled['bool'].connect(self.flatStem.allowMovement)
        self.redrawButton.pressed.connect(self.flatStem.redraw)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Magnolia"))
        self.mode_movement.setText(_translate("MainWindow", "Ruch"))
        self.mode_selection.setText(_translate("MainWindow", "Wybieranie"))
        self.pushButton_2.setText(_translate("MainWindow", "PushButton"))
        self.redrawButton.setText(_translate("MainWindow", "redraw"))

from magnolia.ui.canvas import OGLCanvas
from magnolia.ui.flat import FlatStem
from magnolia.ui.widgets import Segment
