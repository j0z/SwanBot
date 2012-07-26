__keyphrases__ = [{'command':'aop',
	'needs':['aop','%user%'],
	'keywords':['add','to','the','list']},
	{'command':'avoice',
	'needs':['avoice','%user%'],
	'keywords':['add','to','the','list']},
	{'command':'dop',
	'needs':['dop','%user%'],
	'keywords':['remove','add','to','the','list']}]

__chanserv__ = {'auto_mode':0,'auto_kick':[]}

def tick(callback):
	pass

def user_tick(user,callback):
	if not user.has_key('chanserv'):
		user['chanserv'] = __chanserv__.copy()

def parse(commands,callback,channel,user):
	if not callback.owner == user['name']:
		return 0
	
	if not user.has_key('chanserv'):
		user['chanserv'] = __chanserv__.copy()
	
	if not channel in callback.factory.channels:
		callback.msg(channel,'This isn\'t a channel.',to=user['name'])
		return 0
	
	if commands[0] == 'aop' and len(commands)>=2:
		for _user in callback.get_users():
			if _user['name'] == commands[1]:
				_user['chanserv']['auto_mode'] = 1
				callback.mode(channel,True,'o',user=_user['name'])
				callback.msg(channel,'aop set for %s' %
					(commands[1]),to=user['name'])
				return 0
	elif commands[0] == 'avoice' and len(commands)>=2:
		for _user in callback.get_users():
			if _user['name'] == commands[1]:
				_user['chanserv']['auto_mode'] = 2
				callback.mode(channel,True,'v',user=_user['name'])
				callback.msg(channel,'avoice set for %s' %
					(commands[1]),to=user['name'])
				return 0
	elif commands[0] in ['dop','dvoice'] and len(commands)>=2:
		for _user in callback.get_users():
			if _user['name'] == commands[1]:
				_user['chanserv']['auto_mode'] = 0
				callback.mode(channel,False,'o',user=_user['name'])
				callback.mode(channel,False,'v',user=_user['name'])
				callback.msg(channel,'auto op/voice removed for %s' %
					(commands[1]),to=user['name'])
				return 0
	elif commands[0] == 'ak' and len(commands)>=2:
		callback.register_user(commands[1],'')
		
		for _user in callback.get_users():
			if _user['name'] == commands[1]:
				if not user['last_channel'] in _user['chanserv']['auto_kick']:
					_user['chanserv']['auto_kick'].append(user['last_channel'])
				_user['chanserv']['auto_mode'] = 3
		
		callback.kick(user['last_channel'],commands[1],reason='Autokick')

def on_user_join(user,channel,callback):	
	for _user in callback.get_users():
		if _user['name']==user and _user['chanserv']['auto_mode']:
			if _user['chanserv']['auto_mode']==0:
				callback.mode(channel,False,'o',user=user)
				callback.mode(channel,False,'v',user=user)
			elif _user['chanserv']['auto_mode']==1:
				callback.mode(channel,True,'o',user=user)
			elif _user['chanserv']['auto_mode']==2:
				callback.mode(channel,True,'v',user=user)
			elif _user['chanserv']['auto_mode']==3 and channel in _user['chanserv']['auto_kick']:
				callback.kick(channel,user,reason='Autokick')
			
			return 0

def on_user_part(user,channel,callback):
	pass
