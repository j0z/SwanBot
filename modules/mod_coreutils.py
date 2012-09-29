#This module provides a few core features,
#like schedules. It's mostly just for example,
#though.

import feedparser
from datetime import datetime
import time

#Runs every second. Get access to all public nodes.
def tick(public_nodes):
	print public_nodes

#Parses a calendar event, returns JSON string.
def parse_calendar_entry(entry):
	_entry = {}
	_entry['title'] = entry['title']
	_start_time = entry['content'][0]['value']\
	                 .partition('When: ')[2]\
	                 .partition('<br />')[0]\
					 .replace('\n','')

	_start_time = _start_time.encode('utf8').replace('\xc2\xa0',' ')
	_start_time = _start_time.replace('pm','PM').replace('am','AM')

	if _start_time.count(' to '):
		_end_time = _start_time.partition('to ')[2]
		_start_time = _start_time.partition(' to')[0]

		_end_time = ''.join(_end_time.partition('AM')[:2])
		_end_time = ''.join(_end_time.partition('PM')[:2])

		if _end_time.count(':'):
			_entry['ends'] = datetime.strptime(_end_time,'%I:%M%p')
		elif _end_time.count(',') and _end_time.count(':'):
			_entry['ends'] = datetime.strptime(_end_time,'%a %b %d, %Y %I:%M%p')
		elif _end_time.count(','):
			_entry['ends'] = datetime.strptime(_end_time,'%a %b %d, %Y %I%p')
		elif _end_time.count('AM') or _end_time.count('PM'):
			_entry['ends'] = datetime.strptime(_end_time,'%I%p')
		else:
			_entry['ends'] = datetime.strptime(_end_time,'%I%p')

	else:
		_entry['ends'] = None

	if _start_time.count(':'):# and (_start_time.count('am') or _start_time.count('pm')):
		_entry['starts'] = datetime.strptime(_start_time,'%a %b %d, %Y %I:%M%p')
	elif _start_time.count('AM') or _start_time.count('PM'):
		_entry['starts'] = datetime.strptime(_start_time,'%a %b %d, %Y %I%p')
	else:
		_entry['starts'] = datetime.strptime(_start_time,'%a %b %d, %Y')

	#datetime.strptime()

	return _entry

#Parses a Google Calendar.
def get_todays_events_from_calendar(url):
	_feed = feedparser.parse(url)

	for entry in _feed.entries:
		_parsed_entry = parse_calendar_entry(entry)
		print _parsed_entry['starts'],_parsed_entry['ends']


url = 'https://www.google.com/calendar/feeds/jetstarforever%40gmail.com/private-0b5d9ebe10bade7630eda7b436678e8c/basic'

get_todays_events_from_calendar(url)


