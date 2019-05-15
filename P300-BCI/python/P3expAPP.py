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
import numpy as np

class BciApplication(BciGenericApplication):

    def Description(self):
        return 'p3 experiment'

    def Construct(self):
        self.define_param(
            # you should not modify these codes
            "PythonApp:ExpCtr             int         ExpMode=                 0 % % % //0-offline trainning, 1-online trainning, 2-free mode",
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
        )

    def Preflight(self, sigprops):    # you should not modity this function
        #参数初始化
        self.cube_dim = map(int,self.params['cube_dim'])                        #编码信息
        self.NumberOfSequences = int(self.params['NumberOfSequences'])            #重复刺激次数
        self.tasknum = int(self.params['NumberOfTasks'])
        self.nextoutseq = False                                                    #用来指示是否为当前sequences的最后一次闪烁
        self.ExpMode = int(self.params['ExpMode'])                                #实验模式控制
        self.ResultTask = ''
        #屏幕初始化
        if self.ExpMode <2:
            frameless = not bool(int(self.params['Debug']))                            #设置debug模式，可以通过窗口关闭程序
            siz = float(self.params['ScreenSiz'])
            screenid = int(self.params['ScreenId'])                                    #ScreenId 0 is the first screen, 1 the second, -1 the last
            fullscreen(scale=siz, id=screenid, frameless_window=frameless)
        else:
            fullscreen(scale=0.3, id=0, frameless_window=frameless)

    def Initialize(self, indim, outdim):    # you should not modity this function
        self.CmdLst = [str(i) for i in range(1,7)]
        self.cmd = P3expBase.CmdLstCtr(self.CmdLst,self.cube_dim[0]*self.cube_dim[1])    #用来控制任务序列生成等操作
        self.tasklist = self.cmd.GenTaskList(self.tasknum)                            #随机产生任务序列

        self.EXP_setup()                                                            #刺激界面界面设置，依据具体范式来进行修改
        self.necessary_setup(self.ExpMode)                                            #必要的设置，无需特别修改

    def StartRun(self):        # you should not modity this function
        self.states['StimulusType'] = 0
        self.states['StimulusCode'] = 0
        self.states['PhaseInSequence'] = 0

    def Phases(self):    # you should not modity this function
        self.phase(name='ready',                     next='presequences',         duration=2000)
        self.phase(name='presequences',         next='sequences',             duration=int(self.params['PreSequenceDuration']))    
        self.phase(name='sequences',             next='postsequences',         duration=int(self.params['StimulusDuration']))
        self.phase(name='postsequences',         next='sequences',             duration=int(self.params['ISIDuration']))
        self.phase(name='resdisp',                 next='presequences',         duration=2500)
        self.phase(name='stop',                    duration=5000)

        if self.nextoutseq and self.in_phase('sequences'):
            self.phase(name='postsequences',     next='resdisp',             duration=2000 - int(self.params['ISIDuration'])-int(self.params['StimulusDuration']))

        if self.in_phase('postsequences') and len(self.tasklist) < 1 and self.nextoutseq:
            self.phase(name='resdisp',     next='stop',     duration=4000)
        self.design(start='ready', new_trial='presequences', interblock='idle')

    def Transition(self, phase):    # you should not modity this function
        if phase == 'ready':
            self.stimuli['Info'].text = 'Ready!'
            self.stimuli['Info'].on = True

        elif phase == 'presequences':
            self.ResDisplay = False
            self.stimuli['Info'].on = False
            self.nextoutseq = False
            self.states['StimulusCode'] = 0
            self.states['StimulusType'] = 0
            self.states['PhaseInSequence'] = 1

            self.code,self.codebook,self.codeindex = CodeGen(self.cube_dim,self.NumberOfSequences)        #产生刺激序列
            if self.ExpMode<2:
                self.currenttask = self.tasklist.pop(0)
                self.cur_taskcode = self.cmd.Task2Code(self.currenttask)
                self.Task_prompt(1)

        elif phase == 'sequences':
            self.states['PhaseInSequence'] = 2
            self.states['StimulusCode'] = self.codeindex.pop(0)+1
            self.cur_codebook = self.codebook.pop(0)
            if self.ExpMode<2:
                if self.cur_taskcode-1 in self.cur_codebook:    self.states['StimulusType'] = 1
                else:                                            self.states['StimulusType'] = 0
            else:pass
            [StimulusAct(self.stimuli['Flsh'+str(1+item)],1) for item in self.cur_codebook]

        elif phase == 'postsequences':
            self.states['StimulusCode'] = 0
            if len(self.codeindex) < 2:    self.nextoutseq = True
            [StimulusAct(self.stimuli['Flsh'+str(1+item)],0) for item in self.cur_codebook]
            # [StimulusAct(self.stimuli['cmd'+str(1+item)],(1,1,1)) for item in self.cur_codebook]

        elif phase == 'resdisp':
            if self.ExpMode<2:
                self.Task_prompt(0)
            self.states['PhaseInSequence'] = 3
            self.ResultTask = ''

        elif phase == 'stop':
            self.states['StimulusCode'] = 0
            self.states['StimulusType'] = 0
            self.stimuli['Info'].text = 'End'
            self.stimuli['Info'].on = True
        
        else:
            pass

    def Process(self, sig):        # you should not modity this function
        res = sig[0].astype(np.int32)
        if self.in_phase('resdisp') and res[0,0]>-1:
            self.ResultTask = str(res[0,-1]+1)
            if not self.ResDisplay:
                if self.stimuli['rescue'].text == '':
                    self.stimuli['rescue'].text = self.ResultTask
                else:
                    self.stimuli['rescue'].text = self.stimuli['rescue'].text + '  ' + self.ResultTask
                self.ResDisplay = True


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


    ################################################################################################################################
    # realize this function
    def EXP_setup(self):
        # 定义界面布局
        scrw,scrh = self.screen.size
        center = [scrw/2,scrh/2]
        #scrh = scrh - 80                # task, result 显示区占用了一部分。
        hunit = int(scrh/12)
        wunit = int(scrw/13)
        #hpos = [11*hunit,9*hunit,7*hunit,5*hunit,3*hunit,1*hunit]
        hpos = [scrh/2]
        wpos = [1.5*wunit,3.5*wunit,5.5*wunit,7.5*wunit,9.5*wunit,11.5*wunit]
        self.pos_sti = [(x,y) for y in hpos for x in wpos]
        unit = int(min(hunit,wunit))

        # 生成并注册刺激
        for i in range(6):
            # 定义命令提示刺激，it's all to yourself
            textstim = VisualStimuli.Text(text = str(i+1), position  = self.pos_sti[i], anchor = 'center', color = (1,0,1), font_name =r'C:\Windows\Fonts\Arial.TTF',font_size = int(1.2*unit), on = True)
            self.stimulus('cmd'+str(i+1),z = 1,stim = textstim)

            # 定义刺激Flsh的形状, it's all to yourself
            b = box(left=-1,right=1,bottom=-1,top=1,size = (int(1.5*unit),int(1.5*unit)), position = self.pos_sti[i], sticky=True)
            tempShape = PolygonTexture(frame=b,
                                        vertices=((0,0.66),
                                                    (0.33,0.66),
                                                    (0.33,1),
                                                    (0.66,1),
                                                    (0.66,0.66),
                                                    (1,0.66),
                                                    (1,0.33),
                                                    (0.66,0.33),
                                                    (0.66,0),
                                                    (0.33,0),
                                                    (0.33,0.33),
                                                    (0,0.33)),
                                        color=(1,1,0),
                                        anchor='center',
                                        position = self.pos_sti[i],
                                        on=False)
            # 约定将闪烁刺激注册为Flsh1,Flsh2...
            self.stimulus('Flsh'+str(i+1),z = 2,stim = tempShape)

    def Task_prompt(self,flag):        #you should not modify this function
        if flag:
            self.stimuli['cmd'+str(self.cur_taskcode)].color = (1,1,1)
        else:
            self.stimuli['cmd'+str(self.cur_taskcode)].color = (1,0,1)



################################################################################################
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

def StimulusAct(stim,prm):        # realize this function.
    try:    stim.on = prm        # for example: stim.size = prm
    except:    pass
# def StimulusAct(stim,prm):        # realize this function.
    # try:    stim.color = prm        # for example: stim.size = prm
    # except:    pass
################################################################################################
