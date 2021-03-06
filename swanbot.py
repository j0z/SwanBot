#The core of SwanBot

import threading
import logging
import hashlib
import speech
import nodes
import time
import json
import sys
import imp
import os
import re

try:
	from twisted.internet.endpoints import TCP4ServerEndpoint
	from twisted.internet.protocol import Factory
	from twisted.protocols.basic import LineReceiver
	from twisted.internet import reactor
except Exception, e:
	print 'Error importing Twisted:',e
	sys.exit()

try:
	import pygeoip
except:
	print 'PyGeoIP not installed.'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('[%(asctime)s] %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(console_formatter)
logger.addHandler(ch)

#noinspection PyMethodOverriding
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
	def __init__(self):
		self.name = 'Client'
		self.client_name = 'Unknown' #TODO: Naming conflict with self.name
		self.user = None
		self.factory = None

	def connectionMade(self):
		self.client_host = self.transport.getPeer().host
		self.client_port = self.transport.getPeer().port

		_location = self.factory.get_country_name_from_ip(self.client_host)

		logging.debug('Client (%s:%s) connected from %s' %
		             (self.client_host,self.client_port,_location))
	
	def connectionLost(self,reason):
		if not self.client_name == 'API':
			self.factory.delete_client(self.client_name,self.transport,self.name)
		
		logging.debug('%s via %s (%s:%s) disconnected.' %
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

		elif payload['param'] == 'find_nodes':
			_send_string = self.handle_find_nodes(payload['query'])

		elif payload['param'] == 'get_nodes':
			_send_string = self.handle_get_nodes(payload['nodes'])

		self.send(json.dumps(_send_string))
		return True

	def handle_api_send(self,payload):
		_send_string = {'text':'No matching command.'}

		if payload['param'] == 'create_node':
			if payload.has_key('query'):
				if payload['query']['type'] == 'fetch':
					_node = self.create_node_from_payload(payload['query'])
					_send_string = self.handle_fetch_node(_node)
				else:
					_send_string = self.create_node_from_payload(payload['query'])
			else:
				_send_string = {'error':'No \'query\' key passed to create_node.'}

		elif payload['param'] == 'delete_nodes':
			if payload.has_key('nodes'):
				_send_string = self.delete_nodes_from_payload(payload['nodes'])
			else:
				_send_string = {'error':'No \'nodes\' key passed to delete_node.'}
		
		elif payload['param'] == 'modify_node':
			if payload.has_key('id') and payload.has_key('query'):
				_send_string = self.handle_modify_node(payload['id'],payload['query'])
			
			elif not payload.has_key('id') and not payload.has_key('query'):
				_send_string = {'error':'Missing keys for \'modify_node\': id, query.'}
			
			elif not payload.has_key('id'):
				_send_string = {'error':'Missing key for \'modify_node\': id.'}
			
			elif not payload.has_key('query'):
				_send_string = {'error':'Missing keys for \'modify_node\': query.'}
		
		self.send(json.dumps(_send_string))
		return True

	def handle_fetch_node(self,node):
		_fetched_nodes = []
		
		for fetch_node in node['fetch']:
			_find_nodes = self.handle_find_nodes(fetch_node)
			
			if _find_nodes.has_key('results') and _find_nodes['results']:
				_fetched_node = self.handle_get_nodes([_find_nodes['results'][0]])
				_fetched_nodes.append(_fetched_node['results'][0])
			else:
				_node_string = {'error':'Fetched node %s does not exist.'
					% node['fetch'].index(fetch_node)}
				_fetched_nodes = []
				break
		
		if _fetched_nodes:
			node['text'] = node['format']
			
			for match in re.findall('[[node\\[\\d\\]]*].[\\w]*',node['text']):
				_node_id = int(match.partition('[')[2].partition(']')[0])-1
				_key = match.partition('.')[2]
				node['text'] = node['text'].replace(match,_fetched_nodes[_node_id][_key])
			
			_node_string = node
		
		return _node_string
	
	def handle_modify_node(self,node_id,query):
		_changed_node = None
		
		for node in self.user['nodes']:
			if node['id'] == node_id:
				_changed_node = node
				break
		
		if not _changed_node:
			return {'error':'Could not find node with ID \'%s\'.' % node_id}
		
		for key in query:
			node[key] = query[key]
		
		#TODO: It's pointless to return the ID of the node, because the
		#client should already be aware of what the ID is for this type
		#of call to begin with. Somethng should be returned, and it would
		#be out of place for only a string to be returned or something
		#similar. We'll just return the entire node for now.
		return node

	def handle_missing_api_key(self):
		logging.error('Incorrect API key from %s:%s' % (self.client_host,self.client_port))
		self.send(json.dumps({'error':'No API key found in dictionary.'}))

	def auth_user_via_api_key(self,api_key):
		for user in self.factory.users:
			if user['api-key'] == api_key:
				logging.debug('%s -> %s' % (self.name,user['name']))
				self.name = user['name']
				self.user = user
				return True

		logging.error('Incorrect API key from %s:%s' % (self.client_host,self.client_port))
		self.send(json.dumps({'error':'No user with that API key exists.'}))

		return False

	def get_api_key_from_payload(self,payload):
		if not payload.has_key('apikey'):
			return False

		return payload['apikey']

	def create_node_from_payload(self,payload):
		return self.factory.create_node_from_payload(self.user,payload)

	def delete_nodes_from_payload(self,nodes):
		return self.factory.delete_nodes_from_payload(self.user,nodes)

	def delete_node(self,node):
		return self.factory.delete_node(self.user,node)

	def remove_references_to_node(self,node):
		return self.factory.remove_references_to_node(self.user,node)

	def add_child_to_node(self,parent,child):
		return self.factory.add_child_to_node(parent,child)

	def filter_nodes(self):
		self.factory.filter_nodes(self.user)

	def handle_find_nodes(self,query):
		_found_nodes = self.find_nodes(query)

		if _found_nodes:
			return {'results':_found_nodes}
		else:
			return {'error':'No nodes were found.'}

	def handle_get_nodes(self,nodes):
		_returned_nodes = []

		_nodes_copy = nodes[:]

		for node in self.user['nodes']:
			if node['id'] in _nodes_copy:
				if node['type'] == 'fetch':
					node = self.handle_fetch_node(node)
				
				_returned_nodes.append(node)
				_nodes_copy.remove(node['id'])

			if not len(_nodes_copy):
				break

		return {'results':_returned_nodes}

	def find_nodes(self,query):
		return self.factory.find_nodes(self.user,query)

	def retrieve_node_via_id(self,id):
		return self.factory.retrieve_node_via_id(self.user,id)

	def update_user_node_mesh(self):
		#TODO: Look over this
		self.filter_nodes()
		self.factory.save_users_db()

	def create_event(self,type,value):
		"""Creates and broadcasts event of type 'type' with value 'value'"""
		logging.info('Event created: %s - %s' % (type,value))
		
		self.factory.broadcast_event(type,value,self.name)

class SwanBotFactory(Factory):
	protocol = SwanBot
	modules = []
	clients = []
	geoip = None

	def __init__(self):
		self.users = []
		
		self.load_users_db()
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
				logging.info('Creating new user DB...')
				self.add_user('root','testkey')

				_file.write(json.dumps(self.users))
				_file.close()
				logging.info('Created words database.')
				self.load_users_db(error=True)
			else:
				logging.error('The user DB could not be loaded. Run swanbot.py --init')
				_file.close()
				sys.exit()

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
		if not self.geoip:
			return 'Unknown'

		_ip_info = self.geoip.country_name_by_addr(ip)

		if _ip_info:
			return _ip_info
		else:
			logging.debug('Could not find location for \'%s\'' % ip)
			return 'Unknown'

	def save_users_db(self):
		_file = open(os.path.join('data','core_users.json'),'w')		
		_file.write(json.dumps(self.users))
		_file.close()
	
	def startFactory(self):
		logging.info('SwanBot is up and running.')
		
		self.add_module('mod_coreutils.py')
		self.add_module('mod_weather.py')
		
		self.module_thread = ModuleThread()
		self.module_thread.start(self)
	
	def stopFactory(self):
		self.save_users_db()
		
		logging.info('SwanBot is shutting down.')
		self.module_thread.stop()
	
	def tick_modules(self):
		#TODO: Obviously need to refactor here, but I'll wait until
		#the issue of public vs. private in relation to modules is
		#resolved.
		_public_nodes = self.get_all_user_nodes()
		
		for module in self.modules:
			try:
				module['module'].tick(_public_nodes,self)
			except Exception:
				logging.error(sys.exc_info())

	def create_node_from_payload(self,user,payload):
		_node = nodes.create_node()
		_node['owner'] = user['name']

		for key in payload:
			_node[key] = payload[key]

		if payload.has_key('parent') and payload['parent']:
			_parent_nodes = self.find_nodes(payload['parent'])

			for parent_node in _parent_nodes:
				logging.info('Found parent!')
				_retrieved_node = self.retrieve_node_via_id(user,parent_node)
				self.add_child_to_node(_retrieved_node,_node)

			del _node['parent']

		user['nodes'].append(_node)
		logging.info('Created node with ID #%s of type \'%s\'' %
		             (_node['id'],_node['type']))

		self.filter_nodes(user)

		return _node

	def delete_nodes_from_payload(self,user,nodes):
		"""Deletes nodes, where `nodes` is an array
		  of the node IDs to be deleted.

		  returns: array of node IDs that could not be deleted."""
		
		for _user in self.users:
			if _user['name'] == user['name']:
				user = _user
		
		_nodes_copy = nodes[:]

		for node in nodes:
			_node_to_delete = self.retrieve_node_via_id(user,node)
			self.delete_node(user,_node_to_delete)
			_nodes_copy.remove(node)

		return {'results':_nodes_copy}

	def delete_node(self,user,node):
		logging.info('Deleted node #%s of type \'%s\'' %
		             (node['id'],node['type']))

		self.remove_references_to_node(user,node)
		user['nodes'].remove(node)

	def remove_references_to_node(self,user,node):
		for _node_in_mesh in user['nodes']:
			if _node_in_mesh == node:
				continue

			if node['id'] in _node_in_mesh['parents']:
				_node_in_mesh['parents'].remove(node['id'])
				logging.info('\tSynapse with parent #%s removed.' % _node_in_mesh['id'])

			if node['id'] in _node_in_mesh['children']:
				_node_in_mesh['children'].remove(node['id'])
				logging.info('\tSynapse with child #%s removed.' % _node_in_mesh['id'])

	def add_child_to_node(self,parent,child):
		if not parent['id'] in child['parents']:
			child['parents'].append(parent['id'])

		if not child['id'] in parent['children']:
			parent['children'].append(child['id'])

		return True

	def filter_nodes(self,user):
		for node1 in user['nodes']:
			for node2 in user['nodes']:
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
					logging.info('Synapse: Node #%s -> Node #%s' %
					             (node2['id'],node1['id']))

	def find_nodes(self,user,query):
		_matching_nodes = []

		for node in user['nodes']:
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

		#logging.info('Found %s matching nodes.' % len(_matching_nodes))

		return _matching_nodes

	def retrieve_node_via_id(self,user,id):
		for node in user['nodes']:
			if node['id'] == id:
				return node

		return None

	def get_public_user_nodes(self):
		_public_user_nodes = []
		
		for user in self.users:
			_nodes = []
			
			for node in user['nodes']:
				if node['public']:
					_nodes.append(node)
			
			_public_user_nodes.append({'name':user['name'],'nodes':_nodes})
		
		return _public_user_nodes
	
	def get_all_user_nodes(self):
		_user_nodes = []
		
		for user in self.users:
			_user_nodes.append({'name':user['name'],'nodes':user['nodes'][:]})
		
		return _user_nodes
	
	def get_user_from_name(self,name):
		for user in self.users:
			if user['name'] == name:
				return user

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
	
	def add_user(self,name,password):
		for user in self.users:
			if user['name'] == name:
				logging.error('User \'%s\' already exists!' % name)
				return False
		
		api_key = hashlib.sha224(password).hexdigest()
		_user = {'name':name,
			'api-key':api_key,
			'nodes':[]}
		self.users.append(_user)
	
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

		logging.info('Module \'%s\' loaded.' % _mod_name)

		self.modules.append({'name':_sanitized_name,'module':_module})
		
		return 1
	
	def remove_module(self,name):
		name = name.replace('mod_','').replace('.py','')
		
		for mod in self.modules:
			if mod['name'] == name:
				self.modules.remove(mod)
				return 1
		
		return 0
	
	def handle_action_node(self,node):
		if node['type'] == 'speech':
			return speech.node_to_speech(node['text_from'])

endpoint = TCP4ServerEndpoint(reactor, 9002)
endpoint.listen(SwanBotFactory())
reactor.run()