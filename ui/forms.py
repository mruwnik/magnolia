# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(723, 466)
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
        self.mainCanvas.setObjectName("mainCanvas")
        self.horizontalLayout.addWidget(self.mainCanvas)
        self.optionsContainer = QtWidgets.QVBoxLayout()
        self.optionsContainer.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.optionsContainer.setContentsMargins(11, 11, 11, 11)
        self.optionsContainer.setSpacing(6)
        self.optionsContainer.setObjectName("optionsContainer")
        self.pushButton_2 = QtWidgets.QPushButton(self.mainWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.optionsContainer.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(self.mainWidget)
        self.pushButton.setObjectName("pushButton")
        self.optionsContainer.addWidget(self.pushButton)
        self.horizontalLayout.addLayout(self.optionsContainer)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.mainWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 723, 22))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Magnolia"))
        self.pushButton_2.setText(_translate("MainWindow", "PushButton"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))

from ui.canvas import OGLCanvas
