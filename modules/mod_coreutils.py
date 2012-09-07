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
	TYPE = ''
	PASSWORD  = ''
	PUBLIC = -1
	
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
				if not self.TYPE:
					if len(args)==2:
						self.handle_name(args[1])
					else:
						self.get_input(self.handle_type,text='What is the type of this node?')
				elif self.PUBLIC == -1:
					self.get_input(self.handle_public,text='Make this node public? y/n')
				else:
					_node_string = 'Created node \'%s\'...\nPublic:\t%s'\
						% (self.TYPE,self.PUBLIC)
					self.CALLBACK.send('comm:data:%s:%s' % (self.ID,_node_string))
					self.CALLBACK.create_node(self.TYPE,self.PUBLIC)
					self.quit()
	
	def handle_name(self,name):
		self.NAME = str(name[0])
		
		self.CALLBACK.send('comm:data:%s:\\OK' % self.ID)
	
	def handle_type(self,type):
		self.TYPE = str(type[0])
		
		self.CALLBACK.send('comm:data:%s:\\OK' % self.ID)
	
	def handle_password(self,password):
		self.PASSWORD = password
		
		self.CALLBACK.send('comm:data:%s:\\OK' % self.ID)
	
	def handle_public(self,value):
		if value[0].lower() in ['true','yes','y']:
			self.PUBLIC = True
		else:
			self.PUBLIC = False
		
		self.CALLBACK.send('comm:data:%s:\\OK' % self.ID)