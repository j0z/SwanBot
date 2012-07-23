#The majority of this code was taken from
#	http://twistedmatrix.com/documents/current/core/howto/clients.html#auto5
#While the original code would have worked fine for a bot, I didn't like the
#way they handled logging. Why reinvent the wheel when Python has an
#excellent built-in module (`logging`) for doing just that?
#Anyway, this bot creates a "database" of registered users that it loads on
#run and saves on exit.
#
#python ircbot.py -build-db
#python ircbot.py
#
#You can then private message the bot like so:
#<flags> register
#<Holo> You've been registered, flags!
#<flags> register
#<Holo> You've already been registered, flags!
#
#Just wanted to show how JSON can be a lot better than MySQL in cases such
#as this. Notice how I have to do very little work in save() and load() to
#store/fetch data.
#
#Also note that a log file is created in data/log.txt

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import threading
import logging
import core
import time
import json
import sys
import os

#Set up proper logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('[%(asctime)s] %(message)s')

try: os.mkdir('data')
except: pass

fh = logging.FileHandler(os.path.join('data','log.txt'))
fh.setLevel(logging.DEBUG)
fh.setFormatter(file_formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(console_formatter)
logger.addHandler(ch)

__botname__ = 'Holo'
__server__ = '192.168.1.2'
__port__ = 6667
__channels__ = ['#talk','#holo']
__user__ = {'name':'',
	'host':'',
	'follow':False,
	'last_channel':None,
	'alert_channel':None}

class check_users(threading.Thread):
	running = True
	callback = None
	
	def run(self):
		while self.running:
			if self.callback:
				for user in database['users']:
					for module in self.callback.modules:
						module['module'].user_tick(user,self.callback)
				
				for module in self.callback.modules:
					module['module'].tick(self.callback)
				
			time.sleep(1)

def is_registered(name,host=None):
	for user in database['users']:
		if user['name'] == name:
			if host and user['host'] == host:
				return user
			elif not host:
				return user

	return False

def register_user(name,host):
	if is_registered(name,host=host): return False

	logging.info('Registered new user: %s' % name)
	user = __user__.copy()
	user['name'] = name
	user['host'] = host
	
	database['users'].append(user)
	return True

def save():
	logging.info('Offloading database to disk...')
	_file = open(os.path.join('data','users.json'),'w')
	_file.write(json.dumps(database))
	_file.close()
	logging.info('Success!')

def load():
	logging.info('Attempting to load database from disk...')
	try:
		_file = open(os.path.join('data','users.json'),'r')
		database.update(json.loads(_file.readline()))
		
		for user in database['users']:
			for key in user:
				if isinstance(user[key],unicode):
					user[key] = str(user[key])
		
		_file.close()
		logging.info('Success!')
	except:
		logging.error('Could not load database from disk! Please run with -build-db')
		sys.exit()

def upgrade_db():
	_upgraded = False
	
	for user in database['users']:
		for key in __user__:
			if not user.has_key(key):
				user[key] = __user__[key]
				_upgraded = True
	
	if _upgraded:
		logging.info('DB updated!')

def setup():
	global _check_thread
	load()
	_check_thread = check_users()
	_check_thread.start()

database = {}

if '-build-db' in sys.argv:
	logging.info('Creating DB...')
	database = {}
	database['users'] = []
	save()
	sys.exit()
elif '-upgrade-db' in sys.argv:
	logging.info('Upgrading DB...')
	load()
	upgrade_db()
	save()
	setup()
else:
	setup()

if '-h' in sys.argv:
	__server__ = sys.argv[sys.argv.index('-h')+1]

if '-p' in sys.argv:
	__port__ = int(sys.argv[sys.argv.index('-p')+1])

if '-c' in sys.argv:
	__channels__ = sys.argv[sys.argv.index('-c')+1].split(',')

class SwanBot(irc.IRCClient):
	nickname = __botname__
	modules = []
	
	def get_users(self):
		#global database
		
		return database['users']
	
	def has_module(self,name):
		for module in self.modules:
			if module['name'] == name:
				return True
		
		return False
	
	def add_module(self,name):
		try:
			exec('import %s as temp' % name)
			self.modules.append({'name':name,'module':temp})
			logging.info('Loaded module \'%s\'' % name)
		except ImportError:
			logging.error('ImportError occurred when loading module \'%s\'' % name)

	def connectionMade(self):
		global _check_thread
		
		irc.IRCClient.connectionMade(self)
		logging.info('Connected to server')
		_check_thread.callback = self
		
		#Look for modules in modules.conf
		logging.info('Looking for modules.conf...')
		try:
			with open('modules.conf','r') as _modules_conf:
				for line in _modules_conf.readlines():
					self.add_module(line.strip())
			logging.info('Done loading modules')
		except IOError:
			logging.info('Could not find modules.conf.')
		except:
			logging.info('Error when parsing module in modules.conf: %s' % line)

	def connectionLost(self, reason):
		global _check_thread
		
		for channel in self.factory.channels:
			self.leave(channel,reason='Shutting down')
		
		irc.IRCClient.connectionLost(self, reason)
		logging.info('Killed connection to server')
		_check_thread.running = False
		save()

	def signedOn(self):
		for channel in self.factory.channels:
			self.join(channel)

	def joined(self, channel):
		logging.info("Joined %s" % channel)

	def privmsg(self, user, channel, msg):
		name,host = user.split('!', 1)
		#logging.info("<%s> %s" % (name, msg))
		_args = msg.split(' ')
		_registered = is_registered(name,host=host)
		
		if channel == self.nickname or _args[0].count(self.nickname):
			if _args[0].count(self.nickname):
				_args.pop(0)
			
			if 'register' in _args:
				if register_user(name,host):
					self.msg(name,'You\'ve been registered, %s!' % name)
				else:
					self.msg(name,'You\'ve already been registered, %s!' % name)

			elif _registered:
				if _registered['follow']:
					if channel==self.nickname:
						_registered['alert_channel'] = name
					else:
						_registered['alert_channel'] = channel
				else:
					_registered['alert_channel'] = name
				
				_registered['last_channel'] = channel
				
				if 'reload' in _args:
					logging.info('Reloading core...')
					reload(core)
					self.msg(_registered['alert_channel'],'Reloaded module \'core\'')
					
					for module in self.modules:
						logging.info('Reloading %s...' % module['name'])
						
						try:
							reload(module['module'])
							self.msg(_registered['alert_channel'],'Reloaded module \'%s\'' % module['name'])
						except:
							logging.error('Failed loading %s!' % module['name'])
					
					logging.info('Done reloading modules')
					
				else:
					core.parse(_args,self,_registered['alert_channel'],_registered)
					
					for module in self.modules:
						module['module'].parse(_args,self,_registered['alert_channel'],_registered)

	def userJoined(self, user, channel):
		#logging.info('%s joined %s' % (user,channel))
		
		for module in self.modules:
			module['module'].on_user_join(user,channel,self)
	
	def userLeft(self, user, channel):
		#logging.info('%s left %s' % (user,channel))
		
		for module in self.modules:
			module['module'].on_user_part(user,channel,self)
	
	def userQuit(self, user, quitMessage):
		pass
		#logging.info('%s quit (%s)' % (user,quitMessage))
	
	def action(self, user, channel, msg):
		user = user.split('!', 1)[0]
		#logging.info('* %s %s' % (user, msg))

	def irc_NICK(self, prefix, params):
		old_nick = prefix.split('!')[0]
		new_nick = params[0]
		#logging.info("%s is now known as %s" % (old_nick, new_nick))

	def alterCollidedNick(self, nickname):
		return nickname + '_'

class SwanBotFactory(protocol.ClientFactory):
	def __init__(self, channels):
		self.channels = channels

	def buildProtocol(self, addr):
		p = SwanBot()
		p.factory = self
		return p

	def clientConnectionLost(self, connector, reason):
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		logging.error("connection failed:", reason)
		reactor.stop()

def start():
	_factory = SwanBotFactory(__channels__)
	reactor.connectTCP(__server__, __port__, _factory)
	reactor.run()

if __name__ == '__main__':
	start()