import BeautifulSoup
import urllib
import re

__parse_always__ = True
__url_re__ = '(?:http://|www.)[^"]+'

def get_title(url):
	soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(url))
	
	try:
		return soup.title.string.strip().rstrip().replace('&nbsp;',' ').replace('\n',' ')\
			.replace('       ',' ').replace('&quot;','"')
	except:
		return 'Page not found!'

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	for result in re.finditer(__url_re__,' '.join(commands)):
		callback.msg(channel,'%s - %s' % (result.group(0),get_title(result.group(0))))

def on_user_join(user,channel,callback):	
	pass

def on_user_part(user,channel,callback):
	pass
