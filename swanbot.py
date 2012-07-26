#The majority of this code was taken from
#	http://twistedmatrix.com/documents/current/core/howto/clients.html#auto5
#While the original code would have worked fine for a bot, I didn't like the
#way they handled logging. Why reinvent the wheel when Python has an
#excellent built-in module (`logging`) for doing just that?
#Anyway, this bot creates a "database" of registered users that it loads on
#run and saves on exit.
#
#python swanbot.py -build-db
#python swanbot.py
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
__password__ = 'yerpderp'
__email__ = 'clearlyfake@itsfakeimnotkidding.org'
__channels__ = ['#talk','#holo']
__user__ = {'name':'',
	'host':'',
	'last_channel':None,
	'alert_channel':None,
	'owner':False,
	'speech_highlight_in_public':False}

class check_users(threading.Thread):
	running = True
	callback = None
	blacklist = []
	
	def run(self):
		while self.running:
			if self.callback:
				for user in database['users']:
					for module in self.callback.modules:
						if module['name'] in self.blacklist:
							continue
						
						try:
							module['module'].user_tick(user,self.callback)
						except:
							logging.error('Error in %s.user_tick()!' % module['name'])
							self.blacklist.append(module['name'])
				
				for module in self.callback.modules:
					if module['name'] in self.blacklist:
						continue
					
					try:
						module['module'].tick(self.callback)
					except:
						logging.error('Error in %s.tick()!' % module['name'])
						self.blacklist.append(module['name'])
				
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
	owner = None
	versionName = 'SwanBot'
	versionNum = '0.1'
	versionEnv = 'Wayne Brady'
	
	def msg(self,channel,message,to=None):
		_user = is_registered(to)
		
		if _user:			
			if _user['speech_highlight_in_public']:
				message = '%s: %s' % (to,message)
		
		irc.IRCClient.msg(self,channel,str(message))
	
	def register_user(self,name,host):
		register_user(name,host)
	
	def get_users(self):
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

	def nickserv_identify(self):
		self.msg('nickserv','identify %s' % __password__)
	
	def connectionMade(self):
		global _check_thread
		
		if _check_thread.callback:
			return 0
		
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
		
		logging.info('Configuring...')
		
		for user in self.get_users():
			if user['owner']:
				self.owner = user['name']
				logging.info('Configure: Owner set to \'%s\'' % self.owner)
				break
		
		if not self.owner:
			logging.debug('Warning: No owner set! Message \'claim\' to %s.' % self.nickname)		

	def connectionLost(self, reason):
		global _check_thread
		
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
		_highlighted = False
		
		if name == self.nickname:
			return 0
		
		register_user(name,host=host)
		
		#logging.info("<%s> %s" % (name, msg))
		_args = msg.split(' ')
		_registered = is_registered(name,host=host)
		
		if _args[0].count(self.nickname):
			_args.pop(0)
			_highlighted = True

		if not _registered:
			logging.error('ERROR: User \'%s\' not registered!', name)
			return 1
		
		if not channel == self.nickname:
			_registered['last_channel'] = channel
		
		if channel==self.nickname:
			_registered['alert_channel'] = name
		else:
			_registered['alert_channel'] = channel
		
		if 'claim' in _args and not self.owner and (channel==self.nickname or _highlighted):
			_registered['owner'] = name
			self.owner = name
			
			self.msg(name,"I am now under your control. For a tutorial type, !tutorial")
		
		elif 'register' in _args and _registered['owner'] and (channel==self.nickname or _highlighted):
			logging.info('NICKSERV: Attempting to register (issued by %s)' % name)
			self.msg('nickserv','register %s %s' % (__password__,__email__))
		
		elif 'reload' in _args and _registered['owner'] and (channel==self.nickname or _highlighted):
			logging.info('Reloading core...')
			reload(core)
			self.msg(_registered['alert_channel'],'Reloaded module \'core\'')
			
			for module in self.modules:
				logging.info('Reloading %s...' % module['name'])
				
				try:
					reload(module['module'])
					self.msg(_registered['alert_channel'],'Reloaded module \'%s\'' % module['name'],
						to=name)
				except:
					logging.error('Failed loading %s!' % module['name'])
			
			logging.info('Done reloading modules')
			
		elif ' '.join(_args)=='highlight me in public':
			_registered['speech_highlight_in_public'] = True
			self.msg(_registered['alert_channel'],'I will highlight you when speaking in public.',to=name)
		
		elif ' '.join(_args)=='don\'t highlight me in public':
			_registered['speech_highlight_in_public'] = False
			self.msg(_registered['alert_channel'],'I will not highlight you when speaking in public.',
				to=name)	
		
		elif ' '.join(_args)=='kill connection' and (channel==self.nickname or _highlighted):
			logging.info('Shutdown called by \'%s\'' % name)

			reactor.stop()
		
		else:
			core.parse(_args,self,_registered['alert_channel'],_registered)
			
			for module in self.modules:
				module['module'].parse(_args,self,_registered['alert_channel'],_registered)
		
	def noticed(self, user, channel, msg):
		try:
			name,host = user.split('!', 1)
		except:
			return 1

		#Specific stuff to do with NICKSERV
		if name.lower() == 'nickserv':
			if msg.count('already identified'):
				logging.info('NICKSERV: I was already identified.')
			elif msg.count('isn\'t registered'):
				logging.info('NICKSERV: I am not registered. Type \'register\'.')
			elif msg.count('registered under'):
				logging.info('NICKSERV: I am now registered with NICKSERV.')
				self.msg(self.owner,'I am now registered with NICKSERV.')
			elif msg.count('This nickname is registered'):
				logging.info('NICKSERV: Trying to identify with NICKSERV.')
				self.nickserv_identify()
			elif msg.count('now recognized'):
				logging.info('NICKSERV: I am identified with NICKSERV.')

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
