#-*- coding:utf-8 -*-

#提供了标准的P300训练程序
# written：mrtang
# date: 2015.7.26

import string
from VisionEgg.Textures import Texture
from AppTools.Displays import fullscreen
from AppTools.Shapes import PolygonTexture,Block
from AppTools.Boxes import box
import os
os.sys.path.append('.\\common')
from BCIFunc import generate_cube_codebook, generate_RC_codebook
import P3expBase
from tjsBCIFunc import tjs_generate_RC_codebook1

os.sys.path.append('..\\..')


import socket
import numpy as np

from params import *
import random

MYADDR =  BCI2000_HOST_ADDR
GUIADDR = GUI_HOST_ADDR

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
            "PythonApp:ExpCtr             float         StimulusDuration=         120 200 10 2000 // duration of each stimulus",
            "PythonApp:ExpCtr             float         ISIDuration=             120 200 10 2000 // iner-stimulus interval duration",
            "PythonApp:Design             int         ScreenId=                 -1  -1 % % // on which screen should the stimulus window be opened - use -1 for last",
            "PythonApp:Design             float         ScreenSiz=                 0.8 0.8 % % // on which screen should the stimulus window be opened - use -1 for last",
            )

        self.define_state(
            # you should not modify these code
            "StimulusType 1 0 0 0",        # 记录靶刺激状态.0-无靶 1-有靶
            "StimulusCode 16 0 0 0",    # 记录闪烁序列编号。为16位整数。可记录2^16-1个刺激对象。0为无效
            "PhaseInSequence 2 0 0 0",     # 1:序列前，2：序列中，3：序列后
            "Task 8 255 0 0",             # 记录当前的任务，255为无效
        )

    def Preflight(self, sigprops):    # you should not modity this function
        #参数初始化
        self.cube_dim = map(int,self.params['cube_dim'])                        #编码信息
        self.NumberOfSequences = int(self.params['NumberOfSequences'])            #重复刺激次数
        self.tasknum = int(self.params['NumberOfTasks'])
        self.nextoutseq = False                                                    #用来指示是否为当前sequences的最后一次闪烁
        #self.ExpMode = int(self.params['ExpMode'])                                #实验模式控制
        self.ExpMode = 2
        self.ResultTask = ''
        
        #屏幕初始化
        fullscreen(scale=0.5, id=int(self.params['ScreenId']))

    def Initialize(self, indim, outdim):    # you should not modity this function
        self.CmdLst = [str(i) for i in range(1,7)]
        self.cmd = P3expBase.CmdLstCtr(self.CmdLst,self.cube_dim[0]*self.cube_dim[1])    #用来控制任务序列生成等操作
        self.tasklist = self.cmd.GenTaskList(self.tasknum)                            #随机产生任务序列

        self.jump_to_seqs = False
        self.jump_to_again = False
        self.jump_from_wait_task_2_next = False

        self.necessary_setup(self.ExpMode)                                            #必要的设置，无需特别修改

        self.udp_listen_operator = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udp_listen_operator.bind(MYADDR)
        self.udp_listen_operator.setblocking(0)

        self.sock_2_main = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        self.expmode = 'COMMAND_MODE'

    def StartRun(self):        # you should not modity this function
        self.states['StimulusType'] = 0
        self.states['StimulusCode'] = 0
        self.states['PhaseInSequence'] = 0
        self.states['Task'] = 255

    def Phases(self):    # you should not modity this function
        self.phase(name='ready',                 next='wait_cmd',         duration=2000)
        self.phase(name='wait_cmd',)
        self.phase(name='wait_task')    #在此期间等待分配任务
        self.phase(name='presequences',         next='sequences',             duration=int(self.params['PreSequenceDuration']))
        self.phase(name='sequences',             next='postsequences',         duration=int(self.params['StimulusDuration']))
        self.phase(name='postsequences',         next='sequences',             duration=int(self.params['ISIDuration']))
        # self.phase(name='resdisp',                 next='wait_cmd',         duration=2500)
        self.phase(name='resdisp',)
        self.phase(name='stop',                    duration=5000)

        if self.nextoutseq and self.in_phase('sequences'):
            self.phase(name='postsequences',     next='resdisp',             duration=2000 - int(self.params['ISIDuration'])-int(self.params['StimulusDuration']))

        self.design(start='ready', new_trial='wait_cmd', interblock='idle')

    def Transition(self, phase):    # you should not modity this function
        if phase == 'ready':
            self.stimuli['Info'].text = 'Ready!'
            self.stimuli['Info'].on = True

        elif phase == 'wait_cmd':
            self.jump_from_wait_task_2_next = False
            self.jump_to_wait_cmd = False
            self.jump_to_again = False
            #总是默认更新图像
            self.sock_2_main.sendto('**update_image',GUIADDR)

            self.stimuli['Info'].text = 'waiting upper command!'
            self.states['StimulusType'] = 0
            self.states['StimulusCode'] = 0
            self.states['PhaseInSequence'] = 0
            self.states['Task'] = 255
            self.ResDisplay = False

        elif phase == 'presequences':
            self.jump_to_seqs = False
            self.nextoutseq = False
            self.ResDisplay = False
            self.states['StimulusCode'] = 0
            self.states['StimulusType'] = 0
            self.states['PhaseInSequence'] = 1

            self.stimuli['Info'].text = 'new trial'

            if self.expmode == 'TRAIN_MODE':    #训练模式下随机生成任务并发送给gui
                task = random.randint(0,5)
                self.states['Task'] = task
                self.sock_2_main.sendto('**train_task%s'%(task), GUIADDR)

            self.code,self.codebook,self.codeindex = CodeGen(self.cube_dim,self.NumberOfSequences)        #产生刺激序列

        elif phase == 'sequences':
            self.states['PhaseInSequence'] = 2
            self.states['StimulusCode'] = self.codeindex.pop(0)+1
            self.cur_codebook = self.codebook.pop(0)
            self.sock_2_main.sendto('**code'+str(self.cur_codebook[0]),GUIADDR)
            self.stimuli['Info'].text = '[stimulus code:] ' + str(self.cur_codebook)

        elif phase == 'postsequences':
            self.sock_2_main.sendto('**code-1',GUIADDR)
            self.states['StimulusCode'] = 0
            if len(self.codeindex) < 2:    self.nextoutseq = True

        elif phase == 'resdisp':
            self.states['PhaseInSequence'] = 3
            self.states['Task'] = 255
            self.ResultTask = ''

        elif phase == 'stop':
            self.states['StimulusCode'] = 0
            self.states['StimulusType'] = 0
            self.states['Task'] = 255
            self.stimuli['Info'].text = 'End'
            self.stimuli['Info'].on = True
        
        elif phase == 'target_preshow':   #进入自动模式，停止刷新图像
            self.sock_2_main.sendto('**stop_update_image',GUIADDR)

        else:
            pass

    def Process(self, sig):        # you should not modity this function
        # np.save('tem.npy',sig)
        res = sig[0].astype(np.int32)
        if self.in_phase('resdisp') and res[0,0]>-1:
            if not self.ResDisplay:
                self.stimuli['Info'].text = '[result] ' + str(res)
                self.ResDisplay = True
                buf = res.tostring()
                sendbuf = '**update_image**result'+buf  #一个trial结束，图像刷新开启，并且发送结果
                self.sock_2_main.sendto(sendbuf,GUIADDR)
        
        if self.in_phase('wait_cmd'):
            try:
                cmd,addr = self.udp_listen_operator.recvfrom(128)
                print cmd
                cmds = cmd.split('**')
                for c in cmds:
                    if c == 'AUTO_MODE':
                        self.expmode = c
                        self.sock_2_main.sendto('**AUTO_MODE',GUIADDR)
                    elif c == 'COMMAND_MODE':
                        self.expmode = c
                        self.sock_2_main.sendto('**COMMAND_MODE',GUIADDR)
                    elif c == 'TRAIN_MODE':
                        self.expmode = c
                        self.sock_2_main.sendto('**TRAIN_MODE', GUIADDR)
                    elif c == 'NEW_TRIAL':
                        self.jump_to_seqs = True
                    else:
                        pass
            except:
                pass

            if self.jump_to_seqs:
                # if self.expmode in ['COMMAND_MODE','TRAIN_MODE']:
                #     self.change_phase('presequences')
                # elif self.expmode == 'AUTO_MODE':
                #     self.change_phase('target_preshow')
                # else:
                #     pass

                if self.expmode == 'TRAIN_MODE':
                    self.change_phase('presequences')   # 自动分配任务
                else:
                    self.change_phase('wait_task')      # 手动分配任务

        if self.in_phase('wait_task'):
            try:
                cmd,addr = self.udp_listen_operator.recvfrom(128)
                print cmd
                cmds = cmd.split('**')
                for c in cmds:
                    if c[:11] == 'assign_task':
                        self.assign_task = int(c[11:12])
                        self.jump_from_wait_task_2_next = True
                    else:
                        pass
            except:
                pass

            if self.jump_from_wait_task_2_next:
                self.change_phase('presequences')
                    
        elif self.in_phase('resdisp'):
            try:
                cmd,addr = self.udp_listen_operator.recvfrom(128)
                print cmd
                cmds = cmd.split('**')
                for c in cmds:
                    if c == 'TASKCOMPLETED':
                        self.jump_to_wait_cmd = True
                    elif c == 'AGAIN':  #在此请求刺激
                        self.jump_to_again = True
                    else:
                        pass

            except:
                pass

            if self.jump_to_wait_cmd:
                self.change_phase('wait_cmd')

            if self.jump_to_again:
                self.change_phase('again')

    def necessary_setup(self,mode):
        scrw,scrh = self.screen.size
        center = [scrw/2,scrh/2]
 
        # task setup
        if mode < 2:
            str = '  '.join(self.tasklist)
            stim = VisualStimuli.Text(text = str, position  = (50,scrh-35), anchor = 'left', color = (1,1,1),font_name =r'C:\Windows\Fonts\Arial.TTF', font_size = 30, on = True)
            self.stimulus('taskcue',z=1,stim = stim)

        # result setup
        stim = VisualStimuli.Text(text = '', position  = (50,scrh-75), anchor = 'left', color = (1,1,0),font_name =r'C:\Windows\Fonts\Arial.TTF', font_size = 30, on = True)
        self.stimulus('rescue',z=1,stim = stim)

        # info setup
        textstim = VisualStimuli.Text(text = 'Ready', position  = center, anchor = 'center', color = (0,1,0), font_size = 80, on = False)
        # mz = max([int(str(x)[-2]) for x in self.stimuli.values()])
        mz = 2
        self.stimulus('Info', z=mz+1, stim = textstim)


def CodeGen(code_dim,reps):        # realize this function but follow the same rule.
    code,codebook,codeindex = tjs_generate_RC_codebook1(code_dim,reps)
    if code_dim[0]==1:
        for i in range(reps):
            codebook.remove(range(code_dim[1]))
            codeindex.remove(0)
    if code_dim[1]==1:
        for i in range(reps):
            codebook.remove(range(code_dim[0]))
            codeindex.remove(code_dim[0])
    return code,codebook,codeindex
