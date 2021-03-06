__keyphrases__ = [{'command':'aop',
	'needs':
		[{'match':'aop','required':True},
		{'match':'%user%','required':True}],
	'keywords':['add','to','the','list']},
	{'command':'avoice',
	'needs':
		[{'match':'avoice','required':True},
		{'match':'%user%','required':True}],
	'keywords':['add','to','the','list']},
	{'command':'dop',
	'needs':
		[{'match':'dop','required':True},
		{'match':'%user%','required':True}],
	'keywords':['remove','add','to','the','list']}]

__chanserv__ = {'auto_mode':0,'auto_kick':[]}

def tick(callback):
	pass

def user_tick(user,callback):
	if not user.has_key('chanserv'):
		user['chanserv'] = __chanserv__.copy()

def on_user_in_channel(channel,user,callback):
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

def parse(commands,callback,channel,user):
	if not callback.owner == user['name']:
		return 0
	
	if not user.has_key('chanserv'):
		user['chanserv'] = __chanserv__.copy()
	
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

def on_nick_change(old_nick,new_nick,callback):
	for _user in callback.get_users():
		if _user['name']==new_nick and _user['chanserv']['auto_mode']:
			for channel in callback.factory.channels:
				if _user['chanserv']['auto_mode']==0:
					callback.mode(channel,False,'o',user=new_nick)
					callback.mode(channel,False,'v',user=new_nick)
				elif _user['chanserv']['auto_mode']==1:
					callback.mode(channel,True,'o',user=new_nick)
				elif _user['chanserv']['auto_mode']==2:
					callback.mode(channel,True,'v',user=new_nick)
				elif _user['chanserv']['auto_mode']==3 and channel in _user['chanserv']['auto_kick']:
					callback.kick(channel,new_nick,reason='Autokick')
			
			return 0

def on_user_part(user,channel,callback):
	pass
