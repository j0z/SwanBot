#coreutils - Provices tools to add/remove users and perform
#maintenance.

from base_script import Base_Script

COMMANDS = ['adduser','addnode']

def tick(users):
	pass

def get_status_string():
	return 'Blank string'

class Script(Base_Script):
	NAME = ''
	PASSWORD  = ''
	PUBLIC = False
	
	def parse(self):
		args = self.ARGS[:]
		
		if self.STATE == 'running':
			if args[0] == 'adduser':
				if not self.NAME:
					if len(args)==2:
						self.handle_name(args[1])
					else:
						self.get_input(self.handle_name,text='Name: ')
				elif not self.PASSWORD:
					self.get_input(self.handle_password,text='Password: ')
				else:
					self.quit()
					#TODO: Fire event
			
			elif args[0] == 'addnode':
				if not self.NAME:
					if len(args)==2:
						self.handle_name(args[1])
					else:
						self.get_input(self.handle_name,text='What is the name of this node?')
				elif not self.PUBLIC:
					self.get_input(self.handle_public,text='Make this node public? y/n')
				else:
					self.CALLBACK.script_fire_event(self.ID,'finished',True)
	
	def handle_name(self,name):
		#print 'Name set:',name
		self.NAME = name
		
		#self.CALLBACK.send('comm:data:%s:Name was set! Cool!' % self.ID)
	
	def handle_password(self,password):
		#print 'Password set:',password
		self.PASSWORD = password
		
		#self.CALLBACK.send('comm:data:%s:Password was set! Cool!' % self.ID)
	
	def handle_public(self,value):
		if value.lower() in ['true','yes','y']:
			self.PUBLIC = True