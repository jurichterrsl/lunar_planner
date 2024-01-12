# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MyPlugin.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(906, 708)
        self.plot = QtWidgets.QWidget(Form)
        self.plot.setGeometry(QtCore.QRect(10, 10, 881, 571))
        self.plot.setObjectName("plot")
        self.calculate_button = QtWidgets.QPushButton(Form)
        self.calculate_button.setGeometry(QtCore.QRect(610, 590, 281, 81))
        self.calculate_button.setObjectName("calculate_button")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.calculate_button.setText(_translate("Form", "Calculate Graph"))
