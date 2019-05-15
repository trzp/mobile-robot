#!/usr/bin/env python
#coding:utf-8

import os,sys
rootdir = os.path.dirname(os.path.abspath(__file__))
updir = os.path.dirname(rootdir)
sys.path.append(os.path.join(updir,'Parameters'))
import pygame
from pygame.locals import *
from block import *
import socket
from pykinect import KinectClientV2019
from kcftracker_mul_pro import tracker_pro, Tracker_Pro
from RmCar import RmCar_x64
import multiprocessing
from yolo_mul_pro import yolo_pro, Yolo_Pro

class MobileRobot():
    def __init__(self):
        # kinect initialize
        self.kk = KinectClientV2019()

        # rm car initialize
        self.rm = RmCar_x64(True)

        # tracker initialize
        self.track = Tracker_Pro()
        t_ = multiprocessing.Process(target=tracker_pro, args=(self.track.args,))
        t_.start()

        # yolo initialize
        self.yolo = Yolo_Pro()
        y_ = multiprocessing.Process(target=yolo_pro, args=(self.yolo.args,))
        y_.start()

        # sock initialize
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(GUI_HOST_ADDR)
        self.sock.setblocking(0)
        self.sock2bci = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 用于同BCI2000交互
        
        # flag initilize
        self.UPDATE_IMAGE = True
        self.STIM_CODE = -1
        self.EXP_MODE = 'AUTO_MODE'
        self.current_task = -1
        self.manul_cmd = ['forward', 'rleft', 'left', 'rright', 'right']
        self.targets = []
        
        self.current_task_name = 'chair'
        self.assign_task = -1
        self.trials_4_task = None   # 一个任务最多允许多少次trial，超过计数，错误命令也将被执行

        self.scr_initialize()

    def reset_trials_4_task(self):
        self.trials_4_task = 3
        
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
                              'textsize': 40, 'visible': True, 'layer': 2, 'textfont': 'kaiti', 'borderon': False,
                              'bordercolor': (255, 0, 0, 0)})
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
            self.target_text.append(k)
        
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
                elif b == 'stop_update_image':
                    self.UPDATE_IMAGE = False
                elif b == 'update_image':
                    self.UPDATE_IMAGE = True
                elif b[:6] == 'result':  # 收到result,发送任务
                    if self.EXP_MODE == 'TRAIN_MODE':   #训练模式立即清空assign_task是为了清除显示
                        self.assign_task = -1
                    res = np.fromstring(b[6:], dtype=np.int32).tolist()
                elif b[:4] == 'code':
                    self.STIM_CODE = int(b[4:6])  # code-1, code00, code01 ...
                elif b == 'cease_task':  # operator终止当前任务
                    self.current_task = -1
                    self.sock2bci.sendto('TASKCOMPLETED', BCI2000_HOST_ADDR)  # 回复bci2000动作已经完成
                elif b[:10] == 'train_task':   # train模式下，发送的任务
                    self.assign_task = int(b[10:11])
                elif b == '':
                    pass
        except:
            pass
        
        return res

    def command_action(self,res):
        self.current_task = res.pop()
        if self.current_task == 5:  self.current_task = res.pop()  # 命令模式只接受5个控制命令
        self.rm.pushtask(self.manul_cmd[self.current_task], 'manul')  # 驱动轮椅动作,由operator停止轮椅动作
        return

    def train_action(self,res):
        self.current_task = res.pop()
        print '[BCI2000 result] %d'%(self.current_task)
        return

    def auto_action(self,res):
        obj_num = len(self.targets)
        if obj_num == 0:
            self.current_task = -1
            self.sock2bci.sendto('TASKCOMPLETED', BCI2000_HOST_ADDR)  # 回复bci2000动作已经完成
            return
        else:
            while len(res) > 0:
                self.current_task = res.pop()
                if self.current_task < obj_num:
                    break

        tar = self.targets[self.current_task]  # 当前选中的目标
        self.current_task_name = tar['name']
        self.track.init_tracker(tar['box'])
        self.rm.pushtask(tar, 'auto')
        return

    def border_off(self,ob):
        ob.bordercolor = (255,0,0)
        ob.borderon = False

    def command_scr_update(self):
        [self.border_off(k) for k in self.commands_cue]          # 重置边框
        [k.show() for k in self.commands_cue]               # 显示命令块

        if self.assign_task > -1:    # 有训练任务
            self.commands_cue[self.assign_task].bordercolor = (0,255,0)
            self.commands_cue[self.assign_task].borderon = True  # 标识当前训练任务
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
            box, pos = self.track.update()
            x, y, w, h = box
            pygame.draw.rect(self.scr, (255, 255, 0),
                             ((int(x * X_RATIO), int(y * Y_RATIO)), (int(w * X_RATIO), int(h * Y_RATIO))), 2)
            if self.current_task_name == 'bottle':             # 跟踪器返回的定位提供了两种方法
                pos = pos['bottle']
            else:
                pos = pos['obj']

            if pos is not None:
                if self.rm.updatetask(pos):
                    self.current_task = -1
                    self.sock2bci.sendto('TASKCOMPLETED', BCI2000_HOST_ADDR)

        else:
            pass

        # updat stimuli
        obj_num = len(self.targets)
        if self.STIM_CODE >= 0 and self.STIM_CODE < 5 and self.STIM_CODE < obj_num:  # 绘制刺激块
            tar = self.targets[self.STIM_CODE]
            x, y, w, h = tar['box']
            pygame.draw.rect(self.scr, self.color_table[self.STIM_CODE],
                             ((int(x * X_RATIO), int(y * Y_RATIO)), (int(w * X_RATIO), int(h * Y_RATIO))), 0)

    def mainloop(self):
        KINECT_SUR = self.kk.get_color_as_pgsurface()  # kinect初始化
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
                self.command_scr_update()
                if res is not None:
                    self.command_action(res)
            if self.EXP_MODE == 'TRAIN_MODE':
                self.train_scr_update()
                if res is not None:
                    self.train_action(res)
            elif self.EXP_MODE == 'AUTO_MODE':
                self.auto_scr_update()
                if res is not None:
                    self.auto_action(res)
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
