# -*- coding: utf-8 -*-
# auhor: mrtang

import os,sys

root_dir = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(root_dir)

from mrobot_dialog import Ui_Dialog
from PyQt4 import QtCore, QtGui
import socket


class MainWindow(QtGui.QDialog): 

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui=Ui_Dialog() #上面ui类名
        self.ui.setupUi(self)
        
        #布局与事件分离
        QtCore.QObject.connect(self.ui.bt_auto_model, QtCore.SIGNAL("clicked()"), self.bt_auto_model_slot)
        QtCore.QObject.connect(self.ui.bt_cmd_model, QtCore.SIGNAL("clicked()"), self.bt_cmd_model_slot)
        QtCore.QObject.connect(self.ui.bt_new_trial, QtCore.SIGNAL("clicked()"), self.bt_new_trial_slot)
        QtCore.QObject.connect(self.ui.bt_cease_current_task, QtCore.SIGNAL("clicked()"), self.bt_cease_current_task_slot)
        QtCore.QObject.connect(self.ui.bt_estop, QtCore.SIGNAL("clicked()"), self.bt_estop_slot)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        
        self.mode = 'cmd'
        
    def update_addr(self):
        main_addr = self.ui.main_pro_addr.text().split('-')
        self.main_addr = (main_addr[0],int(main_addr[1]))
        
        BCI2000_addr = self.ui.BCI2000_addr.text().split('-')
        self.BCI2000_addr = (BCI2000_addr[0],int(BCI2000_addr[1]))
        
    def bt_cease_current_task_slot(self):
        self.sock.sendto('**STOP_MOVING',self.main_addr)
        print 'STOP MOVING'

    def bt_auto_model_slot(self):
        self.mode = 'auto'
        self.update_addr()
        # self.sock.sendto('**AUTO_MODE',self.main_addr)
        self.sock.sendto('**AUTO_MODE',self.BCI2000_addr)
        print 'AUTO_MODE'
    
    def bt_cmd_model_slot(self):
        self.mode = 'cmd'
        self.update_addr()

        # self.sock.sendto('**COMMAND_MODE',self.main_addr)
        self.sock.sendto('**COMMAND_MODE',self.BCI2000_addr)
        print 'COMMAND_MODE'
    
    def bt_new_trial_slot(self):
        self.update_addr()
        self.sock.sendto('**NEW_TRIAL',self.BCI2000_addr)
        print 'NEW_TRIAL'
    
    def bt_estop_slot(self):
        pass

if __name__ == "__main__":

    import sys
    app = QtGui.QApplication(sys.argv)
    myapp=MainWindow()
    myapp.show()
app.exec_()