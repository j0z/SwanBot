__stats__ = {'seconds_online':0,'lines':0,'joins':0,'parts':0}

def tick(callback):
	pass

def user_tick(user,callback):
	if not user.has_key('stats'):
		user['stats'] = __stats__.copy()
	
	user['stats']['seconds_online']+=1

def parse(commands,callback,channel,user):
	if not user.has_key('stats'):
		user['stats'] = __stats__.copy()
	
	user['stats']['lines']+=1
	
	if commands[0] == 'stats':
		for key in user['stats']:
			callback.msg(channel,'%s, %s: %s' %
				(user['name'],str(key),user['stats'][key]))

def on_user_join(user,channel,callback):
	for _user in callback.get_users():
		if _user['name']==user:
			_user['stats']['joins']+=1
			return 0

def on_user_part(user,channel,callback):
	for _user in callback.get_users():
		if _user['name']==user:
			_user['stats']['parts']+=1
			return 0
