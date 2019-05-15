# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mobile_robot.ui'
#
# Created: Sun Apr  7 12:56:56 2019
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(386, 305)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.main_pro_addr = QtGui.QLineEdit(Dialog)
        self.main_pro_addr.setObjectName(_fromUtf8("main_pro_addr"))
        self.gridLayout.addWidget(self.main_pro_addr, 0, 1, 1, 2)
        self.BCI2000_addr = QtGui.QLineEdit(Dialog)
        self.BCI2000_addr.setObjectName(_fromUtf8("BCI2000_addr"))
        self.gridLayout.addWidget(self.BCI2000_addr, 1, 1, 1, 2)
        self.bt_auto_model = QtGui.QPushButton(Dialog)
        self.bt_auto_model.setObjectName(_fromUtf8("bt_auto_model"))
        self.gridLayout.addWidget(self.bt_auto_model, 2, 0, 1, 2)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.bt_cmd_model = QtGui.QPushButton(Dialog)
        self.bt_cmd_model.setObjectName(_fromUtf8("bt_cmd_model"))
        self.gridLayout.addWidget(self.bt_cmd_model, 2, 2, 1, 1)
        self.bt_new_trial = QtGui.QPushButton(Dialog)
        self.bt_new_trial.setObjectName(_fromUtf8("bt_new_trial"))
        self.gridLayout.addWidget(self.bt_new_trial, 3, 0, 1, 2)
        self.bt_estop = QtGui.QPushButton(Dialog)
        self.bt_estop.setObjectName(_fromUtf8("bt_estop"))
        self.gridLayout.addWidget(self.bt_estop, 3, 2, 1, 1)
        self.bt_cease_current_task = QtGui.QPushButton(Dialog)
        self.bt_cease_current_task.setObjectName(_fromUtf8("bt_cease_current_task"))
        self.gridLayout.addWidget(self.bt_cease_current_task, 4, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "MainPro", None))
        self.main_pro_addr.setText(_translate("Dialog", "127.0.0.1-9098", None))
        self.BCI2000_addr.setText(_translate("Dialog", "127.0.0.1-9099", None))
        self.bt_auto_model.setText(_translate("Dialog", "自动模式", None))
        self.label_2.setText(_translate("Dialog", "BCI2000", None))
        self.bt_cmd_model.setText(_translate("Dialog", "命令模式", None))
        self.bt_new_trial.setText(_translate("Dialog", "新一轮控制", None))
        self.bt_estop.setText(_translate("Dialog", "轮椅急停", None))
        self.bt_cease_current_task.setText(_translate("Dialog", "中断当前任务", None))

