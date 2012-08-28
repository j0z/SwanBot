#base_script - Provides a framework for running and storing
#the states of scripts

class Base_Script:
	def __init__(self):
		self.STATE = 'running'
		self.INPUT_CALLBACK = None
	
	def get_input(self,callback):
		self.STATE = 'input'
		self.INPUT_CALLBACK = callback