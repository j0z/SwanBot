import urllib
import json
import re

__url__ = 'https://www.googleapis.com/freebase/v1/text/en/%search%'

def get_info(query):
	_result = json.loads(urllib.urlopen(__url__.replace('%search%',query.lower())
		.replace(' ','_').replace('\n','')).read())
	
	try:
		return _result['result'].encode("utf-8")
	except:
		return 'Search returned nothing.'

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	if commands[0] == '.search' and len(commands)>=2:
		callback.msg(channel,'Result: %s' % (get_info(' '.join(commands[1:]))),to=user['name'])

def on_user_join(user,channel,callback):	
	pass

def on_user_part(user,channel,callback):
	pass
