import socket
import json

class Client:
	def __init__(self,host,port=9002):
		self.host = host
		self.port = port

		self.connect()

	def parse(self,data):
		for line in ['%s: %s' % (key,data[key]) for key in data]:
			print line

		return data

	def connect(self):		
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((self.host,self.port))

	def get(self,payload):
		self.conn.sendall('api-get:%s\r\n' % json.dumps(payload))

		_returned_data = self.parse(json.loads(self.conn.recv(1024).strip()))

		self.conn.close()
		return _returned_data

	def send(self,payload):
		self.conn.sendall('api-send:%s\r\n' % json.dumps(payload))

		_returned_data = self.parse(json.loads(self.conn.recv(1024).strip()))

		self.conn.close()
		return _returned_data

Client('localhost').get({'param':'user_value','user':'root','value':'password',
                         'apikey':'testkey'})
print '='*10
#Client('localhost').send({'param':'create_node','query':{'type':'twitter','public':True,
#                         'filter':{'type':'tweet'}},
#                         'apikey':'testkey'})
#print '='*10
#Client('localhost').send({'param':'create_node','query':{'type':'tweet','public':True,
#                          'parent':{'type':'twitter'}},
#                          'apikey':'testkey'})
print '='*10
Client('localhost').get({'param':'find_node','query':{'type':'tweet','public':True},
                          'apikey':'testkey'})