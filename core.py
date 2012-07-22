import logging
import time

def parse(commands,callback,channel,user):	
	if 'info' in commands:
		callback.msg(user['alert_channel'],'%s, Follow: %s' % (user['name'],str(user['follow'])))
		callback.msg(user['alert_channel'],'%s, Alert channel: %s' % (user['name'],user['alert_channel']))
	elif 'follow' in commands:
		if user['follow']:
			callback.msg(channel,'%s, I will no longer follow you.' % (user['name']))
			user['follow'] = False
		else:
			callback.msg(channel,'%s, I will follow you.' % (user['name']))
			user['follow'] = True
	elif commands[0] == 'load' and len(commands)==2:
		try:
			if callback.has_module(commands[1]):
				callback.msg(channel,'%s: Module \'%s\' already loaded' % (user['name'],commands[1]))
			else:
				exec('import %s as temp' % (commands[1]))
				callback.add_module(commands[1],temp)
				callback.msg(channel,'%s: Loaded module %s' % (user['name'],commands[1]))
		except ImportError:
			callback.msg(channel,'%s: Could not load module %s' % (user['name'],commands[1]))
			logging.error('No module named \'%s\'' % commands[1])