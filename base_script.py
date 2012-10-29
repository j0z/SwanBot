#base_script - Provides a framework for running and storing
#the states of scripts
import json

class Base_Script:
	def __init__(self,args,callback,id):
		self.STATE = 'running'
		self.INPUT_CALLBACK = None
		self.CALLBACK = callback
		self.ARGS = args
		self.ID = id
	
	def get_input(self,callback,text=''):
		self.STATE = 'input'
		self.INPUT_CALLBACK = callback
		
		if text:
			self.CALLBACK.send('comm:data:%s:%s' % (self.ID,text))
		
		self.CALLBACK.send('comm:input:%s' % self.ID)
	
	def send_input(self,user_input):
		self.STATE = 'running'
		self.INPUT_CALLBACK(json.loads(user_input))
		
		self.INPUT_CALLBACK = None
	
	def quit(self):
		self.STATE = 'finished'
		self.CALLBACK.send('comm:term:%s' % self.ID)