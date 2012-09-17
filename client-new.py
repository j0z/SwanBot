import socket
import json

class Client:
	def __init__(self,host,port=9002):
		self.host = host
		self.port = port
		
		self.connect()
	
	def parse(self,data):
		print repr(data)
		
		for line in ['%s: %s' % (key,data[key]) for key in data]:
			print line
		
		return data
		
	def connect(self):		
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((self.host,self.port))
	
	def get(self):
		self.conn.sendall('api-get:%s\r\n' % json.dumps(payload))
		self.conn.close()
		
		return self.parse(json.loads(self.conn.recv(1024).strip()))
	
	def send(self):
		self.conn.sendall('api-send:%s\r\n' % json.dumps(payload))
		self.conn.close()
		
		return self.parse(json.loads(self.conn.recv(1024).strip()))		

Client('localhost').get({'param':'user_value','user':'root','value':'password'})