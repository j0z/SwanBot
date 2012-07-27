import feedparser

__keyphrases__ = [{'command':'weather',
	'needs':
		[{'match':'weather','required':True},
		{'match':'\d{5}','required':False}],
	'keywords':['check','what\'s','like','in']},
	{'command':'forecast',
	'needs':
		[{'match':'forecast','required':True},
		{'match':'\d{5}','required':False}],
	'keywords':['check','what\'s','like','in']},
	{'command':'tonight',
	'needs':
		[{'match':'tonight','required':True},
		{'match':'\d{5}','required':False}],
	'keywords':['weather','check','what\'s','like','in']},
	{'command':'tomorrow',
	'needs':
		[{'match':'tomorrow','required':True},
		{'match':'\d{5}','required':False}],
	'keywords':['weather','check','what\'s','like','in']},
	{'command':'advisories',
	'needs':
		[{'match':'advisories','required':True},
		{'match':'\d{5}','required':False}],
	'keywords':['weather','check','what\'s','like','in']}
	]

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
	
	return 'Forecast for %s, %s: %s - %s' % (_city,_state,_text,_feed.entries[0].link)

def get_forecast_tonight(zip):
	_feed = get_feed(zip)
	
	_city = _feed.entries[2].link.rpartition('/')[2].rpartition('.html')[0]
	_state = _feed.entries[2].link.rpartition('/')[0].rpartition('/')[2]
	_text = _feed.entries[2].description.partition('- ')[2]
	
	return 'Tonight\'s forecast for %s, %s: %s - %s' % (_city,_state,_text,_feed.entries[0].link)

def get_forecast_tomorrow(zip):
	_feed = get_feed(zip)
	
	_city = _feed.entries[3].link.rpartition('/')[2].rpartition('.html')[0]
	_state = _feed.entries[3].link.rpartition('/')[0].rpartition('/')[2]
	_text = _feed.entries[3].description.partition('- ')[2]
	
	return 'Tomorrow\'s forecast for %s, %s: %s - %s' % (_city,_state,_text,_feed.entries[0].link)

def get_advisories(zip):
	_feed = get_feed(zip)
	_warnings = ''
	
	for entry in _feed.entries[4:]:
		_title = entry.title.partition(' - ')
		_what = _title[0]
		_when = _title[2]
		
		if not len(_warnings):
			_warnings += '%s (%s)' % (_what,_when)
		else:
			_warnings += ' - %s (%s)' % (_what,_when)
	
	_city = _feed.entries[1].link.rpartition('/')[2].rpartition('.html')[0]
	_state = _feed.entries[1].link.rpartition('/')[0].rpartition('/')[2]
	
	return 'Weather advisories for %s, %s: %s' % (_city,_state,_warnings)

def parse(commands,callback,channel,user):
	if not user.has_key('weather'):
		user['weather'] = {}
	
	if commands[0] in ['.w','weather']:
		if len(commands)==2:
			_zip = commands[1]
		elif user['weather'].has_key('zipcode'):
			_zip = user['weather']['zipcode']
		
		callback.msg(channel,'%s' %
			get_weather(_zip),to=user['name'])
	
	elif commands[0] in ['.wf','forecast']:
		if len(commands)==2:
			_zip = commands[1]
		elif user['weather'].has_key('zipcode'):
			_zip = user['weather']['zipcode']
		
		callback.msg(channel,'%s' %
			get_forecast(_zip),to=user['name'])
	
	elif commands[0] in ['.wt','tonight']:
		if len(commands)==2:
			_zip = commands[1]
		elif user['weather'].has_key('zipcode'):
			_zip = user['weather']['zipcode']
		
		callback.msg(channel,'%s' %
			get_forecast_tonight(_zip),to=user['name'])
	
	elif commands[0] in ['.wf','tomorrow']:
		if len(commands)==2:
			_zip = commands[1]
		elif user['weather'].has_key('zipcode'):
			_zip = user['weather']['zipcode']
		
		callback.msg(channel,'%s' %
			get_forecast_tomorrow(_zip),to=user['name'])
	
	elif commands[0] in ['.wa','advisories']:
		if len(commands)==2:
			_zip = commands[1]
		elif user['weather'].has_key('zipcode'):
			_zip = user['weather']['zipcode']
		
		callback.msg(channel,'%s' %
			get_advisories(_zip),to=user['name'])
	else:
		return 0
	
	if len(commands)==2:
		user['weather']['zipcode'] = commands[1]

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass