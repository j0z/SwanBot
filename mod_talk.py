__keyphrases__ = [{'command':'nope',
	'needs':
		[{'match':'placeholder','required':True}],
	'keywords':['turn','notifications']}]

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):	
	if channel in callback.factory.channels:
		return 1

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass