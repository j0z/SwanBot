#The core of SwanBot

try:
	from twisted.internet.endpoints import TCP4ServerEndpoint
	from twisted.internet.protocol import Factory
	from twisted.protocols.basic import LineReceiver
	from twisted.internet import reactor
except:
	print 'Twisted could not be found.'

import threading
import logging
import nodes
import time
import json
import sys
import imp
import os

try:
	import pygeoip
except:
	print 'PyGeoIP not installed.'

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

#noinspection PyMethodOverriding
class SwanBot(LineReceiver):
	scripts = []
	
	def __init__(self):
		self.name = 'Client'
		self.client_name = 'Unknown' #TODO: Naming conflict with self.name
		self.user = None
		self.factory = None

	def connectionMade(self):
		self.client_host = self.transport.getPeer().host
		self.client_port = self.transport.getPeer().port

		print self.factory.get_country_name_from_ip(self.client_host)

		logging.info('Client (%s:%s) connected.' % (self.client_host,self.client_port))
	
	def connectionLost(self,reason):
		if not self.client_name == 'API':
			self.factory.delete_client(self.client_name,self.transport,self.name)
		
		logging.info('%s via %s (%s:%s) disconnected.' %
			(self.name,self.client_name,self.client_host,self.client_port))
	
	def send(self,line):
		self.transport.write(line+'\r\n')
	
	def lineReceived(self,line):
		_args = line.split(':')
		
		if not _args:
			return 0
		
		if _args[0] == 'api-get':
			self.client_name = 'API'
			_payload = json.loads(':'.join(_args[1:]))
			self.api_key = self.get_api_key_from_payload(_payload)

			if self.auth_user_via_api_key(self.api_key):
				self.handle_api_get(_payload)
		
		elif _args[0] == 'api-send':
			self.client_name = 'API'
			_payload = json.loads(':'.join(_args[1:]))
			self.api_key = self.get_api_key_from_payload(_payload)

			if self.auth_user_via_api_key(self.api_key):
				self.handle_api_send(_payload)
				self.update_user_node_mesh()
		
		elif _args[0] == 'event':
			if len(_args)<3:
				logging.info('Threw out event: %s' % line)
				
			self.create_event(_args[1],':'.join(_args[2:]))

	def handle_api_get(self,payload):
		_send_string = {'text':'No matching command.'}

		if payload['param'] == 'user_value':
			_user = payload['user']
			_value = payload['value']
			_send_string = {'text':self.factory.get_user_value(_user,_value)}

		elif payload['param'] == 'find_node':
			_send_string = self.handle_find_nodes(payload['query'])

		self.send(json.dumps(_send_string))
		return True

	def handle_api_send(self,payload):
		_send_string = {'text':'No matching command.'}

		if payload['param'] == 'create_node':
			if payload.has_key('query'):
				_send_string = self.create_node_from_payload(payload['query'])
			else:
				_send_string = {'error':'No \'query\' key passed to create_node.'}

		self.send(json.dumps(_send_string))
		return True

	def handle_command(self,args,id):
		#Leaving this in for now. Might adapt some of it for later use.
		_matches = []
		
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

	def handle_missing_api_key(self):
		logging.error('Incorrect API key from %s:%s' % (self.client_host,self.client_port))
		self.send(json.dumps({'text':'No API key found in dictionary.'}))
	
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

	def auth_user_via_api_key(self,api_key):
		for user in self.factory.users:
			if user['api-key'] == api_key:
				logging.info('%s -> %s' % (self.name,user['name']))
				self.name = user['name']
				self.user = user
				return True

		logging.error('Incorrect API key from %s:%s' % (self.client_host,self.client_port))
		self.send(json.dumps({'text':'No user with that API key exists.'}))

		return False

	def get_api_key_from_payload(self,payload):
		if not payload.has_key('apikey'):
			return False

		return payload['apikey']

	def create_node_from_payload(self,payload):
		_node = nodes.create_node()
		_node['owner'] = self.user['name']

		for key in payload:
			_node[key] = payload[key]

		if payload.has_key('parent') and payload['parent']:
			_parent_nodes = self.find_nodes(payload['parent'])

			for parent_node in _parent_nodes:
				logging.info('Found parent!')
				_retrieved_node = self.retrieve_node_via_id(parent_node)
				self.add_child_to_node(_retrieved_node,_node)

			del _node['parent']

		self.user['nodes'].append(_node)
		logging.info('Created node with ID #%s' % _node['id'])

		self.filter_nodes()

		return _node

	def create_node(self,type,public):
		self.factory.create_node(self.name,type,public)

	def add_child_to_node(self,parent,child):
		if not parent['id'] in child['parents']:
			child['parents'].append(parent['id'])

		if not child['id'] in parent['children']:
			parent['children'].append(child['id'])

		return True

	def filter_nodes(self):
		for node1 in self.user['nodes']:
			for node2 in self.user['nodes']:
				if node1['id'] == node2['id'] or not node1['filter']:
					continue

				_nodes_connected = False
				_found = True

				for key in node1['filter']:
					if not node2.has_key(key) or not node2[key] == node1['filter'][key]:
						_found = False
						break

				if not _found:
					continue

				if not node1['id'] in node2['parents']:
					node2['parents'].append(node1['id'])
					_nodes_connected = True

				if not node2['id'] in node1['children']:
					node1['children'].append(node2['id'])
					_nodes_connected = True

				if _nodes_connected:
					logging.info('Synapse: Node #%s -> Node #%s' % (node2['id'],node1['id']))

	def handle_find_nodes(self,query):
		_found_nodes = self.find_nodes(query)

		if _found_nodes:
			return {'results':_found_nodes}
		else:
			return {'error':'No nodes were found.'}

	def find_nodes(self,query):
		_matching_nodes = []

		for node in self.user['nodes']:
			_found = True

			for key in query:
				if node.has_key(key) and node[key] == query[key]:
					pass
				else:
					_found = False
					break

			if not _found:
				continue

			_matching_nodes.append(node['id'])

		logging.info('Found %s matching nodes.' % len(_matching_nodes))

		return _matching_nodes

	def retrieve_node_via_id(self,id):
		for node in self.user['nodes']:
			if node['id'] == id:
				return node

		return None

	def update_user_node_mesh(self):
		logging.info('Debugging...')
		self.filter_nodes()
		self.factory.save_users_db()

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
	geoip = None

	def __init__(self):
		self.users = []
		self.words_db = {'words':[],'nodes':[]}
		self.node_db = []
		
		self.load_users_db()
		self.load_words_db()
		self.load_geoip_db()
	
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
				    'api-key':'testkey',
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

	def load_geoip_db(self):
		try:
			self.geoip = pygeoip.GeoIP(os.path.join('data','GeoIP.dat'))
			logging.info('Loaded GeoIP database.')
		except NameError:
			pass
		except Exception, e:
			logging.error('Could not locate GeoIP database.')
			print e

	def is_geoip_loaded(self):
		return self.geoip

	def get_country_name_from_ip(self,ip):
		_ip_info = self.geoip.country_name_by_addr(ip)

		if _ip_info:
			return _ip_info
		else:
			logging.warning('Could not find location for \'%s\'' % ip)
			return None

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