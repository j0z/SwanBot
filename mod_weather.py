import feedparser

__keyphrases__ = [{'command':'weather',
	'needs':['weather','\d{5}'],
	'keywords':['check','what\'s','like','in']},
	{'command':'forecast',
	'needs':['forecast','\d{5}'],
	'keywords':['check','what\'s','like','in']},
	{'command':'tonight',
	'needs':['tonight','\d{5}','forecast'],
	'keywords':['check','what\'s','like','in']}]

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def get_feed(zip):
	_feed = feedparser.parse('http://rss.wunderground.com/auto/rss_full/%s' % zip)
	
	try:
		if str(_feed.entries[0].title):
			return _feed
	except:
		return 'Invalid ZIP'

def get_weather(zip):
	_feed = get_feed(zip)
	
	_city = _feed.entries[0].link.rpartition('/')[2].rpartition('.html')[0]
	_state = _feed.entries[0].link.rpartition('/')[0].rpartition('/')[2]
	_text = _feed.entries[0].title.replace('Current Conditions :','Weather for %s, %s:' % (_city,_state))
	
	return '%s - %s' % (_text,_feed.entries[0].link)

def get_forecast(zip):
	_feed = get_feed(zip)
	
	_city = _feed.entries[1].link.rpartition('/')[2].rpartition('.html')[0]
	_state = _feed.entries[1].link.rpartition('/')[0].rpartition('/')[2]
	_text = _feed.entries[1].description.partition('- ')[2]
	#.replace('Current Conditions :','Weather for %s, %s:' % (_city,_state))
	
	return 'Forecast for %s, %s: %s - %s' % (_city,_state,_text,_feed.entries[0].link)

def get_forecast_tonight(zip):
	_feed = get_feed(zip)
	
	_city = _feed.entries[2].link.rpartition('/')[2].rpartition('.html')[0]
	_state = _feed.entries[2].link.rpartition('/')[0].rpartition('/')[2]
	_text = _feed.entries[2].description.partition('- ')[2]
	#.replace('Current Conditions :','Weather for %s, %s:' % (_city,_state))
	
	return 'Tonight\'s forecast for %s, %s: %s - %s' % (_city,_state,_text,_feed.entries[0].link)

def parse(commands,callback,channel,user):
	if commands[0] in ['.w','weather'] and len(commands)==2:
		callback.msg(channel,'%s' %
			get_weather(commands[1]),to=user['name'])
	
	elif commands[0] in ['.wf','forecast'] and len(commands)==2:
		callback.msg(channel,'%s' %
			get_forecast(commands[1]),to=user['name'])
	
	elif commands[0] in ['.wt','tonight'] and len(commands)>=2:
		callback.msg(channel,'%s' %
			get_forecast_tonight(commands[1]),to=user['name'])

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass