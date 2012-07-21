import time

def add_alarm(user,when,what='Ding ding! Alarm is done.'):
	if not user.has_key('alarms'):
		user['alarms'] = []
	
	user['alarms'].append({'when':when,'what':what})

def parse(commands,callback,channel,user):
	#if user['alert_channel']:
	_channel = user['alert_channel']
	
	if 'info' in commands:
		callback.msg(user['alert_channel'],'%s, Follow: %s' % (user['name'],str(user['follow'])))
		callback.msg(user['alert_channel'],'%s, Alert channel: %s' % (user['name'],user['alert_channel']))
	elif 'follow' in commands:
		if user['follow']:
			callback.msg(_channel,'%s, I will no longer follow you.' % (user['name']))
			user['follow'] = False
		else:
			callback.msg(_channel,'%s, I will follow you.' % (user['name']))
			user['follow'] = True
	elif commands[0] == 'alarm' and len(commands)>=3:
		if commands[1] == 'set':
			if len(commands)>3:
				_what = ' '.join(commands[3:])
				add_alarm(user,commands[2],what=_what)
				callback.msg(_channel,'%s: Alarm set for %s (%s)' % (user['name'],commands[2],_what))
			else:
				add_alarm(user,commands[2])
				callback.msg(_channel,'%s: Alarm set for %s' % (user['name'],commands[2]))
			