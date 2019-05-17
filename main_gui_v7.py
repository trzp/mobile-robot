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
from RmCar_server2 import rmRemoteClient

from mr_params import *

class MobileRobot():
    def __init__(self):
        # kinect initialize
        self.kk = KinectClientV2019()

        # yolo initialize
        self.yolo = Yolo_Pro()
        y_ = multiprocessing.Process(target=yolo_pro, args=(self.yolo.args,))
        y_.start()
        
        self.rm_client = rmRemoteClient()

        # sock initialize
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(MAIN_ADDR)
        self.sock.setblocking(0)
        self.sock2bci = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 用于同BCI2000交互
        
        # flag initilize
        self.UPDATE_IMAGE = True
        self.STIM_CODE = -1
        self.EXP_MODE = 'COMMAND_MODE'
        self.current_task = -1
        self.manul_cmd = ['forward', 'rleft', 'left', 'rright', 'right']
        self.targets = []
        
        self.current_task_name = 'chair'
        self.assign_task = -1
        self.scr_initialize()

    def scr_initialize(self):
        # main screen initialize
        pygame.init()
        pygame.font.init()
        self.scr = pygame.display.set_mode(SCREEN_SIZE, 0, 32)  # 主界面初始化
        self.clk = pygame.time.Clock()

        # 界面布局
        self.command_pos = ((512, 50), (75, 300), (75, 550), (948, 300), (948, 550))
        self.com_str = (u'前进', u'左转', u'左移', u'右转', u'右移')
        self.commands_cue = []
        for i in xrange(5):
            k = Block(self.scr, **{'size': (150, 100), 'forecolor': (128, 128, 128, 0), 'position': self.command_pos[i],
                              'anchor': 'center', 'text': self.com_str[i],
                              'textsize': 40, 'visible': True, 'layer': 2, 'textfont': 'kaiti', 'borderon': False,
                              'bordercolor': (255, 0, 0, 0),'borderwidth':2})
            self.commands_cue.append(k)
        
        self.P3_sti = Block(self.scr, **{'size': (150, 100), 'forecolor': (255, 255, 0, 0), 'anchor': 'center', 'visible': False,
                               'layer': 3})

        # auto_tar_cue = []
        self.color_table = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 0), (128, 255, 0))

        # 目标标识
        self.target_text = []
        self.target_str = {'person': u'人类', 'cup': u'杯子', 'bottle': u'瓶子', 'desk': u'桌子', 'sofa': u'沙发', 'chair': u'椅子'}
        for i in xrange(6):
            k = Block(self.scr, **{'size': (100, 40), 'forecolor': self.color_table[i], 'anchor': 'lefttop', 'textsize': 30,
                              'textcolor': (0, 0, 0), 'visible': False, 'layer': 2, 'textfont': 'kaiti'})
            k.reset()
            self.target_text.append(k)
        
    def parse_commands(self):
        res = None
        try:
            buf, addr = self.sock.recvfrom(128)
            bb = buf.split('**')
            for b in bb:
                if b in ['COMMAND_MODE','AUTO_MODE']:
                    self.EXP_MODE = b
                elif b == 'NEW_TRIAL':
                    self.assign_task = -1
                    self.current_task = -1
                    if self.EXP_MODE == 'AUTO_MODE':
                        self.sock2bci.sendto('**targetnum%d'%(len(self.targets)),BCI2000_ADDR)
                elif b == 'stop_update_image':
                    self.UPDATE_IMAGE = False
                elif b == 'update_image':
                    self.UPDATE_IMAGE = True
                elif b[:6] == 'result':  # 收到result,发送任务
                    res = self.current_task = int(b[6:7])
                    self.assign_task = -1
                elif b[:4] == 'code':
                    self.STIM_CODE = int(b[4:6])  # code-1, code00, code01 ...
                elif b == 'cease_task':  # operator终止当前任务
                    self.current_task = -1
                elif b[:12] == 'assignedtask':
                    self.assign_task = int(b[12:13])
                elif b == '':
                    pass
        except:
            pass
        return res

    def command_action(self,res):
        self.rm_client.pushtask(self.manul_cmd[self.current_task], 'manul')
        return

    def auto_action(self,res):
        tar = self.targets[res]  # 当前选中的目标
        self.rm_client.pushtask(tar,'auto')
        return

    def command_scr_update(self):
        for i in range(len(self.commands_cue)):
            ob = self.commands_cue[i]
            ob.borderon = False
            ob.bordercolor = (255,0,0)
            ob.text = str(i)+self.com_str[i]
            ob.textcolor = (0, 255, 255, 0)
            ob.reset()
            ob.show()
        
        if self.assign_task >= 0:
            self.commands_cue[self.assign_task].borderon = True
            self.commands_cue[self.assign_task].bordercolor = (0,0,0)
            self.commands_cue[self.assign_task].text = u'任务'
            self.commands_cue[self.assign_task].textcolor = (255,0,0)
            self.commands_cue[self.assign_task].reset()
            self.commands_cue[self.assign_task].show()

        if self.STIM_CODE >= 0 and self.STIM_CODE < 5:      # 刷刺激块
            self.P3_sti.position = self.command_pos[self.STIM_CODE]
            self.P3_sti.reset()
            self.P3_sti.visible = True
            self.P3_sti.show()
        else:
            self.P3_sti.visible = False
            self.P3_sti.reset()

        if self.current_task >= 0:
            self.commands_cue[self.current_task].borderon = True  # 标识当前的分类结果
            self.commands_cue[self.current_task].reset()
            self.commands_cue[self.current_task].show()

    def auto_scr_update(self):
        # 当前没有任务
        if self.current_task < 0:  # 当前没有任务显示目标检测的结果
            obj_num = len(self.targets)
            for i in xrange(6):
                if i < obj_num:
                    self.target_text[i].visible = True
                    tar = self.targets[i]
                    x, y, w, h = tar['box']
                    self.target_text[i].position = (int(x * X_RATIO), int(y * Y_RATIO))
                    self.target_text[i].text = str(i) + ' ' + self.target_str[tar['name']]
                    self.target_text[i].reset()
                    self.target_text[i].show()
                    pygame.draw.rect(self.scr, self.color_table[i],
                                     ((int(x * X_RATIO), int(y * Y_RATIO)), (int(w * X_RATIO), int(h * Y_RATIO))), 2)

        # 当前有任务
        elif self.current_task >= 0:
            x,y,w,h = box = self.rm_client.update_task()
            if box is not None:
            pygame.draw.rect(self.scr, (255, 255, 0),
                             ((int(x * X_RATIO), int(y * Y_RATIO)), (int(w * X_RATIO), int(h * Y_RATIO))), 2)
        else:
            pass

        if self.assign_task >= 0:
            i = self.assign_task
            self.target_text[i].visible = True
            tar = self.targets[i]
            x, y, w, h = tar['box']
            self.target_text[i].position = (int(x * X_RATIO), int(y * Y_RATIO))
            self.target_text[i].text = u'任务'
            self.target_text[i].reset()
            self.target_text[i].show()
            pygame.draw.rect(self.scr, (0,0,0),
                             ((int(x * X_RATIO), int(y * Y_RATIO)), (int(w * X_RATIO), int(h * Y_RATIO))), 4)

        # updat stimuli
        obj_num = len(self.targets)
        if self.STIM_CODE >= 0 and self.STIM_CODE < 5 and self.STIM_CODE < obj_num:  # 绘制刺激块
            tar = self.targets[self.STIM_CODE]
            x, y, w, h = tar['box']
            pygame.draw.rect(self.scr, self.color_table[self.STIM_CODE],
                             ((int(x * X_RATIO), int(y * Y_RATIO)), (int(w * X_RATIO), int(h * Y_RATIO))), 0)

    def mainloop(self):
        KINECT_SUR = self.kk.get_color_as_pgsurface()  # kinect初始化
        # KINECT_SUR = pygame.image.load('./tem.jpg').convert()

        END = False
        while not END:
            # update screen and yolo
            if self.UPDATE_IMAGE:
                KINECT_SUR = self.kk.get_color_as_pgsurface()
                KINECT_SUR = pygame.transform.smoothscale(KINECT_SUR, SCREEN_SIZE)
                self.targets = self.yolo.update()[:6]

            # update background of the screen
            self.scr.blit(KINECT_SUR, (0, 0))

            # dealing with upper command
            res = self.parse_commands()

            if self.EXP_MODE == 'COMMAND_MODE':
                if res is not None:
                    self.command_action(res)
                self.command_scr_update()
            elif self.EXP_MODE == 'AUTO_MODE':
                if res is not None:
                    self.auto_action(res)
                self.auto_scr_update()
            else:
                pass

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
