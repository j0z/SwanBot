#coreutils - Provices tools to add/remove users and perform
#maintenance.

from base_script import Base_Script

COMMANDS = ['adduser']

class Script(Base_Script):
	def parse(self):
		args = self.ARGS[:]
		
		if self.STATE == 'running':
			if args[0] == 'adduser':
				if len(args)==2:
					_name = args[1]
				else:
					self.get_input(self.handle_name)
	
	def handle_name(self,data):
		print 'Yo, got this:',data