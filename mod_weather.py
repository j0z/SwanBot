import feedparser

def tick(user,callback):
	pass

def get_weather(zip):	
	_feed = feedparser.parse('http://rss.wunderground.com/auto/rss_full/%s' % zip)
	return _feed.entries[0].title.rpartition('Current Conditions : ')[2]

def parse(commands,callback,channel,user):
	if commands[0] == 'weather' and len(commands)==2:
		callback.msg(channel,'%s: Weather for %s: %s' %
			(user['name'],
			commands[1]),
			get_weather(commands[1]))
		add_mail(user,commands[1],commands[2:])

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass