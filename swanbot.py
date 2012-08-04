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
import re

try:
	import gntp.notifier
	__NOTIFICATIONS__ = True
except:
	print 'GNTP module not found. Notifications disabled.'
	__NOTIFICATIONS__ = False

try:
	import simplegit as git
	__GIT__ = True
except:
	print 'simplegit module not found. Git disabled.'
	__GIT__ = False

#Set up proper logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('[%(asctime)s] %(message)s')

try: os.mkdir('data')
except: pass

#fh = logging.FileHandler(os.path.join('data','log.txt'))
#fh.setLevel(logging.DEBUG)
#fh.setFormatter(file_formatter)
#logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
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
	'fallback_owner':False,
	'speech_highlight_in_public':False,
	'message_on_highlight':True}

class check_thread(threading.Thread):
	running = True
	callback = None
	blacklist = []
	update_timer_max = 1800
	update_timer = 1800
	
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
			
			if not self.update_timer:
				#Check if owner is online
				self.callback.update(is_registered(self.owner))
				self.update_timer = self.update_timer_max
			else:
				self.update_timer-=1
				
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
	_check_thread = check_thread()
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
	fallback_owner = None
	versionName = 'SwanBot'
	versionNum = '0.2'
	versionEnv = 'Wayne Brady\'s Cat'

	def update(self,user):
		if not __GIT__:
			return 1
		
		_reload = False
		logging.info('Update: Checking for updates')
		
		for line in git.pull('origin','master'):
			if line.count('swanbot.py'):
				logging.info('Update: Updates have been made to the core. Please restart.')
				self.msg(user['name'],'Changes to the core have been made. Restart.',to=user['name'])
			elif line.count('mod_'):
				logging.info('Update: \'%s\' changed.' % line.rpartition('.py')[0].strip())
				self.msg(user['name'],'Update: \'%s\' changed.' % line.rpartition('.py')[0].strip(),
					to=user['name'])
				_reload = True
		
		if _reload:
			logging.info('Update: Update finished. Reloading.')
			self.msg(user['name'],'Update completed. Reloading.',to=user['name'])
			self.reload(user)
		else:
			logging.info('Update: No updates.')
			self.msg(user['name'],'No updates.',to=user['name'])

	def reload(self,user):
		logging.info('Reloading modules...')
			
		reload(core)
		
		for module in self.modules:
			try:
				reload(module['module'])
			except:
				self.msg(user['alert_channel'],'Failed to reload \'%s\'' % module['name'],
					to=user['name'])
				logging.error('Failed loading %s!' % module['name'])
		
		self.msg(user['alert_channel'],'Reload completed.',to=user['name'])
		logging.info('Done reloading modules')
	
	def parse(self,text):
		text = text.replace('?','')
		text = text.split()
		_match = {'command':None,'matches':0,'keywords':[]}
		
		for module in self.modules:
			try:
				module['module'].__keyphrases__
			except:
				continue
			
			for phrase in module['module'].__keyphrases__:
				_keywords = []
				_matches = 0
				_break = False
				
				for need in phrase['needs']:
					_found_name = False
					
					if need['match'].count('%')==2:
						if need['match'] == '%user%':
							for user in self.get_users():
								if user['name'] == self.nickname:
									continue
								
								if user['name'] in text:
									_keywords.append(user['name'])
									_found_name = True
									_matches += 1
									break
							
							if _found_name:
								continue
					else:
						_re = re.findall(need['match'],' '.join(text).lower())
						
						if not len(_re) and need['required']:
							_break = True
							break
						elif len(_re):
							if not need.has_key('ignore') or not need['ignore']:
								_keywords.append(_re[0])
								_matches += 1
							else:
								_matches += 1
				
				if _break:
					continue
				
				for word in text:
					if word in phrase['keywords']:
						_matches += 1
			
				if _matches > _match['matches']:
					_match['command'] = phrase['command']
					_match['matches'] = _matches
					_match['keywords'] = _keywords
					_match['module'] = module['module']
		
		if _match['command']:
			return _match
		else:
			return None
	
	def notify(self,title,text,image=None,hostname='localhost'):
		if not __NOTIFICATIONS__:
			return 1
		
		gntp.notifier.mini(text,title=title,applicationName='SwanBot',\
			applicationIcon=image,hostname=hostname)
	
	def msg(self,channel,message,to=None):
		_user = is_registered(to)
		
		if _user:			
			if _user['speech_highlight_in_public']:
				message = '%s: %s' % (to,message)
			
			if _user['message_on_highlight'] or not channel==to:
				irc.IRCClient.msg(self,channel,str(message))
				return 1
			else:
				irc.IRCClient.notice(self,to,str(message))
				return 1
		
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
			elif user['fallback_owner']:
				self.fallback_owner = user['name']
				logging.info('Configure: Fallback owner set to \'%s\'' % self.fallback_owner)
			
			if self.owner and self.fallback_owner:
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
		self.who(channel)
	
	def kickedFrom(self, channel, kicker, message):
		logging.info('WARNING: Kicked from %s by %s: %s' % (channel,kicker,message))
		self.join(channel)

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
			
			self.msg(name,'I am now under your control.')
		
		elif 'register' in _args and (_registered['owner'] or _registered['fallback_owner']) and\
			(channel==self.nickname or _highlighted):
			logging.info('NICKSERV: Attempting to register (issued by %s)' % name)
			self.msg('nickserv','register %s %s' % (__password__,__email__))
		
		elif 'reload' in _args and (_registered['owner'] or _registered['fallback_owner']) and\
			(channel==self.nickname or _highlighted):
			self.reload(_registered)
			
		elif ' '.join(_args)=='highlight me in public':
			_registered['speech_highlight_in_public'] = True
			self.msg(_registered['alert_channel'],'I will highlight you when speaking in public.',to=name)
		
		elif ' '.join(_args)=='don\'t highlight me in public':
			_registered['speech_highlight_in_public'] = False
			self.msg(_registered['alert_channel'],'I will not highlight you when speaking in public.',
				to=name)	
		
		elif ' '.join(_args)=='kill connection' and (channel==self.nickname or _highlighted):
			if name == self.owner:
				logging.info('Shutdown called by \'%s\'' % name)
				reactor.stop()
		
		elif _args[0] == 'set':
			if len(_args)==3 and _args[1] == 'message_on_highlight':
				if _args[2] == 'on':
					_registered['message_on_highlight'] = True
					self.msg(_registered['name'],'I will message you directly for certain commands.',
						to=name)
				elif _args[2] == 'off':
					_registered['message_on_highlight'] = False
					self.msg(_registered['name'],'I will notify you for certain commands.',
						to=name)
		
		else:
			core.parse(_args,self,_registered['alert_channel'],_registered)
			
			if channel==self.nickname or _highlighted:
				_parse = self.parse(msg)
			else:
				_parse = None
			
			if _parse:
				_parse['keywords'][0] = _parse['command']
				_parse['module'].parse(_parse['keywords'],self,_registered['alert_channel'],_registered)
			else:
				for module in self.modules:
					_bypass = False
					
					try:
						if module['module'].__parse_always__:
							_bypass = True
					except:
						pass
					
					if (channel==self.nickname or _highlighted or _args[0][0]=='.' or _bypass):
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
			elif msg.count('now recognized') or msg.count('now identified'):
				logging.info('NICKSERV: I am identified with NICKSERV.')
			else:
				logging.info('NICKSERV: %s' % msg)
	
	def who(self, channel):
		self.sendLine('WHO %s' % channel)
	
	def irc_RPL_WHOREPLY(self, *nargs):
		register_user(nargs[1][5],'')
		
		for module in self.modules:
			try:
				module['module'].on_user_in_channel(nargs[1][1],nargs[1][5],self)
			except AttributeError:
				pass
			except:
				logging.error('ERROR in %s.on_user_in_channel()' % module['name'])
	
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
		
		for module in self.modules:
			try:
				module['module'].on_nick_change(old_nick,new_nick,self)
			except:
				logging.error('ERROR in %s.on_nick_change()' % module['name'])
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
