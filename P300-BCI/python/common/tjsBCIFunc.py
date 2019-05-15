#coding:utf-8
from __future__ import division
import time
import os
os.sys.path.append('D:\Python25\Lib')
#from VideoCapture import Device
import threading
import pygame
from VisionEgg.Textures import Texture
import threading,time
from threading import Event
import time
import numpy as np

#=========================================================================
class VideoTexture(threading.Thread):		#定义了摄像头刺激类
	def __init__(self,sti,fre,ev):
		self.cam = Device(0)
		self.sti = sti
		self.fre = fre
		self.ev = ev
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		stp = 1/float(self.fre)
		while True:
			if self.ev.isSet():break
			time.sleep(stp)
			im = self.cam.getImage()
			sur = pygame.image.frombuffer(im.tostring(),(640,480),'RGB')
			self.sti.texture = Texture(sur)

#=========================================================================
# in other modules, we can't reload visualstimuli module.
# so, we write the objects' definition as string and then
# execute this string in the main module.

# lMoniter:行更新监视器。用于在创建一个行更新的文本显示监视器。
# 该监视器定义位置(左对齐)和尺寸后，并赋予待显示的字符串列表，调用
# update方法，能够将显示列表中的字符串一行一行地显示在限定的尺寸内
lMon = r'''
class lMoniter():
	# 监视器的位置，尺寸，颜色，初始字符串列表
	def __init__(self,bci2000,pos,size,color,strlist,layer):
		self.siz = size
		self.bci2000 = bci2000
		self.nm = int(self.siz[0]/(self.siz[1]/2.6))	#当前尺寸下能够容纳的字符数目
		self.dispstrlst = []
		temp = []
		s = -1
		if len(strlist)>0:
			for i in range(len(strlist)):
				s = s+len(strlist[i])+1
				if s<self.nm:	temp.append(strlist[i])
				else:
					self.dispstrlst.append(temp)
					s = 0
					temp = [strlist[i]]
			self.dispstrlst.append(temp)
		n = sum([1 if 'l__mon' in str(i) else 0 for i in self.bci2000.stimuli.values()])
		textstim = VisualStimuli.Text(text = '', position  = pos, anchor = 'left', color = color, font_size = self.siz[1],font_name =r'C:\Windows\Fonts\times.TTF', on = False)
		self.stiName = 'l__mon'+str(n)
		self.bci2000.stimulus(self.stiName, z=layer, stim = textstim)

	def show(self,bl):
		if len(self.dispstrlst)>0:
			temp = self.dispstrlst.pop(0)
			str = ' '.join(temp)
			self.bci2000.stimuli[self.stiName].text = str
			self.bci2000.stimuli[self.stiName].on = bl
			return len(temp)
		else:
			return 0
 
	def update(self,strlist):	#一行一行的更新
		if len(strlist)!=0:
			temp = []
			s = -1
			for i in range(len(llist)):
				if s+len(strlist[i])+1<self.nm:		temp.append(strlist[i])
				else:
					self.dispstrlst.append(temp)
					s = 0
					temp = []
		return self.show(True)
'''

# 使用字符串作为脚本代码运行时注意应当屏蔽转义符(r'.....')，否则可能导致失败

# 定义了逐字显示器。调用update方法能够将指定字符串显示并自动判断是否超出边界，并作出相应操作
wMon = r'''
class wMoniter():
	# 监视器的位置，尺寸，颜色
	def __init__(self,bci2000,pos,size,color,layer):
		self.siz = size
		self.bci2000 = bci2000
		self.nm = int(self.siz[0]/(self.siz[1]/2.6))	#当前尺寸下能够容纳的字符数目
		self.strlst = []
		n = sum([1 if 'w__mon' in str(i) else 0 for i in self.bci2000.stimuli.values()])
		textstim = VisualStimuli.Text(text = '', position  = pos, anchor = 'left', color = color,font_name =r'C:\Windows\Fonts\times.TTF', font_size = self.siz[1], on = False)
		self.stiName = 'w__mon'+str(n)
		self.bci2000.stimulus(self.stiName, z=layer, stim = textstim)

	def update(self,str):
		self.strlst.append(str)
		stri = ' '.join(self.strlst)
		if len(stri)>self.nm:
			self.strlst = [str]
			stri = str
		self.bci2000.stimuli[self.stiName].text = stri
		self.bci2000.stimuli[self.stiName].on = True
'''

