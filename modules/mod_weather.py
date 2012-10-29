#Weather forecast
#By flags - jetstarforever@gmail.com
#
#Required nodes:
#	Type 'location' with a key,value of 'zipcode',zipcode
#
#Created nodes:
#	Type 'weather' with keys 'temperature','forecast'

import feedparser

WAIT_TIME_MAX = 10
WAIT_TIME = 0

def tick(users,callback):
	for user in users:
		_user = callback.get_user_from_name(user['name'])
		
		for node in user['nodes']:
			if node['type'] == 'location':
				#TODO: Does this key exist?
				_zip_code = node['zipcode']
				