import feedparser

__keyphrases__ = [{'command':'weather',
	'needs':['weather','\d{5}'],
	'keywords':['check','what\'s','like','in']}]

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def get_weather(zip):	
	_feed = feedparser.parse('http://rss.wunderground.com/auto/rss_full/%s' % zip)
	
	try:
		return str(_feed.entries[0].title)
	except:
		return 'Invalid ZIP'

def parse(commands,callback,channel,user):
	if commands[0] in ['.w','weather'] and len(commands)==2:
		callback.msg(channel,'%s' %
			get_weather(commands[1]),to=user['name'])

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass