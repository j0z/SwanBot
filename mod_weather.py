import feedparser

def tick(user,callback):
	pass

def get_weather(zip):	
	_feed = feedparser.parse('http://rss.wunderground.com/auto/rss_full/%s' % zip)
	
	try:
		return str(_feed.entries[0].title)
	except:
		return 'Invalid ZIP'

def parse(commands,callback,channel,user):
	if commands[0] == 'weather' and len(commands)==2:
		callback.msg(channel,'%s: %s' %
			(user['name'],
			get_weather(commands[1])))

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass