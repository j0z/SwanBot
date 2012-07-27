import logging
import time

def parse(commands,callback,channel,user):	
	if 'info' in commands:
		callback.msg(user['alert_channel'],'%s, Follow: %s' % (user['name'],str(user['follow'])))
		callback.msg(user['alert_channel'],'%s, Alert channel: %s' % (user['name'],user['alert_channel']))
		callback.msg(user['alert_channel'],'%s, I am running the following modules: %s'
			% (user['name'],', '.join(m['name'] for m in callback.modules)))
	
	elif commands[0] == 'load' and len(commands)==2:
		try:
			if callback.has_module(commands[1]):
				callback.msg(channel,'%s: Module \'%s\' already loaded' % (user['name'],commands[1]))
			else:
				callback.add_module(commands[1])
				callback.msg(channel,'%s: Loaded module %s' % (user['name'],commands[1]))
		except ImportError:
			callback.msg(channel,'%s: Could not load module %s' % (user['name'],commands[1]))
			logging.error('No module named \'%s\'' % commands[1])
	elif commands[0] == 'force-register' and len(commands)==2:
		callback.register_user(commands[1],'')
		callback.msg(channel,'%s: Tried to register %s' % (user['name'],commands[1]))