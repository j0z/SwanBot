#The core of SwanBot

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import threading
import logging
import nodes
import time
import json
import sys
import imp
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('[%(asctime)s] %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(console_formatter)
logger.addHandler(ch)

class ModuleThread(threading.Thread):
	RUNNING = True
	CALLBACK = None
	
	def start(self,callback):
		self.CALLBACK = callback
		self.RUNNING = True
		
		threading.Thread.start(self)
	
	def stop(self):
		if not self.CALLBACK:
			logging.error('Module thread: No callback set.')
			
			return False
		
		self.RUNNING = False
	
	def run(self):		
		if not self.CALLBACK:
			logging.error('Module thread: No callback set.')
			
			return False
		
		logging.info('Module thread: Running.')
		
		while self.RUNNING:
			self.CALLBACK.tick_modules()
			
			time.sleep(1)
		
		logging.info('Module thread: Shut down.')

class SwanBot(LineReceiver):
	scripts = []
	
	def __init__(self):
		self.name = 'Client'
		self.client_name = 'Unknown'
		self.factory = None

	def connectionMade(self):
		self.client_host = self.transport.getPeer().host
		self.client_port = self.transport.getPeer().port
		
		logging.info('Client (%s:%s) connected.' % (self.client_host,self.client_port))
	
	def connectionLost(self,reason):		
		self.factory.delete_client(self.client_name,self.transport,self.name)
		
		logging.info('%s via %s (%s:%s) disconnected.' %
			(self.name,self.client_name,self.client_host,self.client_port))
	
	def send(self,line):
		self.transport.write(line+'\r\n')
	
	def lineReceived(self,line):
		_args = line.split(':')
		_commands = json.loads(':'.join(_args[1:]))
		
		if not _args:
			return 0
		
		if _args[0] == 'api-get':
			_api_key = _commands['apikey']
			self.client_name = 'API'

			if _commands['param'] == 'user_value':
				_user = _commands['user']
				_value = _commands['value']
				
				_send_string = json.dumps({'text':self.factory.get_user_value(_user,_value)})
				
				self.send(_send_string)
			else:
				self.send(json.dumps({'text':'No matching command.'}))
		
		elif _args[0] == 'api-send':
			_api_key = _commands['apikey']
			self.client_name = 'API'

			if _args[1] == 'user_value':
				_id = _args[2]
				
				_send_string = json.dumps(self.factory.set_user_value(_args[3],_args[4],
					':'.join(_args[5:])))
				
				self.send('send:data:%s:%s' % (_id,_send_string))
		
		elif _args[0] == 'event':
			if len(_args)<3:
				logging.info('Threw out event: %s' % line)
				return False
				
			self.create_event(_args[1],':'.join(_args[2:]))
	
	def handle_command(self,args,id):
		#Leaving this in for now. Might adapt some of it for later use.
		_matches = []
		_return = []
		
		if args[0] == 'loadmod' and len(args)==2:
			try:				
				if self.factory.add_module(args[1]):
					logging.info('Loaded module: %s' % args[1])
					self.send('comm:text:%s:\'%s\' loaded.' % (id,args[1]))
					
					return True
				else:
					logging.error('Module already loaded: %s' % args[1])
					self.send('comm:text:%s:\'%s\' already loaded.' % (id,args[1]))
					
					return True
			except Exception, e:
				logging.error('Failed to import mod \'%s\'' % args[1])
				logging.error(e)
				
				self.send('comm:data:%s:%s' % (id,e))
				
				return False
		
		elif args[0] == 'delmod':
			if len(args)==2:
				_mod_name = args[1]
				
				if self.factory.remove_module(_mod_name):
					logging.info('Unloaded module: %s' % args[1])
					self.send('comm:text:%s:\'%s\' unloaded.' % (id,args[1]))
				else:
					logging.error('Module is not loaded: %s' % args[1])
					self.send('comm:text:%s:\'%s\' is not loaded.' % (id,args[1]))
					return False
			
			else:
				self.send('comm:text:%s:Usage: delmod <mod>' % (id))
				
				return False
			
			return True	
			
		for module in self.factory.modules:
			if args[0] in module['module'].COMMANDS:
				_matches.append(module)
				continue
		
		if len(_matches)==1:
			_script_id = self.create_script(_matches[0],args)
			
			#TODO: Client needs to log this!
			#self.send('comm:id:%s:%s' % (id,_script_id))
			
			self.run_script(_script_id)
			
		elif len(_matches)>1:
			_matches_string = '\t'.join([entry['name'] for entry in _matches])
			self.send('comm:text:%s:%s' % (id,_matches_string))
		
		else:
			self.send('comm:text:%s:%s' % (id,'Nothing!'))
	
	def handle_script_input(self,args,id):	
		for script in self.scripts:
			if script['id'] == id:
				script['script'].send_input(args)
	
	def handle_login(self,line):
		"""NOTE: 'password' must be a sha224 hash."""
		try:
			user,password,client_name = line.split(':')
		except Exception, e:
			print e
			return False
		
		if self.factory.login(user,password):
			logging.info('%s (%s:%s) -> %s' % (self.name,self.client_host,self.client_port,user))
			self.name = user
			self.state = 'identified'
			self.send('login:success')
			
			self.client_name = client_name
			
			if not self.factory.create_client(client_name,self.transport,user):
				self.send('login:failed')
				
				return False
			
			logging.info('%s logged in.' % user)
		else:
			self.send('login:failed')
			
			logging.info('Login failed!')

	def create_node(self,type,public):
		self.factory.create_node(self.name,type,public)
	
	def create_event(self,type,value):
		"""Creates and broadcasts event of type 'type' with value 'value'"""
		logging.info('Event created: %s - %s' % (type,value))
		
		self.factory.broadcast_event(type,value,self.name)
	
	def create_script(self,module,args):
		_script_id = len(self.scripts)+1
		_script = {'script':module['module'].Script(args,self,_script_id),
			'id':_script_id}
		
		self.scripts.append(_script)
		logging.info('Created script with id #%s' % _script['id'])
		
		return _script['id']
	
	def run_script(self,id):
		for script in self.scripts:
			if script['id'] == id:
				script['script'].parse()

class SwanBotFactory(Factory):
	protocol = SwanBot
	modules = []
	clients = []

	def __init__(self):
		self.users = []
		self.words_db = {'words':[],'nodes':[]}
		self.node_db = []
		
		self.load_users_db()
		self.load_words_db()
	
	def load_users_db(self,error=False):
		try:
			_file = open(os.path.join('data','core_users.json'),'r')
			self.users = json.loads(_file.readline())
			
			#Set the current highest node ID
			for user in self.users:
				for node in user['nodes']:
					if node['id']>nodes.NODE_ID:
						nodes.NODE_ID = node['id']
			
			_file.close()
			logging.info('Loaded user database.')
		except Exception, e:
			if error:
				logging.error('Could not create core_users.json!')
				logging.error(e)
				sys.exit(1)
			
			logging.error('Could not load words database from disk!')
			
			try:
				os.mkdir('data')
			except:
				pass
			
			_file = open(os.path.join('data','core_users.json'),'w')
			
			if '--init' in sys.argv:
				self.users = [{'name':'root',
					'password':'871ce144069ea0816545f52f09cd135d1182262c3b235808fa5a3281',
					'nodes':[]}]
				
				logging.info('Creating new user DB...')
			
			_file.write(json.dumps(self.users))
			_file.close()
			logging.info('Created words database.')
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
		except Exception, e:
			if error:
				logging.error('Could not create words.json!')
				logging.error(e)
				sys.exit(1)
			
			logging.error('Could not load words database from disk!')
			_file = open(os.path.join('data','words.json'),'w')
			_file.write(json.dumps(self.words_db))
			_file.close()
			logging.info('Created words database.')
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
		
		self.add_module('mod_coreutils')
		
		self.module_thread = ModuleThread()
		self.module_thread.start(self)
	
	def stopFactory(self):
		self.save_users_db()
		self.save_words_db()
		
		logging.info('SwanBot is shutting down.')
		self.module_thread.stop()
	
	def tick_modules(self):
		_public_nodes = self.get_public_user_nodes()
		
		for module in self.modules:
			try:
				module['module'].tick(_public_nodes)
			except Exception, e:
				print e
	
	def login(self,name,password):
		for user in self.users:
			if user['name'] == name and user['password'] == password:
				return True
		
		return False
	
	def create_client(self,client_name,transport,user):
		_host = transport.getPeer().host
		_port = transport.getPeer().port
		
		for client in self.clients:
			_client_host = client['transport'].getPeer().host
			_client_port = client['transport'].getPeer().port
			
			if client['client_name'] == client_name and _client_host == _host and\
				_client_port == _port and client['user'] == user:
				
				logging.info('%s via %s (%s:%s) failed to log in due to a duplicate connection.'
					% (user,client_name,_host,_port))
				return False
		
		self.clients.append({'client_name':client_name,
			'transport':transport,'user':user})
		
		logging.info('%s connected via \'%s\' (%s:%s)' % (user,client_name,_host,_port))
		return True
	
	def delete_client(self,client_name,transport,user):
		_host = transport.getPeer().host
		_port = transport.getPeer().port
		
		for client in self.clients:
			_client_host = client['transport'].getPeer().host
			_client_port = client['transport'].getPeer().port
			
			if client['client_name'] == client_name and _client_host == _host and\
				_client_port == _port and client['user'] == user:
				self.clients.remove(client)
				
				return True
		
		logging.error('Could not find matching client: %s via %s (%s:%s)'
			% (user,client_name,_host,_port))
		
		return False
	
	def broadcast_event(self,type,value,user):
		_event = 'event:%s:%s' % (type,value)
		
		for client in self.clients:
			if client['user'] == user:
				_client_host = client['transport'].getPeer().host
				_client_port = client['transport'].getPeer().port
				client['transport'].write(_event+'\r\n')
				
				logging.info('Event sent to (%s:%s)!' % (_client_host,_client_port))
	
	def create_node(self,username,type,public):
		for user in self.users:
			if user['name'] == username:
				_node = nodes.create_node()
				_node['owner'] = username
				_node['type'] = type
				_node['public'] = public
				
				user['nodes'].append(_node)
				logging.info('Created node with ID #%s' % _node['id'])
	
	def get_public_user_nodes(self):
		_public_user_nodes = []
		
		for user in self.users:
			_nodes = []
			
			for node in user['nodes']:
				if node['public']:
					_nodes.append(node)
			
			_public_user_nodes.append({'name':user['name'],'nodes':_nodes})
		
		return _public_user_nodes
	
	def get_user_value(self,name,value):
		for user in self.users:
			if user['name'] == name:
				try:
					return user[value]
				except:
					logging.error('User %s has no value \'%s\'' % (name,value))
					return None
	
	def set_user_value(self,name,value,to):
		for user in self.users:
			if user['name'] == name:
				user[value] = to
				
				return user[value]
	
	def add_module(self,name):
		#Sanitize input to prevent duplicates
		_sanitized_name = name.replace('mod_','').replace('.py','')
		
		if _sanitized_name in [mod['name'] for mod in self.modules]:
			return 0
		
		_mod_name = name
				
		if not _mod_name.count('py'):
			_mod_name = _mod_name+'.py'

		_module = imp.load_source(name.replace('.py',''),
			os.path.join('modules',_mod_name))
		
		self.modules.append({'name':_sanitized_name,'module':_module})
		
		return 1
	
	def remove_module(self,name):
		name = name.replace('mod_','').replace('.py','')
		
		for mod in self.modules:
			if mod['name'] == name:
				self.modules.remove(mod)
				return 1
		
		return 0

endpoint = TCP4ServerEndpoint(reactor, 9002)
endpoint.listen(SwanBotFactory())
reactor.run()