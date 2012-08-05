#If you're reading this, know that this module is a huge work-in-progress
#and uses a lot of weird/unconventional methods to figure out the topic
#being discussed. I feel the need to say something because there are probably
#algorithms out there to do this already, but I believe the following things:
#	+ The language used in most IRC channels is largely informal jargon,
#	  meaning there is a lot of data that needs to be thrown out.
#	+ In busier channels, mutiple conversations can be held at the same time,
#	  meaning the inputed data could be valuable to some and meaningless
#	  to others.
#I feel that a lot of these things wouldn't be covered in any existing methods.
#If you feel that I'm wrong, please message me via Github, otherwise I have
#prepared what I believe to be a more useful and efficient way of handling
#the first issue.
#As for the second problem I mentioned... there really isn't a way to handle it.
#I suppose you could track the users involved in a conversation but I find that
#to be useless for the most part, as uninvolved users will still see the outputted
#text from the bot.
#That, and I don't participate in any of these busy channels, so I'm unaware
#as to what data is garbage and what isn't.
#I welcome any info/thoughts you might have if you are more experienced in
#anything I've mentioned.

import logging
import urllib
import json
import re
import os

__parse_always__ = True
__search_url__ = 'https://www.googleapis.com/freebase/v1/text/en/%search%'
__research_url__ = 'https://www.googleapis.com/freebase/v1/search?query=%search%'
__info_url__ = 'https://www.googleapis.com/freebase/v1/text/%mid%'
__ignore__ = ['after','although','though','because','before','once','since','than',
	'that','though','till','unless','until','when','whenever','where','wherever',
	'while','the','this']

def init():
	global words_db
	words_db = {'words':[]}
	
	try:
		_file = open(os.path.join('data','words.json'),'r')
		words_db = json.loads(_file.readline())
		
		for entry in words_db['words']:
			for key in entry:
				if isinstance(entry[key],unicode):
					entry[key] = entry[key].encode("utf-8")
		
		_file.close()
		words_db = words_db['words']
		logging.info('Success!')
	except:
		logging.error('Could not load words database from disk!')
		_file = open(os.path.join('data','words.json'),'w')
		_file.write(json.dumps(words_db))
		_file.close()
		init()

def shutdown():
	logging.info('Offloading words database to disk...')
	_file = open(os.path.join('data','words.json'),'w')
	_file.write(json.dumps({'words':words_db}))
	_file.close()
	logging.info('Success!')

def get_info(mid):
	try:
		_result = json.loads(urllib.urlopen(__info_url__.replace('%mid%',mid)
			.replace(' ','_')).read())
	except:
		return 'Search returned nothing.'
	
	try:
		return _result['result'].encode("utf-8")
	except:
		return 'Search returned nothing.'


def perform_search(query):
	try:
		_result = json.loads(urllib.urlopen(__search_url__.replace('%search%',query.lower())
			.replace(' ','_')).read())
	except:
		return 'Search returned nothing.'
	
	try:
		return _result['result'].encode("utf-8")
	except:
		return 'Search returned nothing.'

def research_topic(topic):
	try:
		_result = json.loads(urllib.urlopen(__research_url__.replace('%search%',topic.lower())
			.replace(' ','_')).read())
	except:
		return None
	
	_result = _result['result'][0]
	
	if _result['score']<50:
		return None
	
	return _result

def add_word(word,score=1):
	word = word.lower()
	for char in ['.',',',';',':','\'','|',')','(','>','<']:
		word = word.replace(char,'')
	
	word = word.replace(' ','')
	
	_len = len(word)
	if not _len or _len<=3:
		return None
	
	if word in __ignore__:
		print 'Discarding \'%s\'' % word
		return None
	
	_words = [{entry['word']:entry} for entry in words_db]
	
	for _word in _words:
		if word in _word.keys():
			_word[word]['score']+=score
			return _word[word]

	words_db.append({'word':word,'score':score})
	return words_db[len(words_db)-1]

def get_topics():
	_third = {'word':None,'score':0}
	_second = {'word':None,'score':0}
	_highest = {'word':None,'score':0}
	
	for entry in words_db:
		if entry['score']>_highest['score']:
			_highest = entry.copy()
		elif entry['score']>_second['score']:
			_second = entry.copy()
		elif entry['score']>_third['score']:
			_third = entry.copy()
	
	if _highest['word']:
		return [_highest,_second,_third]
	
	return 'No topic could be found.'

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	if commands[0] == '.search' and len(commands)>=2:
		callback.msg(channel,'Result: %s' % (perform_search(' '.join(commands[1:]))),to=user['name'])
		
		for word in commands[1:]:
			add_word(word,score=10)
		
		return 1
	elif commands[0] == '.topic':
		_topics = get_topics()
		
		for _topic in _topics[:2]:
			callback.msg(channel,'Topic: %s (%s)' % (_topic['word'],_topic['score']),to=user['name'])
		
		return 1
	elif commands[0] == '.topic_ext':
		_combined_topics = None
		_res_combined = None
		_res_topic = None
		_topics = get_topics()
		
		if _topics == 'No topic could be found.':
			print 'No topic!'
			return 1
		
		#Sometimes combining the first two topics can give us a better result
		if len(_topics)>=2 and _topics[1]['word']:
			_combined_topic = ' '.join([topic['word'] for topic in _topics[:2]])
			_res_combined = research_topic(_combined_topic)
			
			if _res_combined:
				callback.msg(channel,'Combined topic: %s (%s)' % (_combined_topic,_res_combined['score']),
					to=user['name'])
		
		_res = research_topic(_topics[0]['word'])
		if _res:
			callback.msg(channel,'Single topic: %s (%s)' % (_topics[0]['word'],_res['score']),
				to=user['name'])
		
		if _res and _res_combined and _res['score']>_res_combined['score']:
			callback.msg(channel,'Single: %s' % get_info(_res['mid']),to=user['name'])
		elif _res and _res_combined and _res['score']<_res_combined['score']:
			callback.msg(channel,'Combined: %s' % get_info(_res_combined['mid']),to=user['name'])
		else:
			callback.msg(channel,'Not a valid topic: %s' % _topics[0]['word'],to=user['name'])
			add_word(_topics[0]['word'],score=-50)
		
		return 1
	elif commands[0] == '.topic_ban' and len(commands)==2:
		add_word(commands[1],score=-50)
		return 1
	
	for word in commands[0:]:
		if word.istitle() and not ' '.join(commands[0:]).count('. %s' % word) and commands.index(word):
			_score = 5
		else:
			_score = 1
		
		_ret = add_word(word,score=_score)
		
		#if _ret:
		#	print _ret['word'],_ret['score']

def on_user_join(user,channel,callback):	
	pass

def on_user_part(user,channel,callback):
	pass