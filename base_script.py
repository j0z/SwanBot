#base_script - Provides a framework for running and storing
#the states of scripts

class Base_Script:
	def __init__(self,args,callback,id):
		self.STATE = 'running'
		self.INPUT_CALLBACK = None
		self.CALLBACK = callback
		self.ARGS = args
		self.ID = id
	
	def get_input(self,callback):
		self.STATE = 'input'
		self.INPUT_CALLBACK = callback
		
		self.CALLBACK.send('comm:get:')