import time

#Found this on StackExchange and adapted it to Python.
#http://stackoverflow.com/a/165745
daySuffix = ['th','st','nd','rd','th',
		'th','th','th','th','th'];

def node_to_speech(node):
	_speech_node = {'type':'speech','text':'Unparsed','public':True}
	
	if node['type'] == 'calendar_event':
		_start_time = time.strptime(node['starts'], '%Y-%m-%d %H:%M:%S')
		_day_name = time.strftime('%A',_start_time)
		
		_day = time.strftime('%d',_start_time)
		if _day % 100 >= 11 and _day % 100 <= 13:
			_day += 'th';
		else:
			_day += daySuffix[int(_day) % 10];		
		
		_title = node['title']
		
		_speech_node['text'] = '%s the %s, %s.' % \
			(_day_name,_day,_title)
	
	return _speech_node