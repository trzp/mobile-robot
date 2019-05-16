#!/usr/bin/env python
#coding:utf-8

import os,sys
rootdir = os.path.dirname(os.path.abspath(__file__))
updir = os.path.dirname(rootdir)


import pygame
from pygame.locals import *
from block import *
import socket
from pykinect import KinectClientV2019
from kcftracker_mul_pro import tracker_pro, TrackerPro
from RmCar import RmCar_x64
import multiprocessing
from yolo_mul_pro import yolo_pro, Yolo_Pro

from mr_params import *

class MobileRobot():
    def __init__(self):
        # kinect initialize
        self.kk = KinectClientV2019()

        # yolo initialize
        self.yolo = Yolo_Pro()
        y_ = multiprocessing.Process(target=yolo_pro, args=(self.yolo.args,))
        # y_.start()

        
        # flag initilize
        self.UPDATE_IMAGE = True
        self.STIM_CODE = -1
        self.EXP_MODE = 'COMMAND_MODE'
        self.current_task = -1
        self.current_result = -1
        self.manul_cmd = ['forward', 'rleft', 'left', 'rright', 'right']
        
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind(MAIN_ADDR)
        self.sock.setblocking(0)
        
        self.scr_initialize()
        
    def parse_commands(self):
        res = None
        try:
            buf, addr = self.sock.recvfrom(128)
            bb = buf.split('**')
            for b in bb:
                if b in ['COMMAND_MODE','AUTO_MODE','TRAIN_MODE']:
                    self.EXP_MODE = b
                elif b == 'NEW_TRIAL':
                    self.reset_trials_4_task()
                    self.current_result = -1
                elif b == 'stop_update_image':
                    self.UPDATE_IMAGE = False
                elif b == 'update_image':
                    self.UPDATE_IMAGE = True
                elif b[:6] == 'result':  # 收到result,发送任务
                    r = int(b[6:7])
                    self.current_result = r
                    self.current_task = -1
                    res = ['result',r]
                elif b[:4] == 'code':
                    self.STIM_CODE = int(b[4:6])  # code-1, code00, code01 ...
                elif b == 'cease_task':  # operator终止当前任务
                    self.current_task = -1
                    self.sock2bci.sendto('TASKCOMPLETED', BCI2000_HOST_ADDR)  # 回复bci2000动作已经完成
                elif b[:10] == 'train_task':   # train模式下，发送的任务
                    self.assign_task = int(b[10:11])
                elif b[:4] == 'task':
                    r = int(b[4:5])
                    res = ['task',r]
                    self.current_task = r
                    self.current_result = -1
                    print self.current_task
                elif b == '':
                    pass
        except:
            pass

    def scr_initialize(self):
        # main screen initialize
        pygame.init()
        pygame.font.init()
        self.scr = pygame.display.set_mode(SCREEN_SIZE, 0, 32)  # 主界面初始化
        self.clk = pygame.time.Clock()

        # 界面布局
        self.command_pos = ((512, 50), (75, 300), (75, 550), (948, 300), (948, 550))
        com_str = (u'前进', u'左转', u'左移', u'右转', u'右移')
        self.commands_cue = []
        for i in xrange(5):
            k = Block(self.scr, **{'size': (150, 100), 'forecolor': (128, 128, 128, 0), 'position': self.command_pos[i],
                              'anchor': 'center', 'text': com_str[i],
                              'textsize': 40, 'visible': True, 'layer': 2, 'textfont': 'simkai', 'borderon': False,
                              'bordercolor': (255, 0, 0, 0)})
            self.commands_cue.append(k)
        
        self.P3_sti = Block(self.scr, **{'size': (150, 100), 'forecolor': (255, 255, 0, 0), 'anchor': 'center', 'visible': False,
                               'layer': 3})

        # auto_tar_cue = []
        self.color_table = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 0), (128, 255, 0))


    def border_off(self,ob):
        ob.bordercolor = (255,0,0)
        ob.borderon = False

    def train_scr_update(self):
        for st in self.commands_cue:         #重置边框颜色
            st.bordercolor = (255,0,0)
            st.borderon = False
            st.reset()
            st.show()

        if self.current_task > -1:
            self.commands_cue[self.current_task].bordercolor = (0,255,0)
            self.commands_cue[self.current_task].borderon = True  # 标识当前训练任务
            self.commands_cue[self.current_task].reset()
            self.commands_cue[self.current_task].show()

        if self.STIM_CODE >= 0 and self.STIM_CODE < 5:      # 刷刺激块
            self.P3_sti.position = self.command_pos[self.STIM_CODE]
            self.P3_sti.reset()
            self.P3_sti.visible = True
            self.P3_sti.show()
        else:
            self.P3_sti.visible = False
            self.P3_sti.reset()
            
        if self.current_result > -1:
            self.commands_cue[self.current_result].bordercolor = (255,0,0)
            self.commands_cue[self.current_result].borderon = True  # 标识当前训练任务
            self.commands_cue[self.current_result].reset()
            self.commands_cue[self.current_result].show()


    def mainloop(self):
        # KINECT_SUR = self.kk.get_color_as_pgsurface()  # kinect初始化
        KINECT_SUR = pygame.image.load('./tem.jpg').convert()

        END = False
        while not END:
            # update screen and yolo
            if self.UPDATE_IMAGE:
                # KINECT_SUR = self.kk.get_color_as_pgsurface()
                KINECT_SUR = pygame.transform.smoothscale(KINECT_SUR, SCREEN_SIZE)

            # update background of the screen
            self.scr.blit(KINECT_SUR, (0, 0))
            res = self.parse_commands()
            self.train_scr_update()

            # deal with user events
            ev = pygame.event.get()
            for e in ev:
                if e.type == QUIT:    END = True
            pygame.display.update()
            self.clk.tick(60)

        pygame.quit()
        self.kk.release()

if __name__ == "__main__":
    m = MobileRobot()
    m.mainloop()
