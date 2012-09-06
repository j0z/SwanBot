#coreutils - Provices tools to add/remove users and perform
#maintenance.

from base_script import Base_Script

COMMANDS = ['adduser']

def tick():
	print 'Module tick!'

class Script(Base_Script):
	NAME = ''
	PASSWORD  = ''
	
	def parse(self):
		args = self.ARGS[:]
		
		if self.STATE == 'running':
			if args[0] == 'adduser':
				if not self.NAME:
					if len(args)==2:
						self.handle_name(args[1])
					else:
						self.get_input(self.handle_name)
				elif not self.PASSWORD:
					self.get_input(self.handle_password)
				else:
					self.CALLBACK.script_fire_event(self.ID,'finished',True)
	
	def handle_name(self,name):
		#print 'Name set:',name
		self.NAME = name
		
		self.CALLBACK.send('comm:data:%s:Name was set! Cool!' % self.ID)
	
	def handle_password(self,password):
		#print 'Password set:',password
		self.PASSWORD = password
		
		self.CALLBACK.send('comm:data:%s:Password was set! Cool!' % self.ID)