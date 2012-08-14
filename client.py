from twisted.internet import protocol, reactor
from twisted.protocols import basic
import logging
import hashlib
import json

class Client(basic.LineReceiver):
	node_db_callback = None
	callback = None
	recv_node_db_string = ''
	
	def __init__(self,callback):
		self.node_db_string = ''
		self.callback = callback
		
	def connectionMade(self):
		self.send('%s:%s' % (self.factory.user,self.factory.password))
		
		if self.callback:
			self.callback.connected_to_client(self)
		else:
			logging.warning('No callback set for core! How\'d you manage that?')
	
	def connectionLost(self,reason):
		pass
	
	def send(self,line):
		self.transport.write(line+'\r\n')

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
	
	def get_node_db(self,callback):
		self.send('get:nodes')
		self.node_db_callback = callback
	
	def start_send_node_db(self):
		self.send('send:start-node')
	
	def send_node_db(self,data):
		self.send('send:nodes:%s' % data)
		logging.info('Uploading node_db to server (chunk %s)' % len(data))

class ClientFactory(protocol.ClientFactory):
	def __init__(self,callback,user='test',password='test'):
		self.callback = callback
		self.user = user
		self.password = hashlib.sha224(password).hexdigest()

	def buildProtocol(self,addr):
		p = Client(self.callback)
		p.factory = self
		return p

def start(callback,core_port):
	f = ClientFactory(callback)
	reactor.connectTCP('localhost',core_port,f)
	
	try:
		reactor.run()
	except:
		logging.info('Reactor was already running.')