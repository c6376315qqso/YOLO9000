# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1065, 762)
        Dialog.setWindowIcon(QtGui.QIcon('icon.jpg'))
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.disPicture = QtWidgets.QLabel(Dialog)
        self.disPicture.setText("")
        self.disPicture.setObjectName("disPicture")
        self.gridLayout.addWidget(self.disPicture, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.openButton = QtWidgets.QPushButton(Dialog)
        self.openButton.setObjectName("openButton")
        self.horizontalLayout.addWidget(self.openButton)
        self.detect9000Button = QtWidgets.QPushButton(Dialog)
        self.detect9000Button.setObjectName("detect9000Button")
        self.horizontalLayout.addWidget(self.detect9000Button)
        self.detectv2Button = QtWidgets.QPushButton(Dialog)
        self.detectv2Button.setObjectName("detectv2Button")
        self.horizontalLayout.addWidget(self.detectv2Button)
        self.saveButton = QtWidgets.QPushButton(Dialog)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.clearButton = QtWidgets.QPushButton(Dialog)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout.addWidget(self.clearButton)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.gridLayout.setRowStretch(0, 100)
        self.gridLayout.setRowStretch(1, 1)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "YOLO检测系统"))
        self.openButton.setText(_translate("Dialog", "打开图像"))
        self.detect9000Button.setText(_translate("Dialog", "YOLO9000检测"))
        self.detectv2Button.setText(_translate("Dialog", "YOLOv2检测"))
        self.saveButton.setText(_translate("Dialog", "保存"))
        self.clearButton.setText(_translate("Dialog", "清空"))
