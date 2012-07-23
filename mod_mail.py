import time

def tick(user,callback):
	_curr_time = time.strptime(time.ctime())
	
	if user.has_key('messages'):
		pass

def add_mail(user,who,message):
	if not user.has_key('messages'):
		user['messages'] = []
	
	user['messages'].append({'to':who,
		'message':' '.join(message),
		'when':time.strftime('%A, %B %d at %H:%M')})

def get_mail(user,callback):
	_had_mail = False
	
	for _user in callback.get_users():
		if _user.has_key('messages'):
			for message in _user['messages']:
				if message['to'] == user:
					callback.msg(user,'Private message from %s sent %s: %s' %
						(_user['name'],str(message['when']),str(message['message'])))
					_user['messages'].remove(message)
					_had_mail = True
	
	if not _had_mail:
		callback.msg(user,'You have no mail!')

def parse(commands,callback,channel,user):
	if commands[0] == 'mail':
		if (len(commands)==2 and commands[1] in ['check','get']) or len(commands)==1:
			get_mail(user['name'],callback)
		elif len(commands)>=3:
			add_mail(user,commands[1],commands[2:])
			callback.msg(channel,'%s: Message sent to %s' % (user['name'],commands[1]))

def on_user_join(user,channel,callback):
	get_mail(user,callback)

def on_user_part(user,channel,callback):
	pass
	