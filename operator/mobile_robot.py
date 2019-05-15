# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mobile_robot.ui'
#
# Created: Fri Apr 26 15:19:49 2019
#      by: PyQt4 UI code generator 4.11
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
        Dialog.resize(294, 354)
        self.gridLayout_3 = QtGui.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.main_pro_addr = QtGui.QLineEdit(Dialog)
        self.main_pro_addr.setObjectName(_fromUtf8("main_pro_addr"))
        self.gridLayout_2.addWidget(self.main_pro_addr, 0, 1, 1, 2)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.BCI2000_addr = QtGui.QLineEdit(Dialog)
        self.BCI2000_addr.setObjectName(_fromUtf8("BCI2000_addr"))
        self.gridLayout_2.addWidget(self.BCI2000_addr, 1, 1, 1, 2)
        self.bt_auto_model = QtGui.QPushButton(Dialog)
        self.bt_auto_model.setObjectName(_fromUtf8("bt_auto_model"))
        self.gridLayout_2.addWidget(self.bt_auto_model, 2, 0, 1, 2)
        self.bt_cmd_model = QtGui.QPushButton(Dialog)
        self.bt_cmd_model.setObjectName(_fromUtf8("bt_cmd_model"))
        self.gridLayout_2.addWidget(self.bt_cmd_model, 2, 2, 1, 1)
        self.bt_new_trial = QtGui.QPushButton(Dialog)
        self.bt_new_trial.setObjectName(_fromUtf8("bt_new_trial"))
        self.gridLayout_2.addWidget(self.bt_new_trial, 3, 0, 1, 2)
        self.bt_estop = QtGui.QPushButton(Dialog)
        self.bt_estop.setObjectName(_fromUtf8("bt_estop"))
        self.gridLayout_2.addWidget(self.bt_estop, 3, 2, 1, 1)
        self.bt_cease_current_task = QtGui.QPushButton(Dialog)
        self.bt_cease_current_task.setObjectName(_fromUtf8("bt_cease_current_task"))
        self.gridLayout_2.addWidget(self.bt_cease_current_task, 4, 0, 1, 2)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 2)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.wheechair_addr = QtGui.QLineEdit(Dialog)
        self.wheechair_addr.setObjectName(_fromUtf8("wheechair_addr"))
        self.gridLayout.addWidget(self.wheechair_addr, 1, 1, 1, 2)
        self.bt_forward = QtGui.QPushButton(Dialog)
        self.bt_forward.setObjectName(_fromUtf8("bt_forward"))
        self.gridLayout.addWidget(self.bt_forward, 2, 0, 1, 2)
        self.bt_reverse = QtGui.QPushButton(Dialog)
        self.bt_reverse.setObjectName(_fromUtf8("bt_reverse"))
        self.gridLayout.addWidget(self.bt_reverse, 2, 2, 1, 1)
        self.bt_tleft = QtGui.QPushButton(Dialog)
        self.bt_tleft.setObjectName(_fromUtf8("bt_tleft"))
        self.gridLayout.addWidget(self.bt_tleft, 3, 0, 1, 2)
        self.bt_tright = QtGui.QPushButton(Dialog)
        self.bt_tright.setObjectName(_fromUtf8("bt_tright"))
        self.gridLayout.addWidget(self.bt_tright, 3, 2, 1, 1)
        self.bt_rleft = QtGui.QPushButton(Dialog)
        self.bt_rleft.setObjectName(_fromUtf8("bt_rleft"))
        self.gridLayout.addWidget(self.bt_rleft, 4, 0, 1, 2)
        self.bt_rright = QtGui.QPushButton(Dialog)
        self.bt_rright.setObjectName(_fromUtf8("bt_rright"))
        self.gridLayout.addWidget(self.bt_rright, 4, 2, 1, 1)
        self.bt_stop = QtGui.QPushButton(Dialog)
        self.bt_stop.setObjectName(_fromUtf8("bt_stop"))
        self.gridLayout.addWidget(self.bt_stop, 5, 0, 1, 2)
        self.gridLayout_3.addLayout(self.gridLayout, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "MainPro", None))
        self.main_pro_addr.setText(_translate("Dialog", "127.0.0.1-9098", None))
        self.label_2.setText(_translate("Dialog", "BCI2000", None))
        self.BCI2000_addr.setText(_translate("Dialog", "127.0.0.1-9099", None))
        self.bt_auto_model.setText(_translate("Dialog", "自动模式", None))
        self.bt_cmd_model.setText(_translate("Dialog", "命令模式", None))
        self.bt_new_trial.setText(_translate("Dialog", "新一轮控制", None))
        self.bt_estop.setText(_translate("Dialog", "轮椅急停", None))
        self.bt_cease_current_task.setText(_translate("Dialog", "中断当前任务", None))
        self.label_3.setText(_translate("Dialog", "直接控制区", None))
        self.label_4.setText(_translate("Dialog", "小车", None))
        self.wheechair_addr.setText(_translate("Dialog", "127.0.0.1-9097", None))
        self.bt_forward.setText(_translate("Dialog", "前进", None))
        self.bt_reverse.setText(_translate("Dialog", "后退", None))
        self.bt_tleft.setText(_translate("Dialog", "左移", None))
        self.bt_tright.setText(_translate("Dialog", "右移", None))
        self.bt_rleft.setText(_translate("Dialog", "左转", None))
        self.bt_rright.setText(_translate("Dialog", "右转", None))
        self.bt_stop.setText(_translate("Dialog", "停止", None))

