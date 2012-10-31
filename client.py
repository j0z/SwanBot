import socket
import json

class Client:
	def __init__(self,host,apikey,port=9002,debug=False):
		self.host = host
		self.port = port
		self.apikey = apikey
		self.debug = debug

	def parse(self,data):
		if self.debug:
			for line in ['%s: %s' % (key,data[key]) for key in data]:
				print line
	
			print '='*10
		
			if data.has_key('error'):
				print 'Error:',data['error']

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
		_result = json.dumps(query)
		json.loads(_result)
		
		return self.send({'param':'create_node','query':query})

	def find_nodes(self,query):
		_results = self.get({'param':'find_nodes','query':query})

		if _results.has_key('results'):
			return _results['results']
		
		return []

	def get_nodes(self,nodes):
		_results = self.get({'param':'get_nodes','nodes':nodes})

		if _results.has_key('results'):
			return _results['results']
		
		return []

	def delete_nodes(self,nodes):
		_results = self.send({'param':'delete_nodes','nodes':nodes})

		if _results.has_key('results'):
			return _results['results']
		
		return []
	
	def modify_node(self,node_id,query):
		_results = self.send({'param':'modify_node','id':node_id,
						'query':query})
		
		if _results.has_key('results'):
			return _results['results']
		
		return []

#API_KEY = '934a26c6ec10c1c44e1e140c6ffa25036166c0afd0efcfe638693e6a'
#_client = Client('localhost',API_KEY)
#print _client.get_nodes(_client.find_nodes({'type':'test_node'}))[0]['data']
#_client.modify_node(1,{'data':'derp2'})
#print _client.get_nodes(_client.find_nodes({'type':'test_node'}))[0]['data']
#
#print _client.create_node({'type':'test_node'})
#_client.create_node({'type':'test_node_2'})
#
#_client.create_node({'type':'fetch','name':'test_fetch',
#	'fetch':[{'type':'test_node'},{'type':'test_node_2'}],
#	'format':'Node 1: node[1].type, Node 2: node[2].type'})
#

#
#_client.create_node({'public':True,'type':'watch','input':{'type':'action',
#	'action':'tablet-awake'},'output':
#		{'type':'speech','text_from':{'type':'fetch','name':'test_fetch'}}})
#
#_client.create_node({'type':'calendar','public':True,
#        'url':'https://www.google.com/calendar/feeds/jetstarforever%40gmail.com/private-0b5d9ebe10bade7630eda7b436678e8c/basic'})