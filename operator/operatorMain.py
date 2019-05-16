# -*- coding: utf-8 -*-
# auhor: mrtang

import os,sys

root_dir = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(root_dir)

# from mrobot_dialog import Ui_Dialog
from operatorUi import Ui_Dialog
from PyQt4 import QtCore, QtGui
import socket
import json
import sys


# 主控面板负责和BCI2000通信，告知控制模式，启动新任务等
# 和weehlchair通信，直接干预


# 任务0，1，2，3，4，5显示的时从0开始，是为了和gui对应。实际发送给bci2000的数字是1，2，3，4，5，6


class MainWindow(QtGui.QDialog): 

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui=Ui_Dialog() #上面ui类名
        self.ui.setupUi(self)
        
        #布局与事件分离
        # 模式控制
        QtCore.QObject.connect(self.ui.bt_auto_model, QtCore.SIGNAL("clicked()"), self.bt_auto_model_slot)
        QtCore.QObject.connect(self.ui.bt_cmd_model, QtCore.SIGNAL("clicked()"), self.bt_cmd_model_slot)
        QtCore.QObject.connect(self.ui.bt_new_trial, QtCore.SIGNAL("clicked()"), self.bt_new_trial_slot)
        QtCore.QObject.connect(self.ui.bt_cease_current_task, QtCore.SIGNAL("clicked()"), self.bt_cease_current_task_slot)
        QtCore.QObject.connect(self.ui.bt_train_mode, QtCore.SIGNAL("clicked()"), self.bt_train_model_slot)
        
        # 人工干预
        QtCore.QObject.connect(self.ui.bt_forward, QtCore.SIGNAL("clicked()"), self.bt_forward_slot)
        QtCore.QObject.connect(self.ui.bt_reverse, QtCore.SIGNAL("clicked()"), self.bt_reverse_slot)
        QtCore.QObject.connect(self.ui.bt_tleft, QtCore.SIGNAL("clicked()"), self.bt_tleft_slot)
        QtCore.QObject.connect(self.ui.bt_tright, QtCore.SIGNAL("clicked()"), self.bt_tright_slot)
        QtCore.QObject.connect(self.ui.bt_rleft, QtCore.SIGNAL("clicked()"), self.bt_rleft_slot)
        QtCore.QObject.connect(self.ui.bt_rright, QtCore.SIGNAL("clicked()"), self.bt_rright_slot)
        QtCore.QObject.connect(self.ui.bt_stop, QtCore.SIGNAL("clicked()"), self.bt_stop_slot)
        
        # 任务分发区
        QtCore.QObject.connect(self.ui.bt_task0, QtCore.SIGNAL("clicked()"), self.bt_task0_slot)
        QtCore.QObject.connect(self.ui.bt_task1, QtCore.SIGNAL("clicked()"), self.bt_task1_slot)
        QtCore.QObject.connect(self.ui.bt_task2, QtCore.SIGNAL("clicked()"), self.bt_task2_slot)
        QtCore.QObject.connect(self.ui.bt_task3, QtCore.SIGNAL("clicked()"), self.bt_task3_slot)
        QtCore.QObject.connect(self.ui.bt_task4, QtCore.SIGNAL("clicked()"), self.bt_task4_slot)
        QtCore.QObject.connect(self.ui.bt_task5, QtCore.SIGNAL("clicked()"), self.bt_task5_slot)

        QtCore.QObject.connect(self.ui.save_param, QtCore.SIGNAL("clicked()"), self.write_addr)
        
        QtCore.QMetaObject.connectSlotsByName(self)


        try:
            with open(os.path.join(root_dir,'addr.txt'),'r') as f:
                buf = f.read()
                addrs = json.loads(buf)
                self.ui.main_pro_addr.setText(addrs['main'])
                self.ui.BCI2000_addr.setText(addrs['bci'])
                self.ui.wheechair_addr.setText(addrs['wc'])
        except:
            pass


        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        self.mode = 'cmd'
        
    def bt_train_model_slot(self):
        self.mode = 'train'
        self.update_addr()
        self.sock.sendto('**TRAIN_MODE',self.main_addr)
        self.sock.sendto('**TRAIN_MODE',self.BCI2000_addr)
        print '>>> train mode'

    def write_addr(self):
        main_text = str(self.ui.main_pro_addr.text())
        bci_text = str(self.ui.BCI2000_addr.text())
        wc_text = str(self.ui.wheechair_addr.text())

        with open(os.path.join(root_dir, 'addr.txt'), 'w') as f:
            buf = json.dumps({'wc': wc_text, 'main': main_text, 'bci': bci_text})
            f.write(buf)
        print '>>> save addrs'


    def bt_forward_slot(self):
        self.update_addr()
        self.sock.sendto('##pushtask**manul**forward',self.wc_addr)
        print '>>> forward'
        
    def bt_stop_slot(self):
        self.update_addr()
        self.sock.sendto('##stop',self.wc_addr)
        print '>>> stop'
    
    def bt_reverse_slot(self):
        self.update_addr()
        self.sock.sendto('##pushtask**manul**backward',self.wc_addr)
        print '>>> reverse'
        
    def bt_tleft_slot(self):
        self.update_addr()
        self.sock.sendto('##pushtask**manul**left',self.wc_addr)
        print '>>> left'
    
    def bt_tright_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**right',self.wc_addr)
        print '>>> right'
    
    def bt_rleft_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**rleft',self.wc_addr)
        print '>>> rotate left'
    
    def bt_rright_slot(self):
        self.update_addr()
        # self.bt_stop_slot()
        # time.sleep(0.2)
        self.sock.sendto('##pushtask**manul**rright',self.wc_addr)
        print '>>> rotate right'
        
    def update_addr(self):
        main_text = str(self.ui.main_pro_addr.text())
        main_addr = main_text.split('-')
        self.main_addr = (main_addr[0],int(main_addr[1]))

        bci_text = str(self.ui.BCI2000_addr.text())
        BCI2000_addr = bci_text.split('-')
        self.BCI2000_addr = (BCI2000_addr[0],int(BCI2000_addr[1]))

        wc_text = str(self.ui.wheechair_addr.text())
        wc_addr = wc_text.split('-')
        self.wc_addr = (wc_addr[0],int(wc_addr[1]))
        
    def bt_cease_current_task_slot(self):
        self.sock.sendto('**cease_task',self.main_addr)
        self.sock.sendto('##stop',self.wc_addr)
        self.sock.sendto('**completed',self.BCI2000_addr)
        
        print '>>> interrupt current task'

    def bt_auto_model_slot(self):
        self.mode = 'auto'
        self.update_addr()
        self.sock.sendto('**AUTO_MODE',self.main_addr)
        self.sock.sendto('**AUTO_MODE',self.BCI2000_addr)
        print '>>> auto mode'

    def bt_cmd_model_slot(self):
        self.mode = 'cmd'
        self.update_addr()

        self.sock.sendto('**COMMAND_MODE',self.main_addr)
        self.sock.sendto('**COMMAND_MODE',self.BCI2000_addr)
        print '>>> command mode'
    
    def bt_new_trial_slot(self):
        self.update_addr()
        self.sock.sendto('**NEW_TRIAL',self.BCI2000_addr)
        print '>>> new trial'

    def bt_task0_slot(self):
        self.update_addr()
        self.sock.sendto('**task1',self.BCI2000_addr)
        print '>>> task0'

    def bt_task1_slot(self):
        self.update_addr()
        self.sock.sendto('**task2',self.BCI2000_addr)
        print '>>> task1'

    def bt_task2_slot(self):
        self.update_addr()
        self.sock.sendto('**task3',self.BCI2000_addr)
        print '>>> task2'

    def bt_task3_slot(self):
        self.update_addr()
        self.sock.sendto('**task4',self.BCI2000_addr)
        print '>>> task3'

    def bt_task4_slot(self):
        self.update_addr()
        self.sock.sendto('**task5',self.BCI2000_addr)
        print '>>> task4'

    def bt_task5_slot(self):
        self.update_addr()
        self.sock.sendto('**task6',self.BCI2000_addr)
        print '>>> task5'


if __name__ == "__main__":

    import sys
    app = QtGui.QApplication(sys.argv)
    myapp=MainWindow()
    myapp.show()
app.exec_()