#The core of SwanBot

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import logging
import hashlib
import json
import sys
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('[%(asctime)s] %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(console_formatter)
logger.addHandler(ch)

class SwanBot(LineReceiver):
	chunk_size = 15000
	node_db_start_index = 0
	node_db_end_index = chunk_size
	node_string = ''
	
	def __init__(self):
		self.state = 'connected'
	
	def connectionMade(self):
		self.send(self.factory.motd)
		
		logging.info('Client connected.')
	
	def connectionLost(self,reason):
		logging.info('Client disconnected.')
	
	def send(self,line):
		self.transport.write(line+'\r\n')
	
	def lineReceived(self,line):
		#print line
		
		if self.state == 'connected':
			self.handle_login(line)
			return 0
		
		_args = line.split(':')
		
		if not _args:
			return 0
		
		if _args[0] == 'get':
			if _args[1] == 'nodes':
				self.node_string = json.dumps(self.factory.node_db)
				self.send_nodes(0)
	
	def handle_login(self,line):
		"""NOTE: 'password' must be an md5 hash."""
		try:
			user,password = line.split(':')
		except Exception, e:
			print e
		
		if self.factory.login(user,password):
			self.state = 'identified'
			self.send('login:success')
			
			logging.info('Logged in!')
		else:
			self.send('login:failed')
			
			logging.info('Login failed!')
	
	def send_nodes(self,index):
		self.node_string = self.node_string[self.node_db_start_index:self.node_db_end_index]
		self.node_db_start_index = self.node_db_end_index
		self.node_db_end_index += self.chunk_size
		
		self.send('send:nodes:%s' % self.node_string)
		#self.send('test')

class SwanBotFactory(Factory):
	protocol = SwanBot

	def __init__(self):
		self.motd = 'Welcome to SwanBot!'
		self.users = []
		self.words_db = {'words':[],'nodes':[]}
		self.node_db = []
		
		self.load_users_db()
		self.load_words_db()
	
	def load_users_db(self,error=False):
		try:
			_file = open(os.path.join('data','core_users.json'),'r')
			self.users.extend(json.loads(_file.readline()))
			
			_file.close()
			logging.info('Loaded user database.')
		except Exception, e:
			if error:
				logging.error('Could not create core_users.json!')
				logging.error(e)
				sys.exit(1)
			
			logging.error('Could not load words database from disk!')
			_file = open(os.path.join('data','core_users.json'),'w')
			_file.write(json.dumps(self.users))
			_file.close()
			logging.error('Created words database.')
			self.load_users_db(error=True)
	
	def load_words_db(self,error=False):
		self.words_db = {'words':[],'nodes':[]}
		
		try:
			_file = open(os.path.join('data','words.json'),'r')
			words_db = json.loads(_file.readline())
			
			for entry in self.words_db['words']:
				for key in entry:
					if isinstance(entry[key],unicode):
						entry[key] = entry[key].encode("utf-8")
			
			_file.close()
			self.node_db = words_db['nodes']
			self.words_db = words_db['words']
			logging.info('Loaded words db.')
		except:
			if error:
				logging.error('Could not create words.json!')
				logging.error(e)
				sys.exit(1)
			
			logging.error('Could not load words database from disk!')
			_file = open(os.path.join('data','words.json'),'w')
			_file.write(json.dumps(words_db))
			_file.close()
			logging.error('Created words database.')
			self.load_words_db(error=True)
		
	def save_users_db(self):
		_file = open(os.path.join('data','core_users.json'),'w')
		_file.write(json.dumps(self.users))
		_file.close()
	
	def save_words_db(self):
		_file = open(os.path.join('data','words.json'),'w')
		_file.write(json.dumps({'words':self.words_db,'nodes':self.node_db},ensure_ascii=True))
		_file.close()
	
	def startFactory(self):
		logging.info('SwanBot is up and running.')
	
	def stopFactory(self):
		self.save_users_db()
		self.save_words_db
		
		logging.info('SwanBot is shutting down.')
	
	def login(self,name,password):
		for user in self.users:
			if user['name'] == name and user['password'] == password:
				return True
		
		return False

endpoint = TCP4ServerEndpoint(reactor, 9002)
endpoint.listen(SwanBotFactory())
reactor.run()