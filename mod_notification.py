__keyphrases__ = [{'command':'growl',
	'needs':
		[{'match':'growl','required':True},
		{'match':'on','required':False},
		{'match':'off','required':False},
		{'match':'join','required':False},
		{'match':'message','required':False},
		{'match':'highlight','required':False},
		{'match':'mention','required':False},
		{'match':'ip','required':False},
		{'match':'host','required':False},
		{'match':'\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b','required':False}],
	'keywords':['turn','notifications']}]

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	if not user.has_key('notify_on'):
		user['notify_on'] = []
		user['growl_host'] = None
	
	if commands[0] == 'growl' and len(commands)==3:
		if commands[1] == 'on':
			if not commands[2] in user['notify_on']:
				user['notify_on'].append(commands[2])
				callback.msg(channel,'I will notify you if this event occurs: %s ' %
					commands[2],to=user['name'])
			else:
				callback.msg(channel,'You are already being notified for this event: %s ' %
					commands[2],to=user['name'])
		elif commands[1] == 'off':
			if not commands[2] in user['notify_on']:
				callback.msg(channel,'You are not currently being notified for this event: %s ' %
					commands[2],to=user['name'])
			else:
				user['notify_on'].remove(commands[2])
				callback.msg(channel,'You will no longer be notified for this event: %s ' %
					commands[2],to=user['name'])
		elif commands[1] in ['host','ip']:
			user['growl_host'] = commands[2]
			callback.msg(channel,'Growl IP set: %s ' %
					commands[2],to=user['name'])
	
	for _user in callback.get_users():
		if not _user.has_key('notify_on'):
			_user['notify_on'] = []
			_user['growl_host'] = None
			continue
		
		if not _user['growl_host'] and _user['notify_on']:
			callback.msg(_user['name'],'Please configure your growl IP! Message: growl ip <ip>',
				to=_user['name'])
			continue
		
		if 'message' in _user['notify_on'] and not _user['name']==user['name']:
			callback.notify('%s - %s' % (channel,user['name']),' '.join(commands),
				hostname=_user['growl_host'])
		elif 'highlight' in _user['notify_on'] or 'mention' in _user['notify_on']:
			if _user['name'] in commands:
				callback.notify('%s - %s' % (channel,user['name']),' '.join(commands),
					hostname=_user['growl_host'])

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass