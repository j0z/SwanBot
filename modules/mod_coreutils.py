#This module provides a few core features,
#like schedules. It's mostly just for example,
#though.

import feedparser
import datetime
import logging

#Runs every second. Get access to all public nodes.
def tick(public_nodes,callback):
	_calendars = []

	#Check for any calendar nodes
	for user in public_nodes:
		for node in user['nodes']:
			if node['type'] == 'calendar':
				_calendars.append({'user':user['name'],
				                   'calendar':node['url']})

	for calendar in _calendars:
		_user = callback.get_user_from_name(calendar['user'])
		_events = get_todays_events_from_calendar(calendar['calendar'])

		for event in _events:
			if callback.find_nodes(_user,{'type':'calendar_event','title':event['title']}):
				continue
			else:
				callback.create_node_from_payload(_user,{'type':'calendar_event','title':event['title'],
				                                   'starts':event['starts'],'ends':event['ends']})
				logging.info('Added new calendar item for user \'%s\'' % calendar['user'])

#Parses incoming date/time strings from calendar entries.
#TODO: Do this.
def parse_time_string(time):
	pass

#Parses a calendar event, returns JSON object.
def parse_calendar_entry(entry):
	_entry = {}
	_entry['title'] = entry['title'].encode('utf8')
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
			_entry['ends'] = datetime.datetime.strptime(_end_time,'%I:%M%p')
		elif _end_time.count(',') and _end_time.count(':'):
			_entry['ends'] = datetime.datetime.strptime(_end_time,'%a %b %d, %Y %I:%M%p')
		elif _end_time.count(','):
			_entry['ends'] = datetime.datetime.strptime(_end_time,'%a %b %d, %Y %I%p')
		elif _end_time.count('AM') or _end_time.count('PM'):
			_entry['ends'] = datetime.datetime.strptime(_end_time,'%I%p')
		else:
			_entry['ends'] = datetime.datetime.strptime(_end_time,'%I%p')

	else:
		_entry['ends'] = None

	if _start_time.count(':'):
		_entry['starts'] = datetime.datetime.strptime(_start_time,'%a %b %d, %Y %I:%M%p')
	elif _start_time.count('AM') or _start_time.count('PM'):
		_entry['starts'] = datetime.datetime.strptime(_start_time,'%a %b %d, %Y %I%p')
	else:
		_entry['starts'] = datetime.datetime.strptime(_start_time,'%a %b %d, %Y')

	if _entry['ends']:
		_entry['ends'] = _entry['ends'].replace(month=_entry['starts'].month)
		_entry['ends'] = _entry['ends'].replace(day=_entry['starts'].day)
		_entry['ends'] = _entry['ends'].replace(year=_entry['starts'].year)

	return _entry

def calendar_entry_to_string(entry):
	_start_time_string = str(entry['starts'])
	_end_time_string = str(entry['ends'])

	return {'title':entry['title'],'starts':_start_time_string,'ends':_end_time_string}

#Parses a Google Calendar.
def get_todays_events_from_calendar(url):
	_feed = feedparser.parse(url)
	_todays_date = datetime.datetime.today()
	_entries = []

	for entry in _feed.entries:
		_parsed_entry = parse_calendar_entry(entry)
		_string_entry = calendar_entry_to_string(_parsed_entry)

		if _parsed_entry['starts'].year == _todays_date.year and\
		   _parsed_entry['starts'].day == _todays_date.day and\
		   _parsed_entry['starts'].month == _todays_date.month:
			_entries.append(_string_entry)

	return _entries

def get_this_weeks_events_from_calendar(url):
	_feed = feedparser.parse(url)
	_todays_date = datetime.datetime.today()
	_todays_date += datetime.timedelta(days=7)
	_entries = []

	for entry in _feed.entries:
		_parsed_entry = parse_calendar_entry(entry)

		if _parsed_entry['starts'].year == _todays_date.year and\
		   0<_todays_date.day-_parsed_entry['starts'].day<=7 and\
		   _parsed_entry['starts'].month >= _todays_date.month:
			_entries.append(_parsed_entry)

	return _entries

#url =
#get_this_weeks_events_from_calendar(url)


