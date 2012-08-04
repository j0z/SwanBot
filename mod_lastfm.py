import feedparser

__url__ = 'http://ws.audioscrobbler.com/1.0/user/%user%/recenttracks.rss'

def get_playing(user):
	url = __url__.replace('%user%',user)
	soup = feedparser.parse(url)
	
	try:
		return 'Last played: %s' % soup.entries[0].title.replace(u'\u2013','-')
	except:
		return 'Error!'

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	if not user.has_key('last_fm'):
		user['last_fm'] = None
	
	if commands[0] == '.lastfm' and len(commands)==2:
		user['last_fm'] = commands[1]
		callback.msg(channel,get_playing(commands[1]),to=user['name'])
	elif commands[0] == '.lastfm' and len(commands)==1:
		if user['last_fm']:
			callback.msg(channel,get_playing(user['last_fm']),to=user['name'])
		else:
			callback.msg(user['name'],'Your last.fm ID is not set! Use: .lastfm <name>',to=user['name'])

def on_user_join(user,channel,callback):	
	pass

def on_user_part(user,channel,callback):
	pass