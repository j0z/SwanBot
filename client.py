import socket
import json

class Client:
	def __init__(self,host,apikey,port=9002,debug=True):
		self.host = host
		self.port = port
		self.apikey = apikey
		self.debug = debug

	def parse(self,data):
		if self.debug:
			for line in ['%s: %s' % (key,data[key]) for key in data]:
				print line
	
			print '='*10

		return data

	def connect(self):		
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((self.host,self.port))

	def disconnect(self):
		self.conn.close()
		self.conn = None

	def get(self,payload):
		payload['apikey'] = self.apikey

		self.connect()
		self.conn.sendall('api-get:%s\r\n' % json.dumps(payload))

		_returned_data = self.parse(json.loads(self.conn.recv(2048).strip()))

		self.disconnect()

		return _returned_data

	def send(self,payload):
		payload['apikey'] = self.apikey

		self.connect()
		self.conn.sendall('api-send:%s\r\n' % json.dumps(payload))

		_returned_data = self.parse(json.loads(self.conn.recv(2048).strip()))

		self.disconnect()

		return _returned_data

	def create_node(self,query):
		return self.send({'param':'create_node','query':query})

	def find_nodes(self,query):
		_results = self.get({'param':'find_nodes','query':query})

		if _results.has_key('results'):
			return _results['results']
		else:
			return []

	def get_nodes(self,nodes):
		_results = self.get({'param':'get_nodes','nodes':nodes})

		if _results.has_key('results'):
			return _results['results']
		else:
			return []

	def delete_nodes(self,nodes):
		_results = self.send({'param':'delete_nodes','nodes':nodes})

		if _results.has_key('results'):
			return _results['results']
		else:
			return []
#
#_client = Client('localhost','testkey')
#
#_client.create_node({'public':True,'type':'watch','input':{'type':'action',
#	'action':'tablet-awake'},'output':
#		{'type':'speech','text_from':{'type':'calendar_event'}}})
#
#_client.create_node({'type':'calendar','public':True,
#        'url':'https://www.google.com/calendar/feeds/jetstarforever%40gmail.com/private-0b5d9ebe10bade7630eda7b436678e8c/basic'})
