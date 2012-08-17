import bluetooth
import logging
import hashlib
import client
import time
import json
import os

#Set up proper logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('[%(asctime)s] %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(console_formatter)
logger.addHandler(ch)

class BluetoothBot:
	def __init__(self):
		self.devices = []
		self.core = None
		self.status = {'command':None,'value':None,'data':None}
		
		self.load()
	
	def connect_to_client(self):
		client.start(self,'localhost',9002,execute=self.status)
	
	def connected_to_client(self,callback):
		self.core = callback
	
	def get_data(self,data):
		self.status['data'] = data
		self.core.quit()
		
		logging.info('Disconnected from core.')
	
	def pair_device_with_user(self,user,value,to):
		self.status['command'] = 'set_user_value'
		self.status['value'] = '\'%s\',\'%s\',\'%s\'' % (user,value,to)
		
		self.connect_to_client()
		
		if not to == self.status['data']:
			raise Exception('Did not get expected return value! Wanted %s, got %s.' %
				(to,self.status['data']))
			
		logging.info('Device was paired successfully!')
	
	def save(self):
		try:
			os.mkdir('data')
		except:
			pass
		
		try:
			_out = open(os.path.join('data','bluetooth.json'),'w')
		except Exception, e:
			print e
			logging.error('Could not open data%sbluetooth.json for writing!' % os.sep)
			return 0
		
		_out.write(json.dumps(self.devices))
		_out.close()
		self.core.quit()
	
	def load(self):
		try:
			_out = open(os.path.join('data','bluetooth.json'),'r')
		except:
			logging.error('Could not open data%sbluetooth.json for reading!' % os.sep)
			return 0
		
		self.devices = json.loads(_out.readline())
		_out.close()
	
	def discover_devices(self):
		for device in bluetooth.discover_devices(lookup_names = True):
			_found = False
			
			for _device in self.devices:
				print 
				if _device['address'][0] == device[0]:
					_found = True
					break
			
			if not _found:
				self.devices.append({'address':device,'connection':None})
				logging.debug('Added new bluetooth device %s (%s)' % (device[0],device[1]))
				
		self.devices
	
	def list_devices(self):
		for device in self.devices:
			print device
	
	def look_for_user(self,name):
		if not self.status['data']:
			self.status['command'] = 'get_user_value'
			self.status['value'] = '\'%s\',\'%s\'' % (name,'bluetooth')
		
			self.connect_to_client()
		
		_bluetooth = self.status['data']
		
		for device in self.devices:
			if not device['address'][0]==_bluetooth: continue
			
			if not device['connection']:
				device['connection'] = bluetooth.BluetoothSocket()
				
				try:
					device['connection'].connect((device['address'][0],1))
				except:
					pass
			
			print 'Took a while'
			try:
				device['connection'].send('!')
				return True
			except:
				device['connection'].close()
				device['connection'] = None
				return False
	
	def watch_for_user(self,user):
		user_here = self.look_for_user(user)
		
		while 1:
			if self.look_for_user(user):
				if not user_here:
					logging.info('User is nearby!')
				
				user_here = True
				
			elif user_here:
				user_here = False
				logging.info('%s has left.' % (user))
				break
				
			else:
				print 'Not here!'
			
			#time.sleep(5)

def encrypt(text):
	return hashlib.sha224(text).hexdigest()

def lock_screen():
	winpath = os.environ['windir']
	os.system(winpath + r'\system32\rundll32 user32.dll, LockWorkStation')

bot = BluetoothBot()
#bot.pair_device_with_user('test','bluetooth',bot.devices[0]['address'][0])
bot.watch_for_user('test')