import threading
import logging
import hashlib
import getpass
import client
import time
import sys

if len(sys.argv)<3:
	print 'Expected: console.py <host> <port>'
	sys.exit(1)

#Setup console logging...
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('[%(asctime)s] %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(console_formatter)
logger.addHandler(ch)

class Console_Thread(threading.Thread):
	RUNNING = False
	CONSOLE = None
	CORE = None
	
	def connected_to_client(self,core):
		logging.info('Connected to core, callback set.')
		self.RUNNING = True
		self.CONSOLE = None
		self.CORE = core
		
		self.start()
	
	def get_text(self,data):
		self.CONSOLE.get_text(data)
	
	def get_data(self,data):
		self.CONSOLE.get_data(data)
	
	def get_input(self,id):
		self.CONSOLE.lock()
		_user_input = self.CONSOLE.get_input()
		
		self.CORE.send('comm:input:%s:%s' % (id,_user_input))
	
	def unlock(self,id):
		self.CONSOLE.unlock()
	
	def run(self):
		self.CONSOLE = Console()
		self.CONSOLE.CALLBACK = self.CORE
		self.CONSOLE.run()

class Console:
	RUN_LEVEL = 0
	CALLBACK = None
	INPUT = ''
	LOCK = False
	
	def get_input(self):
		_line = ''
		
		if self.RUN_LEVEL == 0:
			_line+='#'
		
		try:
			print _line,
			return raw_input().split()
		except EOFError:
			return '\n\n\n'
	
	def lock(self):
		print '**Locked**'
		self.LOCK = True
	
	def unlock(self):
		print '**Unlocked**'
		self.LOCK = False
	
	def get_text(self,text):
		print '=',text
		self.unlock()
	
	def get_data(self,data):
		print '>',data
	
	def run(self):
		time.sleep(0.5)
		
		while self.RUN_LEVEL>-1:
			self.INPUT = self.get_input()
			
			if self.INPUT == '\n\n\n':
				self.RUN_LEVEL = -1
			elif ''.join(self.INPUT) in ['quit','exit']:
				self.CALLBACK.quit()
				self.RUN_LEVEL = -1
			else:
				if not len(self.INPUT):
					continue
				
				self.lock()
				self.CALLBACK.run_command(self.INPUT)
				
				while self.LOCK:
					pass
		else:
			print '\nExiting...'

#print 'Username:',
USER = 'root'#raw_input()

PASSWORD = hashlib.sha224('root').hexdigest()
#hashlib.sha224(getpass.getpass()).hexdigest()

CONSOLE_THREAD = Console_Thread()
client.start(CONSOLE_THREAD,
	sys.argv[1],
	int(sys.argv[2]),
	user=USER,
	password=PASSWORD)