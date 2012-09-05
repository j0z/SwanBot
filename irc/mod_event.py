def tick(callback):
	pass

def user_tick(user,callback):
	pass

def add_event(user,when,event):
	if not user.has_key('events'):
		user['events'] = []
	
	user['events'].append({'event':event,
		'when':when})

def check_event(user,channel,event,callback):
	for _user in callback.get_users():
		if _user['name'] == user and _user.has_key('events'):
			for _event in _user['events']:
				if _event['when'] == event:
					callback.msg(channel,str(_event['event']))

def get_events(user,callback):
	_had_event = False
	
	if not user.has_key('events'):
		return 1
	
	for event in user['events']:
		callback.msg(user['name'],'%s: %s' %
			(str(event['when']),str(event['event'])))
		_had_event = True

	if not _had_event:
		callback.msg(user['name'],'You have no events.')

def delete_event(user,number,callback):	
	number = int(number)
	
	if not user.has_key('events') or 0 >= number or number > len(user['events']):
		return 1
	
	user['events'].pop(number-1)
	
	callback.msg(user['name'],'event deleted!')

def parse(commands,callback,channel,user):
	if commands[0] == 'event' and len(commands)>=2:
		if (len(commands)>=4 and commands[1] in ['add','create']):
			add_event(user,commands[2],' '.join(commands[3:]))
			callback.msg(user['name'],'%s, event added!' % user['name'])
		elif commands[1] == 'list':
			get_events(user,callback)
		elif commands[1] == 'delete' and len(commands)==3:
			delete_event(user,commands[2],callback)

def on_user_join(user,channel,callback):
	check_event(user,channel,'join',callback)

def on_user_part(user,channel,callback):
	check_event(user,channel,'part',callback)
	