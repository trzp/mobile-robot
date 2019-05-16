#-*- coding:utf-8 -*-

#提供了标准的P300训练程序
# written：mrtang
# date: 2015.7.26

from VisionEgg.Textures import Texture
import string
from AppTools.Displays import fullscreen
from AppTools.Shapes import PolygonTexture,Block
from AppTools.Boxes import box
import os,sys

# sys.path.append('..\\..')

from mr_params import *

GUIADDR = MAIN_ADDR


import socket
import numpy as np
import copy

import random
from get_sock_command import getCmd
from copy import copy


# bci2000系统中所有标记均为1开始，包括matlab结果返回
# 但是向外传递的刺激编码和结果均从0开始

TRIAL_NUM = 3  #一个任务允许几次尝试


class BciApplication(BciGenericApplication):

    def Description(self):
        return 'p3 experiment'

    def Construct(self):
        self.define_param(
            # you should not modify these codes
            "PythonApp:ExpCtr             int         ExpMode=                 2 % % % //0-offline trainning, 1-online trainning, 2-free mode",
            "PythonApp:ExpCtr             int         Debug=                     1 1 % % //1-debug,0-non debug",
            "PythonApp:ExpCtr             int         NumberOfTasks=             8 % % % //system will randomly set tasks",
            "PythonApp:ExpCtr             intlist     cube_dim=                 2 4 4 % % //code dim",
            "PythonApp:ExpCtr             int         NumberOfSequences=         3 10 1 100 // number of repeated sequences",
            "PythonApp:ExpCtr             int         PreSequenceDuration=     2500 1000 0 % // duration before stimulus sequence(ms)",
            "PythonApp:ExpCtr             float       StimulusDuration=         120 200 10 2000 // duration of each stimulus",
            "PythonApp:ExpCtr             float       ISIDuration=             120 200 10 2000 // iner-stimulus interval duration",
            "PythonApp:Design             int         ScreenId=                 -1  -1 % % // on which screen should the stimulus window be opened - use -1 for last",
            "PythonApp:Design             float       ScreenSiz=                 0.8 0.8 % % // on which screen should the stimulus window be opened - use -1 for last",
            )

        self.define_state(
            # you should not modify these code
            "StimulusType 1 0 0 0",         # 记录靶刺激状态.0-无靶 1-有靶
            "StimulusCode 16 0 0 0",        # 记录闪烁序列编号。为16位整数。可记录2^16-1个刺激对象。0为无效
            "PhaseInSequence 2 0 0 0",      # 1:序列前，2：序列中，3：序列后
            "Task 8 0 0 0",                 #255为无效值
        )

    def Preflight(self, sigprops):    # you should not modity this function
        #参数初始化
        self.nextoutseq = False                                                    #用来指示是否为当前sequences的最后一次闪烁
        self.ExpMode = int(self.params['ExpMode'])                                 #实验模式控制
        self.ResultTask = ''
        
        #屏幕初始化
        fullscreen(scale=0.3, id=int(self.params['ScreenId']))

    def Initialize(self, indim, outdim):    # you should not modity this function
        self.necessary_setup(self.ExpMode)                                            #必要的设置，无需特别修改

        self.sock_2_main = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.jump_to_wait_cmd = False
        self.cmd_listoner = getCmd()
        self.expmode = 'COMMAND_MODE'
        self.NumberOfSequences = int(self.params['NumberOfSequences'])
        
    def StartRun(self):        # you should not modity this function
        self.states['StimulusType'] = 0
        self.states['StimulusCode'] = 0
        self.states['PhaseInSequence'] = 0
        self.states['Task'] = 0

    def Phases(self):    # you should not modity this function
        self.phase(name='ready',                 next='wait_cmd',         duration=2000)
        self.phase(name='wait_cmd',)
        self.phase(name='wait_task')

        self.phase(name='presequences',         next='sequences',             duration=int(self.params['PreSequenceDuration']))    
        self.phase(name='sequences',             next='postsequences',         duration=int(self.params['StimulusDuration']))
        self.phase(name='postsequences',         next='sequences',             duration=int(self.params['ISIDuration']))
        
        self.phase(name='resdisp',)
        self.phase(name='action')
        self.phase(name='stop',                    duration=5000)

        if self.nextoutseq and self.in_phase('sequences'):
            self.phase(name='postsequences',     next='resdisp',             duration=2000 - int(self.params['ISIDuration'])-int(self.params['StimulusDuration']))

        self.design(start='ready', new_trial='presequences', interblock='idle')

    def Transition(self, phase):    # you should not modity this function
        if phase == 'ready':
            self.stimuli['Info'].text = 'Ready!'
            self.stimuli['Info'].on = True
            self.states['StimulusType'] = 0
            self.states['StimulusCode'] = 0
            self.states['PhaseInSequence'] = 0
            self.states['Task'] = 0
            
        elif phase == 'wait_cmd':
            self.jump_to_wait_cmd = False
            self.jump_wc_2_wt = False
            self.targetnum = 5          #临时变量 正常设为0
            self.jump_wt_2_pre = False
            self.jump_wt_2_wc = False
            self.jump_action_2_wc = False
            self.currenttask = 1
            
            
            self.sock_2_main.sendto('**update_image',GUIADDR)

            self.stimuli['Info'].text = 'waiting command!'
            self.states['StimulusType'] = 0
            self.states['StimulusCode'] = 0
            self.states['PhaseInSequence'] = 0
            self.states['Task'] = 0
            self.ResDisplay = False
            
        elif phase == 'wait_task':
            if self.expmode == 'AUTO_MODE':
                self.sock_2_main.sendto('**NEW_TRIAL**stop_update_image',GUIADDR)
            self.jump_wc_2_wt = False

            self.stimuli['Info'].text = 'waiting task!'
            self.states['StimulusType'] = 0
            self.states['StimulusCode'] = 0
            self.states['PhaseInSequence'] = 0
            self.states['Task'] = 0
            self.ResDisplay = False
            self.trial_num = TRIAL_NUM              #允许尝试3次

        elif phase == 'presequences':
            self.code = code_gen(1,6,self.NumberOfSequences)
            self.jump_wc_2_wt = False
            self.ResDisplay = False
            self.jump_res_2_pre = False
            self.jump_res_2_action = False
            
            
            self.stimuli['Info'].on = True
            self.stimuli['Info'].text = 'new trial'
            self.nextoutseq = False
            self.states['StimulusCode'] = 0
            self.states['StimulusType'] = 0
            self.states['PhaseInSequence'] = 1
            self.states['Task'] = 0

        elif phase == 'sequences':                                 #发送出去的code均减1
            self.states['PhaseInSequence'] = 2
            self.current_code = self.code.pop()
            self.states['StimulusCode'] = self.current_code

            if self.current_code == self.currenttask:    self.states['StimulusType'] = 1
            else:                                        self.states['StimulusType'] = 0

            self.sock_2_main.sendto('**code'+str(self.current_code-1),GUIADDR)
            self.stimuli['Info'].text = '[stimulus code:] ' + str(self.current_code)

        elif phase == 'postsequences':
            self.sock_2_main.sendto('**code-1',GUIADDR)
            self.states['StimulusCode'] = 0
            if len(self.code) < 2:    self.nextoutseq = True

        elif phase == 'resdisp':
            self.states['PhaseInSequence'] = 3
            self.states['Task'] = 0
            self.ResultTask = ''
            self.jump_action_2_wc = False
            self.states['StimulusType'] = 0
            self.states['StimulusCode'] = 0
            self.states['Task'] = 0
            
        elif phase == 'action':
            self.stimuli['Info'].text = 'action'
            sendbuf = '**update_image**result'+str(self.action_num)

            self.sock_2_main.sendto(sendbuf,GUIADDR)

        elif phase == 'stop':
            self.states['StimulusCode'] = 0
            self.states['StimulusType'] = 0
            self.stimuli['Info'].text = 'End'
            self.stimuli['Info'].on = True
        
        else:
            pass


    # matlab 传递的结果时1，2，3，4，5，6
    def Process(self, sig):        # you should not modity this function
        res = np.asarray(sig)[0].astype(np.int32)
        if self.in_phase('resdisp') and res[0]>-1:
            if not self.ResDisplay:
                self.stimuli['Info'].text = '[result] ' + str(res)
                self.ResDisplay = True
                
                res = list(res)
                # resdisp且得到结果，只会进一次
                for i in xrange(6):
                    cr = res.pop()
                    if cr <= self.targetnum:    #得到当前允许的结果
                        break
                
                self.trial_num -= 1

                if self.trial_num > 0 and cr != self.currenttask:  #结果不正确最多三次强制执行
                    self.jump_res_2_pre = True
                else:
                    self.jump_res_2_action = True
                    self.action_num = cr - 1
        
        if self.in_phase('resdisp'):
            if self.jump_res_2_action:
                self.change_phase('action')
            if self.jump_res_2_pre:
                self.change_phase('presequences')

        # 等待命令  自动模式/命令模式/新一个任务
        if self.in_phase('wait_cmd'):
            cmds = copy(self.cmd_listoner.cmds)
            self.cmd_listoner.cmds = []
            for c in cmds:
                if c == 'AUTO_MODE':
                    self.expmode = c
                    self.sock_2_main.sendto('**AUTO_MODE',GUIADDR)
                elif c == 'COMMAND_MODE':
                    self.expmode = c
                    self.sock_2_main.sendto('**COMMAND_MODE',GUIADDR)
                elif c == 'NEW_TRIAL':
                    self.jump_wc_2_wt = True
                    # if self.expmode == 'AUTO_MODE':
                        # self.sock_2_main.sendto('**NEW_TRIAL**stop_update_image',GUIADDR)
                        # print '**NEW_TRIAL**stop_update_image'
                        # gui得到new_trial命令后，将立即回复当前可用命令数
                else:
                    pass
            
            # 得到进行新任务的指令，跳转
            if self.jump_wc_2_wt:
                self.change_phase('wait_task')
        
        # 等待任务 此时命令队列中将得到可用命令数
        if self.in_phase('wait_task'):            #gui接受到newtirla之后会立即回复targetnum
            cmds = copy(self.cmd_listoner.cmds)
            self.cmd_listoner.cmds = []
            for c in cmds:
                if c[:4] == 'task':  #受领任务
                    if self.expmode == 'COMMAND_MODE':
                        self.targetnum = 5
                    self.currenttask = int(c[4:5])
                    if self.targetnum == 0:
                        self.jump_wt_2_wc = True
                    else:
                        self.states['Task'] = self.currenttask
                        self.jump_wt_2_pre = True
                        
                    self.sock_2_main.sendto('**assignedtask%d'%(self.currenttask-1)+c,GUIADDR)  #发送给主程序的都减1
                elif c[:9] == 'targetnum':
                    self.targetnum = int(c[9:10])
                    
            
            if self.jump_wt_2_wc:
                self.change_phase('wait_cmd')
            
            if self.jump_wt_2_pre:
                self.change_phase('presequences')
        
        if self.in_phase('action'):
            cmds = copy(self.cmd_listoner.cmds)
            self.cmd_listoner.cmds = []
            for c in cmds:
                if c[:9] == 'completed':
                    self.jump_action_2_wc = True
            
            if self.jump_action_2_wc:
                self.change_phase('wait_cmd')

    def necessary_setup(self,mode):
        scrw,scrh = self.screen.size
        center = [scrw/2,scrh/2]

        # result setup
        stim = VisualStimuli.Text(text = '', position  = (50,scrh-75), anchor = 'left', color = (1,1,0),font_name =r'C:\Windows\Fonts\Arial.TTF', font_size = 30, on = True)
        self.stimulus('rescue',z=1,stim = stim)

        # info setup
        textstim = VisualStimuli.Text(text = 'Ready', position  = center, anchor = 'center', color = (0,1,0), font_size = 80, on = False)
        # mz = max([int(str(x)[-2]) for x in self.stimuli.values()])
        mz = 2
        self.stimulus('Info', z=mz+1, stim = textstim)

def code_gen(start,len,reps):
    seq = range(start,start+len)
    random.shuffle(seq)
    count = 0
    while True:
        tem = range(start,start+len)
        random.shuffle(tem)
        if tem[0] != seq[-1]:
            seq.extend(tem)
            count += 1
            if count == reps -1:
                break
    return seq
