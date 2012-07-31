import logging
import time

def parse(commands,callback,channel,user):
	if not user['name'] == callback.owner:
		return 1
	
	if 'info' in commands:
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
	elif commands[0] == 'join' and len(commands)>=2:
		if len(commands)>2:
			callback.join(commands[1],key=' '.join(commands[2:]))
		else:
			callback.join(commands[1])
		
		callback.msg(user['name'],'Trying to join %s' % commands[1],to=user['name'])
	elif commands[0] in ['leave','part'] and len(commands)>=2:
		if len(commands)>2:
			callback.part(commands[1],reason=' '.join(commands[2:]))
		else:
			callback.part(commands[1],reason='Part issued by %s' % user['name'])
		
		callback.msg(user['name'],'Left %s' % commands[1],to=user['name'])
	
	elif commands[0] == 'cycle' and len(commands)>=2:
		if len(commands)>2:
			callback.part(commands[1],reason=' '.join(commands[2:]))
			callback.join(commands[1],key=' '.join(commands[2:]))
		else:
			callback.part(commands[1],reason='Part issued by %s' % user['name'])
			callback.join(commands[1])
		
		callback.msg(user['name'],'Cycling %s' % commands[1],to=user['name'])
	
	elif commands[0] == 'set':
		if len(commands)==3 and commands[1] == 'fallback':			
			for _user in callback.get_users():
				if not _user['name'] == commands[2]:
					continue
				
				_user['fallback_owner'] = True
				callback.fallback_owner = commands[2]
				callback.msg(user['name'],'Set fallback_owner to %s' % commands[2],to=user['name'])
				callback.msg(commands[2],'You are now the fallback owner of this bot.',to=user['name'])
				break
			