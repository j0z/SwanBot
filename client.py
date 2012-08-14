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
	
	def __init__(self,callback):
		self.node_db_string = ''
		self.callback = callback
		self.queries = []
	
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
			self.callback.connected_to_client(self)
		else:
			logging.warning('No callback set for core! How\'d you manage that?')
	
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
				except:
					print 'Data invalid, sending for more chunks...'
	
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
	def __init__(self,callback,user='test',password='test'):
		self.callback = callback
		self.user = user
		self.password = hashlib.sha224(password).hexdigest()

	def buildProtocol(self,addr):
		p = Client(self.callback)
		p.factory = self
		return p

def start(callback,core_host,core_port):
	f = ClientFactory(callback)
	reactor.connectTCP(core_host,core_port,f)
	
	try:
		reactor.run()
	except:
		logging.info('Reactor was already running.')