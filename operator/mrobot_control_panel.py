# -*- coding: utf-8 -*-
# auhor: mrtang

import os,sys

root_dir = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(root_dir)

# from mrobot_dialog import Ui_Dialog
from mobile_robot import Ui_Dialog
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
        
        QtCore.QObject.connect(self.ui.bt_forward, QtCore.SIGNAL("clicked()"), self.bt_forward_slot)
        QtCore.QObject.connect(self.ui.bt_reverse, QtCore.SIGNAL("clicked()"), self.bt_reverse_slot)
        QtCore.QObject.connect(self.ui.bt_tleft, QtCore.SIGNAL("clicked()"), self.bt_tleft_slot)
        QtCore.QObject.connect(self.ui.bt_tright, QtCore.SIGNAL("clicked()"), self.bt_tright_slot)
        QtCore.QObject.connect(self.ui.bt_rleft, QtCore.SIGNAL("clicked()"), self.bt_rleft_slot)
        QtCore.QObject.connect(self.ui.bt_rright, QtCore.SIGNAL("clicked()"), self.bt_rright_slot)
        QtCore.QObject.connect(self.ui.bt_stop, QtCore.SIGNAL("clicked()"), self.bt_stop_slot)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        
        self.mode = 'cmd'
        
    def bt_forward_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**forward',self.wc_addr)
        
    def bt_stop_slot(self):
        self.update_addr()
        self.sock.sendto('##stop',self.wc_addr)
    
    def bt_reverse_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**backward',self.wc_addr)
        
    def bt_tleft_slot(self):    
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**left',self.wc_addr)
    
    def bt_tright_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**right',self.wc_addr)
    
    def bt_rleft_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**rleft',self.wc_addr)
    
    def bt_rright_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**rright',self.wc_addr)
        
    def update_addr(self):
        main_addr = self.ui.main_pro_addr.text().split('-')
        self.main_addr = (main_addr[0],int(main_addr[1]))
        
        BCI2000_addr = self.ui.BCI2000_addr.text().split('-')
        self.BCI2000_addr = (BCI2000_addr[0],int(BCI2000_addr[1]))
        
        wc_addr = self.ui.wheechair_addr.text().split('-')
        self.wc_addr = (wc_addr[0],int(wc_addr[1]))
        
    def bt_cease_current_task_slot(self):
        self.sock.sendto('**cease_task',self.main_addr)
        self.sock.sendto('##stop',self.wc_addr)
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
        # self.sock.sendto('**NEW_TRIAL',self.main_addr)
        print 'NEW_TRIAL'

    # 发送assign_taskN
    
    def bt_estop_slot(self):
        pass

if __name__ == "__main__":

    import sys
    app = QtGui.QApplication(sys.argv)
    myapp=MainWindow()
    myapp.show()
app.exec_()