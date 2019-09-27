# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'caDlg.ui'
#
# Created: Thu Sep 12 17:21:56 2019
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(814, 733)
        Dialog.setStyleSheet("background-color: rgb(226, 246, 255);")
        self.cbSerialItems = QtWidgets.QComboBox(Dialog)
        self.cbSerialItems.setGeometry(QtCore.QRect(390, 100, 311, 51))
        self.cbSerialItems.setObjectName("cbSerialItems")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(60, 110, 161, 24))
        self.label.setObjectName("label")
        self.btnZeroCal = QtWidgets.QPushButton(Dialog)
        self.btnZeroCal.setGeometry(QtCore.QRect(70, 390, 150, 46))
        self.btnZeroCal.setObjectName("btnZeroCal")
        self.btnOpenCA = QtWidgets.QPushButton(Dialog)
        self.btnOpenCA.setGeometry(QtCore.QRect(70, 240, 150, 46))
        self.btnOpenCA.setObjectName("btnOpenCA")
        self.btnReadValue = QtWidgets.QPushButton(Dialog)
        self.btnReadValue.setGeometry(QtCore.QRect(70, 510, 150, 46))
        self.btnReadValue.setObjectName("btnReadValue")
        self.btnCloseCA = QtWidgets.QPushButton(Dialog)
        self.btnCloseCA.setGeometry(QtCore.QRect(410, 230, 150, 46))
        self.btnCloseCA.setObjectName("btnCloseCA")
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(280, 490, 491, 185))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblReadCIE1931_x = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lblReadCIE1931_x.setFont(font)
        self.lblReadCIE1931_x.setObjectName("lblReadCIE1931_x")
        self.verticalLayout.addWidget(self.lblReadCIE1931_x)
        self.lblReadCIE1931_y = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lblReadCIE1931_y.setFont(font)
        self.lblReadCIE1931_y.setObjectName("lblReadCIE1931_y")
        self.verticalLayout.addWidget(self.lblReadCIE1931_y)
        self.lblReadCIE1931_lv = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lblReadCIE1931_lv.setFont(font)
        self.lblReadCIE1931_lv.setObjectName("lblReadCIE1931_lv")
        self.verticalLayout.addWidget(self.lblReadCIE1931_lv)

        self.retranslateUi(Dialog)
        self.btnOpenCA.clicked['bool'].connect(Dialog.btn_open_ca_click)
        self.btnCloseCA.clicked['bool'].connect(Dialog.btn_close_ca_click)
        self.btnZeroCal.clicked['bool'].connect(Dialog.btn_zerocalc_click)
        self.btnReadValue.clicked['bool'].connect(Dialog.btn_read_xylv_click)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.cbSerialItems, self.btnOpenCA)
        Dialog.setTabOrder(self.btnOpenCA, self.btnCloseCA)
        Dialog.setTabOrder(self.btnCloseCA, self.btnZeroCal)
        Dialog.setTabOrder(self.btnZeroCal, self.btnReadValue)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "CA310"))
        self.label.setText(_translate("Dialog", "Serial Port:"))
        self.btnZeroCal.setText(_translate("Dialog", "Zero Calc"))
        self.btnOpenCA.setText(_translate("Dialog", "Open CA410"))
        self.btnReadValue.setText(_translate("Dialog", "READ x,y,lv"))
        self.btnCloseCA.setText(_translate("Dialog", "Close CA"))
        self.lblReadCIE1931_x.setText(_translate("Dialog", "TextLabel"))
        self.lblReadCIE1931_y.setText(_translate("Dialog", "TextLabel"))
        self.lblReadCIE1931_lv.setText(_translate("Dialog", "TextLabel"))

