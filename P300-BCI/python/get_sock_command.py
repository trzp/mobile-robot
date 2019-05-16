# -*- coding: utf-8 -*-
# auhor: mrtang

import threading
from threading import Event
import socket

import os
import sys

# rootdir = os.path.dirname(os.path.abspath(__file__))
# rootdir1 = os.path.dirname(rootdir)
# rootdir2 = os.path.dirname(rootdir1)

# sys.path.append(rootdir2)

from mr_params import *
MYADDR =  BCI2000_ADDR

import time

class getCmd(threading.Thread):
    
    def __init__(self):
        self.ev = Event()
        threading.Thread.__init__(self)
        self.cmds = []
        
        self.from_operator = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.from_operator.bind(MYADDR)
        print MYADDR
        # self.from_operator.setblocking(0)
        
        self.setDaemon(True)
        self.start()

    def run(self):
        while not self.ev.isSet():
            buf,_ = self.from_operator.recvfrom(128)
            print buf
            tem = buf.split('**')
            print tem
            for t in tem:
                print 'get command >>> %s'%t
            self.cmds.extend(tem)

    
    def __del__(self):  #定义退出时的动作
        self.from_operator.sendto('end',MYADDR) #确保不被阻塞
        self.ev.set()

if __name__ == '__main__':
    g = getCmd()
    g.start()
    while True:
        print g.cmds
        g.cmds = []
        time.sleep(2)