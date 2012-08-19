import facedetect
import bluetooth
import threading
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

class Start(threading.Thread):
	def client_disconnected(self):
		global bot
		
		bot.stop = True
		logging.info('Waiting for watch thread to end...')
		
	def connected_to_client(self,callback):
		global bot
		
		bot.core = callback
		print 'Set core, starting...'
		self.start()
		
	def run(self):
		global bot
		
		if bot.core:
			#bot.connect_to_client()
			bot.pair_device_with_user('test','bluetooth',bot.devices[1]['address'][0])
			bot.watch_for_user('test')

class BluetoothBot():
	def __init__(self):
		self.devices = []
		self.core = None
		self.stop = False
		
		self.load()
	
	def connect_to_client(self):
		logging.info('Connecting to core.')
		client.start(self,'localhost',9002)
	
	def get_data(self,data):
		self.status['data'] = data
	
	def pair_device_with_user(self,user,value,to):
		self.core.set_user_value(user,value,to)
		
		#if not to == self.status['data']:
		#	raise Exception('Did not get expected return value! Wanted %s, got %s.' %
		#		(to,self.status['data']))
			
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
		#self.status['command'] = 'get_user_value'
		#self.status['value'] = '\'%s\',\'%s\'' % (name,'password')
		#self.connect_to_client()
		#_bluetooth = self.status['data']
		
		_q = self.core.get_user_value(name,'bluetooth')
		
		while 1:
			if _q['done']:
				_bluetooth = json.loads(_q['data'])['text']
				break
		
		for device in self.devices:
			if not device['address'][0]==_bluetooth: continue
			
			if not device['connection']:
				device['connection'] = bluetooth.BluetoothSocket()
				
				try:
					device['connection'].connect((device['address'][0],1))
				except:
					pass
			
			try:
				device['connection'].send('!')
				return True
			except:
				device['connection'].close()
				device['connection'] = None
				return False
	
	def watch_for_user(self,user):
		user_here = self.look_for_user(user)
		force_recheck = False
		_sleep_for = 10
		_face_file = None
		
		_q = self.core.get_user_value(user,'face')
		
		while 1:
			if _q['data']:
				_face_file = json.loads(_q['data'])['text']
				break
		
		print _face_file
		
		while not self.stop:
			if self.look_for_user(user):
				if not user_here or force_recheck:
					if force_recheck:
						force_recheck = False
						logging.info('Recheck was forced.')
						
					logging.info('User is nearby!')
					
					if _face_file:
						_face_detect = facedetect.compare(_face_file)
					else:
						logging.info('No face on file. Smile!')
						_face_detect = facedetect.compare('%s.jpg' % user,learn=True)
						self.core.set_user_value(user,'face','%s.jpg' % user)
					
					if _face_detect:
						logging.info('Welcome home!')
						_sleep_for = 60
					else:
						force_recheck = True
						_sleep_for = 3
						logging.info('False detection of %s. Scan time set to %s this tick, next 60.' %
							(user,_sleep_for))
				
				else:
					_sleep_for = 60
				user_here = True
				
			elif user_here:
				user_here = False
				_sleep_for = 30
				logging.info('%s has left. Scan time set to: %s' % (user,_sleep_for))
				lock_screen()
			else:
				pass
				#_sleep_for = 30
				print 'Not here!'
			
			#print _sleep_for
			
			time.sleep(_sleep_for)

def encrypt(text):
	return hashlib.sha224(text).hexdigest()

def lock_screen():
	winpath = os.environ['windir']
	os.system(winpath + r'\system32\rundll32 user32.dll, LockWorkStation')

bot = BluetoothBot()

_start = Start()
client.start(_start,'localhost',9002)