#================================================================================
# 定义了定频闪烁刺激
class Asy(threading.Thread):
	def __init__(self,sti,sti_property,values,fre,ev):
		self.stp = 0.5/fre
		self.sti = sti
		self.sti_p = sti_property
		self.values = values
		self.ev = ev
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		exec('self.sti.'+self.sti_p + '= self.values[0]')
		lst = time.clock()
		while True:
			if self.ev.isSet():
				if time.clock() - lst > 0.98*self.stp:
					exec('self.sti.'+self.sti_p + '= self.values[0] if self.sti.' + self.sti_p + '==self.values[1] else self.values[1]')
					lst = lst + self.stp
			else:
				lst = time.clock()
				exec('self.sti.'+self.sti_p + '= self.values[0]')

def SSVEPsti(stilist,propertylist,valueslist,frelist,switch):
	map(lambda sti,pro,values,fre:Asy(sti,pro,values,fre,switch),stilist,propertylist,valueslist,frelist)

#for example
# ev = Event()
# ev.set()		#anywhere call ev.set()/ev.clear() to start/stop stimulus updating
# stilist = [self.stimuli['Flsh1'],self.stimuli['Flsh2'],self.stimuli['Flsh3'],self.stimuli['Flsh4'],]
# propertylist = ['on','color','size','pos']
# valueslist = [(True,False),((1,0,0),(0,1,0)),((100,100),(50,50)),((0,0),(20,20))]
# frelist = [10,11,20,15]
# SSVEPsti(stilist,propertylist,valueslist,frelist,ev)

def tjs_generate_RC_codebook1(cube_dim, reps):
	# 行列交替型闪烁，适用于行列数目相等,并且建议在大于3行3列时使用
	cube = np.arange(np.prod(cube_dim)).reshape(cube_dim)

	codeindex = []
	codebook = []
	for rep in range(reps):
		while True:
			code = []
			coder = np.random.permutation(cube_dim[0])									#行随机
			codec = np.random.permutation(range(cube_dim[0],cube_dim[0]+cube_dim[1]))	#列随机
			map(lambda i,j:code.extend([i,j]),coder,codec)								#行列交替连接,行列数目不等时code里面会放入None
			for i in range(code.count(None)):	code.remove(None)
			try:
				if codeindex[-2]!=code[0] and codeindex[-1]!=code[1]:	break			#保证行和列都不会连续两次重复
			except:
				if rep == 0:	break
				else:pass
		codeindex.extend(code)

	def temdeal(cube,cube_dim,i):
		if i<cube_dim[0]:		return cube[i,].tolist()
		elif i>=cube_dim[0]:	return cube[:,i-cube_dim[0]].tolist()

	map(lambda i:codebook.append(temdeal(cube,cube_dim,i)),codeindex)
	return cube, codebook, codeindex

def tjs_generate_RC_codebook2(cube_dim, reps):
	# 普通型
	cube_size = np.prod(cube_dim)
	cube = np.arange(cube_size).reshape(cube_dim)

	codeindex = []
	codebook = []
	for rep in range(reps):
		while True:
			code = np.random.permutation(cube_size)
			try:
				if codeindex[-1]!=code[0]:	break
			except:
				if rep == 0:	break
				else:pass
		codeindex.extend(code)

	def temdeal(cube,cube_dim,i):
		if i<cube_dim[0]:		return cube[i,].tolist()
		elif i>=cube_dim[0]:	return cube[:,i-cube_dim[0]].tolist()

	map(lambda i:codebook.append(temdeal(cube,cube_dim,i)),codeindex)
	return cube, codebook, codeindex