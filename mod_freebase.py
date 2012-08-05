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
__ignore__ = ['for','and','nor','but','or','yet','so','after','although','as',
	'though','because','before','if','once','since','than','that','though','till'
	'unless','until','when','whenever','where','wherever','while','the','i']

words_db = []

def init():
	global words_db
	
	try:
		_file = open(os.path.join('data','words.json'),'r')
		words_db = json.loads(_file.readline())
		
		for entry in words_db['words']:
			for key in entry:
				if isinstance(entry[key],unicode):
					entry[key] = str(entry[key])
		
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
		print __research_url__.replace('%search%',topic.lower())
		return None
	
	_result = _result['result'][0]
	
	if _result['score']<50:
		return None
	
	return _result

def add_word(word,score=1):
	word = word.lower().replace(',','').replace('.','').replace(';','')
	
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

def get_topic():
	_highest = {'word':None,'score':0}
	
	for entry in words_db:
		if entry['score']>_highest['score']:
			_highest['word'] = entry['word']
			_highest['score'] = entry['score']
	
	if _highest['word']:
		print _highest['score']
		return _highest['word']
	
	return 'No topic could be found.'

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	if commands[0] == '.search' and len(commands)>=2:
		callback.msg(channel,'Result: %s' % (perform_search(' '.join(commands[1:]))),to=user['name'])
		
		#Since we are explicitly telling SwanBot to look up this term,
		#we should weight it a bit heavier.
		for word in commands[1:]:
			add_word(word,score=10)
		
		return 1
	elif commands[0] == '.topic':
		_topic = get_topic()
		callback.msg(channel,'Topic: %s' % _topic,to=user['name'])
		return 1
	elif commands[0] == '.topic_ext':
		_topic = get_topic()
		callback.msg(channel,'Topic: %s' % _topic,to=user['name'])
		
		if _topic == 'No topic could be found.':
			print 'No topic!'
			return 1
		
		_res = research_topic(_topic)
		
		if _res:
			callback.msg(channel,'Result: %s' % get_info(_res['mid']),to=user['name'])
		else:
			print 'Not a valid topic. Resetting.'
			add_word(_topic,score=-50)
		
		return 1
	
	for word in commands[0:]:
		if word.istitle() and not ' '.join(commands[0:]).count('. %s' % word) and commands.index(word):
			_score = 5
		else:
			_score = 1
		
		_ret = add_word(word,score=_score)
		
		if _ret:
			print _ret['word'],_ret['score']

def on_user_join(user,channel,callback):	
	pass

def on_user_part(user,channel,callback):
	pass