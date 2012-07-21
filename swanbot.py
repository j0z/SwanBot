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
#You can disable this by commenting out lines 38-41

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
import threading
import logging
import parse
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

class check_users(threading.Thread):
	running = True
	callback = None
	
	def run(self):
		while self.running:
			_curr_time = time.strptime(time.ctime())
			
			for user in database['users']:
				if user.has_key('alarms'):
					for alarm in user['alarms']:
						_time = time.strptime(alarm['when'],'%H:%M')
						if _time.tm_hour <= _curr_time.tm_hour and _time.tm_min <= _curr_time.tm_min:
							user['alarms'].remove(alarm)
							
							if self.callback:
								self.callback.msg(user['alert_channel'],
									'%s: %s' % (user['name'],alarm['what']))
			
			time.sleep(1)

def is_registered(name,host):
	for user in database['users']:
		if user['name'] == name and user['host'] == host:
			return user

	return False

def register_user(name,host):
	if is_registered(name,host): return False

	logging.info('Registered new user: %s' % name)
	database['users'].append({'name':name,'host':host,'follow':False,'alert_channel':None})
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

database = {}

if '-build-db' in sys.argv:
	logging.info('Creating DB...')
	database = {}
	database['users'] = []
	save()
	sys.exit()
else:
	load()
	_check_thread = check_users()
	_check_thread.start()

class SwanBot(irc.IRCClient):
	nickname = __botname__

	def connectionMade(self):
		global _check_thread
		
		irc.IRCClient.connectionMade(self)
		logging.info('Connected to server')
		_check_thread.callback = self

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
		logging.info("<%s> %s" % (name, msg))
		_args = msg.split(' ')
		_registered = is_registered(name,host)
		
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
				
				if 'reload' in _args:
					self.msg(name,'Reloading module...')
					reload(parse)
				else:
					parse.parse(_args,self,channel,_registered)

	def action(self, user, channel, msg):
		user = user.split('!', 1)[0]
		logging.info("* %s %s" % (user, msg))

	def irc_NICK(self, prefix, params):
		old_nick = prefix.split('!')[0]
		new_nick = params[0]
		self.logger.log("%s is now known as %s" % (old_nick, new_nick))

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