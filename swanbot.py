#The core of SwanBot

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import mod_freebase
import logging
import hashlib
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

class SwanBot(LineReceiver):
	chunk_size = 15000
	node_db_start_index = 0
	node_db_end_index = chunk_size
	node_string = ''
	recv_node_string = ''
	scripts = []
	
	def __init__(self):
		self.name = 'Client'
		self.state = 'connected'
	
	def connectionMade(self):
		self.send(self.factory.motd)
		
		logging.info('Client connected.')
	
	def connectionLost(self,reason):
		logging.info('%s disconnected.' % self.name)
	
	def send(self,line):
		self.transport.write(line+'\r\n')
	
	def lineReceived(self,line):
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
			
			elif _args[1] == 'user_value':
				_id = _args[2]
				
				_send_string = json.dumps({'text':self.factory.get_user_value(_args[3],_args[4])})
				
				self.send('send:data:%s:%s' % (_id,_send_string))
			
			elif _args[1] == 'examine_topic':
				_id = _args[2]
				_range = int(_args[3])
				
				_send_string = json.dumps(mod_freebase.examine_topic(':'.join(_args[4:])))
				
				self.send('send:data:%s:%s' % (_id,_send_string[_range:_range+self.chunk_size]))
			
			elif _args[1] == 'research_topic':
				_id = _args[2]
				_range = _args[3]
				
				_send_string = json.dumps(mod_freebase.research_topic(':'.join(_args[4:]),self.factory))
				
				self.send('send:data:%s:%s' % (_id,_send_string))
			
			elif _args[1] == 'expand_nodes':
				_id = _args[2]
				_range = _args[3]
				
				_nodes = json.loads(':'.join(_args[4:]))
				_send_string = json.dumps(mod_freebase.expand_nodes(_nodes,self.factory))
				
				self.send('send:data:%s:%s' % (_id,_send_string))
			
			elif _args[1] == 'nodes_to_string':
				_id = _args[2]
				_range = _args[3]
				
				_nodes = json.loads(':'.join(_args[4:]))
				_send_string = {'text':', '.join([self.factory.node_db[entry]['text'] for entry in _nodes
					if self.factory.node_db[entry]['valuetype'] == 'object'])\
						[:300].encode('utf-8','ignore')}
				
				self.send('send:data:%s:%s' % (_id,json.dumps(_send_string)))
			
			elif _args[1] == 'find_node':
				_id = _args[2]
				_range = _args[3]
				
				_search = ':'.join(_args[4:])
				_send_string = json.dumps({'text':mod_freebase.find_node(_search,self.factory)})
				
				self.send('send:data:%s:%s' % (_id,_send_string))
			
			elif _args[1] == 'show_node':
				_id = _args[2]
				_range = _args[3]
				
				_index = int(_args[4])
				_send_string = json.dumps({'text':mod_freebase.show_node(_index,self.factory)})
				
				self.send('send:data:%s:%s' % (_id,_send_string))
		
		elif _args[0] == 'send':
			if _args[1] == 'start-node':
				self.recv_node_string = ''
			
			elif _args[1] == 'nodes':
				self.recv_node_string += ':'.join(_args[2:])
				
				try:
					_node_db = json.loads(self.recv_node_string)
					
					self.factory.node_db = _node_db
					logging.info('node_db was uploaded!')
				except:
					logging.info('Downloading chunk: %s' % len(self.recv_node_string))
			
			elif _args[1] == 'user_value':
				_id = _args[2]
				
				_send_string = json.dumps(self.factory.set_user_value(_args[3],_args[4],
					':'.join(_args[5:])))
				
				self.send('send:data:%s:%s' % (_id,_send_string))
		
		elif _args[0] == 'comm':
			self.handle_command(_args[2:],_args[1])
	
	def handle_command(self,args,id):
		_matches = []
		_return = []
		
		if args[0] == 'loadmod' and len(args)==2:
			try:
				_mod_name = args[1]
				
				if not _mod_name.count('py'):
					_mod_name = _mod_name+'.py'
				
				TEMP_MOD = imp.load_source(args[1].replace('.py',''),\
					os.path.join('modules',_mod_name))
				#exec('import %s as TEMP_MOD' % args[1])
				if self.add_module(args[1],TEMP_MOD):
					logging.info('Loaded module: %s' % args[1])
					self.send('comm:data:%s:\'%s\' loaded.' % (id,args[1]))
					
					return True
				else:
					logging.error('Module already loaded: %s' % args[1])
					self.send('comm:data:%s:\'%s\' already loaded.' % (id,args[1]))
					
					return True
			except Exception, e:
				logging.error('Failed to import mod \'%s\'' % args[1])
				logging.error(e)
				
				self.send('comm:data:%s:%s' % (id,e))
				
				return False
			
		for module in self.factory.modules:
			if args[0] in module['module'].COMMANDS:
				_matches.append(module)
		
		if len(_matches)==1:
			_script_id = self.create_script(_matches[0],args)
			
			#TODO: Client needs to log this!
			#self.send('comm:id:%s:%s' % (id,_script_id))
			
			self.run_script(_script_id)
			
		elif len(_matches)>1:
			_matches_string = '\t'.join([entry['name'] for entry in _matches])
			self.send('comm:data:%s:%s' % (id,_matches_string))
		
		else:
			self.send('comm:data:%s:%s' % (id,'Nothing!'))
	
	def handle_login(self,line):
		"""NOTE: 'password' must be a sha224 hash."""
		try:
			user,password = line.split(':')
		except Exception, e:
			print e
		
		if self.factory.login(user,password):
			self.state = 'identified'
			self.send('login:success')
			
			logging.info('%s logged in.' % user)
			self.name = user
		else:
			self.send('login:failed')
			
			logging.info('Login failed!')
	
	def send_nodes(self,index):
		self.node_string = self.node_string[self.node_db_start_index:self.node_db_end_index]
		self.node_db_start_index = self.node_db_end_index
		self.node_db_end_index += self.chunk_size
		
		self.send('send:nodes:%s' % self.node_string)
	
	def add_module(self,name,module):
		#Sanitize input to prevent duplicates
		name = name.replace('mod_','').replace('.py','')
		
		if name in [mod['name'] for mod in self.factory.modules]:
			return 0
		
		self.factory.modules.append({'name':name,'module':module})
		
		return 1
	
	def create_script(self,module,args):
		_script = {'script':module['module'].Script(args,self),
			'id':len(self.scripts)+1}
		
		_script['script'].id = _script['id']
		
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
			
			try:
				os.mkdir('data')
			except:
				pass
			
			_file = open(os.path.join('data','core_users.json'),'w')
			
			if '--init' in sys.argv:
				self.users = [{'name':'root',
					'password':'871ce144069ea0816545f52f09cd135d1182262c3b235808fa5a3281'}]
				
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
		except:
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
	
	def stopFactory(self):
		self.save_users_db()
		self.save_words_db
		
		logging.info('SwanBot is shutting down.')
	
	def login(self,name,password):
		for user in self.users:
			if user['name'] == name and user['password'] == password:
				return True
		
		return False
	
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

endpoint = TCP4ServerEndpoint(reactor, 9002)
endpoint.listen(SwanBotFactory())
reactor.run()