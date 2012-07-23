import time

def tick(callback):
	pass

def user_tick(user,callback):
	_curr_time = time.strptime(time.ctime())
	
	if user.has_key('alarms'):
		for alarm in user['alarms']:
			_time = time.strptime(alarm['when'],'%H:%M')
			if _time.tm_hour <= _curr_time.tm_hour and _time.tm_min <= _curr_time.tm_min:
				user['alarms'].remove(alarm)
				
				if callback:
					callback.msg(user['alert_channel'],
						'%s: %s' % (user['name'],str(alarm['what'])))

def add_alarm(user,when,what='Ding ding! Alarm is done.'):
	if not user.has_key('alarms'):
		user['alarms'] = []
	
	user['alarms'].append({'when':when,'what':what})

def parse(commands,callback,channel,user):
	if commands[0] == 'alarm' and len(commands)>=3:
		if commands[1] == 'set':
			if len(commands)>3:
				_what = ' '.join(commands[3:])
				add_alarm(user,commands[2],what=_what)
				callback.msg(channel,'%s: Alarm set for %s (%s)' % (user['name'],commands[2],_what))
			else:
				add_alarm(user,commands[2])
				callback.msg(channel,'%s: Alarm set for %s' % (user['name'],commands[2]))

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass