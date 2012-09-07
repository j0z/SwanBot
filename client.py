from twisted.internet import protocol, reactor
from twisted.protocols import basic
import logging
import json
import sys

class Client(basic.LineReceiver):
	node_db_callback = None
	callback = None
	recv_node_db_string = ''
	query_id = 0
	
	def __init__(self,callback):
		self.node_db_string = ''
		self.callback = callback
		self.queries = []
	
	def restart(self):
		pass
	
	def quit(self):
		self.transport.loseConnection()
		reactor.stop()
	
	def create_query(self):
		_temp = {'id':self.query_id,'data':'','done':False}
		self.queries.append(_temp)
		self.query_id+=1
		
		if '--debug' in sys.argv:
			logging.info('Created query #%s' % _temp['id'])
		
		return _temp
	
	def get_query(self,qid):
		for entry in self.queries:
			if entry['id'] == qid:
				return entry
		
		return -1
		
	def connectionMade(self):
		self.send('%s:%s:%s' % (self.factory.user,self.factory.password,
			self.factory.clientname))
		
		if self.callback:
			try:
				self.callback.connected_to_client(self)
			except:
				logging.error('Could not find callback.connected_to_client!')
		else:
			logging.warning('No callback set for core! How\'d you manage that?')
	
	def connectionLost(self,reason):
		if self.callback:
			try:
				self.callback.client_disconnected()
			except:
				pass
	
	def send(self,line):
		self.transport.write(line.encode('utf-8')+'\r\n')
	
	def fire_event(self,type,value):
		self.send('event:%s:%s' % (type,value))

	def lineReceived(self,line):
		#print '>>>',line
		
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
					logging.error('Data invalid. Got...')
					print _query['data']
				
				try:
					self.callback.get_data(_data)
				except:
					logging.error('Callback is missing function \'get_data()\'')
		
		elif _args[0] == 'comm':
			_script_id = int(_args[2])
			
			if _args[1] == 'text':
				try:
					self.callback.get_text(':'.join(_args[3:]))
					self.send('comm:got:%s' % _script_id)
				except:
					logging.error('Callback is missing function \'get_text()\'')
			
			elif _args[1] == 'data':
				try:
					self.callback.get_data(':'.join(_args[3:]))
					self.send('comm:got:%s' % _script_id)
				except:
					logging.error('Callback is missing function \'get_data()\'')
			
			elif _args[1] == 'input':
				#logging.info('Script with ID \'%s\' requests input.' % _script_id)
				
				try:
					self.callback.get_input(_script_id)
				except:
					logging.error('Callback is missing function \'get_input()\'')
			
			elif _args[1] == 'term':
				logging.info('Script with ID \'%s\' terminated.' % _script_id)
				
				try:
					self.callback.unlock(_script_id)
				except:
					logging.error('Callback is missing function \'unlock()\'')
		
		elif _args[0] == 'event':
			if len(_args)<3:
				return False
			
			try:
				self.callback.get_event(_args[1],':'.join(_args[2:]))
			except:
				logging.error('Callback is missing function \'get_event()\'')
	
	def get_user_value(self,name,value):
		_query = self.create_query()
		self.send('get:user_value:%s:%s:%s' % (_query['id'],name,value))
		
		return _query
	
	def set_user_value(self,name,value,to):
		_query = self.create_query()
		self.send('send:user_value:%s:%s:%s:%s' % (_query['id'],name,value,to))
		
		return _query
	
	def run_command(self,args):
		_query = self.create_query()
		self.send('comm:get:'+str(_query['id'])+':'+':'.join(args))
	
	def get_node_db(self,callback):
		self.send('get:nodes')
		self.node_db_callback = callback
	
	def start_send_node_db(self):
		self.send('send:start-node')
	
	def send_node_db(self,data):
		_client = ['python','client.py']
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
	def __init__(self,callback,user='',password='',clientname='Unnamed'):
		self.callback = callback
		self.user = user
		self.password = password
		self.clientname = clientname

		#def clientConnectionLost(self, connector, reason):
		#print 'Reconnecting?'
		#connector.connect()

	def buildProtocol(self,addr):
		p = Client(self.callback)
		p.factory = self
		return p

def start(callback,core_host,core_port,user='',password='',clientname='Unnamed'):
	f = ClientFactory(callback,user=user,password=password,clientname=clientname)
	reactor.connectTCP(core_host,core_port,f)
	
	try:
		reactor.run()
	except:
		logging.info('Reactor still running...')
		
		