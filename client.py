from twisted.internet import protocol, reactor
from twisted.protocols import basic
import logging
import hashlib
import json

class Client(basic.LineReceiver):
	node_db_callback = None
	callback = None
	recv_node_db_string = ''
	query_id = 0
	
	def __init__(self,callback,execute=None):
		self.node_db_string = ''
		self.callback = callback
		self.execute = execute
		self.queries = []
	
	def quit(self):
		reactor.stop()
	
	def create_query(self):
		_temp = {'id':self.query_id,'data':'','done':False}
		self.queries.append(_temp)
		self.query_id+=1
		
		logging.info('Created query #%s' % _temp['id'])
		
		return _temp
	
	def get_query(self,qid):
		for entry in self.queries:
			if entry['id'] == qid:
				return entry
		
		return -1
		
	def connectionMade(self):
		self.send('%s:%s' % (self.factory.user,self.factory.password))
		
		if self.callback:
			try:
				self.callback.connected_to_client(self)
			except:
				logging.error('Could not find callback.connected_to_client!')
		else:
			logging.warning('No callback set for core! How\'d you manage that?')
		
		if self.execute:
			try:
				exec('self.%s(%s)' % (self.execute['command'],self.execute['value']))
			except Exception, e:
				print e
				print 'self.%s(%s)' % (self.execute['command'],self.execute['value'])
	
	def connectionLost(self,reason):
		pass
	
	def send(self,line):
		self.transport.write(line.encode('utf-8')+'\r\n')

	def lineReceived(self,line):
		#print line
		
		_args = line.split(':')
		
		if not _args:
			return 0
		
		if _args[0] == 'login':
			if _args[1] == 'success':
				logging.info('Logged in to core.')
			else:
				logging.info('Login to core failed!')
				self.transport.loseConnection()
				reactor.stop()
		
		elif _args[0] == 'send':
			if _args[1] == 'nodes':
				self.node_db_string += ':'.join(_args[2:])
				
				try:
					_node_db = json.loads(self.node_db_string)
					
					if self.node_db_callback:
						logging.info('Sending node_db to callback...')
						self.node_db_callback(_node_db)
					else:
						logging.info('No callback was set! Data tossed.')
				except:
					logging.info('Downloading chunk: %s' % len(self.node_db_string))
					self.send('get:nodes')
		
			elif _args[1] == 'data':
				_query = self.get_query(int(_args[2]))
				
				if _query==-1:
					logging.error('Got malformed packet: Expected third argument to be valid query ID.')
					return 0
				
				_query['data'] += ':'.join(_args[3:])
				
				try:
					_data = json.loads(_query['data'])
					#_query['callback'](_data)
					_query['done'] = True
					
					if self.execute:
						self.callback.get_data(_data)
				except:
					print 'Data invalid, sending for more chunks...'
	
	def get_user_value(self,name,value):
		_query = self.create_query()
		self.send('get:user_value:%s:%s:%s' % (_query['id'],name,value))
		
		return _query
	
	def set_user_value(self,name,value,to):
		_query = self.create_query()
		self.send('send:user_value:%s:%s:%s:%s' % (_query['id'],name,value,to))
		
		return _query
	
	def get_node_db(self,callback):
		self.send('get:nodes')
		self.node_db_callback = callback
	
	def start_send_node_db(self):
		self.send('send:start-node')
	
	def send_node_db(self,data):
		self.send('send:nodes:%s' % data)
		logging.info('Uploading node_db to server (chunk %s)' % len(data))
	
	def examine_topic(self,topic,range=0):
		_query = self.create_query()
		self.send('get:examine_topic:%s:%s:%s' % (_query['id'],range,topic))
		
		return _query
	
	def research_topic(self,mid,range=0):
		_query = self.create_query()
		self.send('get:research_topic:%s:%s:%s' % (_query['id'],range,mid))
		
		return _query
	
	def expand_nodes(self,nodes,range=0):
		_query = self.create_query()
		self.send('get:expand_nodes:%s:%s:%s' % (_query['id'],range,json.dumps(nodes)))
		
		return _query
	
	def nodes_to_string(self,nodes,range=0):
		_query = self.create_query()
		self.send('get:nodes_to_string:%s:%s:%s' % (_query['id'],range,json.dumps(nodes)))
		
		return _query
	
	def find_node(self,search,range=0):
		_query = self.create_query()
		self.send('get:find_node:%s:%s:%s' % (_query['id'],range,search))
		
		return _query
	
	def show_node(self,index,range=0):
		_query = self.create_query()
		self.send('get:show_node:%s:%s:%s' % (_query['id'],range,index))
		
		return _query

class ClientFactory(protocol.ClientFactory):
	def __init__(self,callback,user='test',password='test',execute=None):
		self.callback = callback
		self.user = user
		self.password = hashlib.sha224(password).hexdigest()
		self.execute = execute

	def buildProtocol(self,addr):
		p = Client(self.callback,execute=self.execute)
		p.factory = self
		return p

def start(callback,core_host,core_port,execute=None):
	f = ClientFactory(callback,execute=execute)
	reactor.connectTCP(core_host,core_port,f)
	
	try:
		reactor.run()
	except:
		pass