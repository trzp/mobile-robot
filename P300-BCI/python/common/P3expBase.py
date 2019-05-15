#coding:utf-8
import socket
import random

class CmdLstCtr():				#you should not modify these code
	def __init__(self,CmdLst,Num):
		if len(CmdLst)<Num:	raise EndUserError,'CmdLst definition is not complete!!!'
		self.CmdLst = CmdLst

	def GenTaskList(self,tasknum):
		n = 1+int(tasknum*4/len(self.CmdLst))
		cmdlst = self.CmdLst*n
		tasklist = []
		[tasklist.append(random.choice(cmdlst)) for i in range(tasknum)]
		return tasklist

	def Task2Code(self,task):	# code 0 ineffective
		return self.CmdLst.index(task) + 1

	def Code2Task(self,code):	# code 0 ineffective
		return self.CmdLst[code]

def ClientFunc(client,flag):	#you should not modify this function
	if client.recv(20) == 'complete':
		print 'recv'
		flag[0] = 1

def ClientCreate(addr):			#you should not modity this function
	cl = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	for i in range(10):
		try:
			cl.connect(addr)
		except:
			if i == 9:	raise EndUserError,'connect failed!!!'
		else:		return cl