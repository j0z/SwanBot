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

try:
	__api_key__ = '&key='+open(os.path.join('data','apikey.txt'),'r').readlines()[0]
except:
	__api_key__ = ''
	logging.info('No FreeBase API key set. Place key in data%sapikey.txt' % os.sep)

__parse_always__ = True
__search_url__ = 'https://www.googleapis.com/freebase/v1/text/en/%search%'+__api_key__
__topic_url__ = 'https://www.googleapis.com/freebase/v1/topic%mid%?'+__api_key__
__research_url__ = 'https://www.googleapis.com/freebase/v1/search?query=%search%'+__api_key__
__info_url__ = 'https://www.googleapis.com/freebase/v1/text%mid%?maxlength=300'+__api_key__
__ignore__ = ['after','although','though','because','before','once','since','than',
	'that','though','till','unless','until','when','whenever','where','wherever',
	'while','the','this']

def add_node(data,parent=None,callback=None):
	for _node in callback.node_db:
		if _node['text'] == data['text']:
			if data.has_key('id') and data['id'] == _node['id']:
				return callback.node_db.index(_node)
			else:
				return callback.node_db.index(_node)
	
	data['related'] = []
	
	if parent:
		if not parent in data['related']:
			data['related'].append(callback.node_db.index(parent))
	
	callback.node_db.append(data)
	return len(callback.node_db)-1

def add_word(word,score=1):
	word = word.lower()
	for char in ['.',',',';',':','\'','|',')','(','>','<']:
		word = word.replace(char,'')
	
	word = word.replace(' ','')
	
	_len = len(word)
	if not _len or _len<=3:
		return None
	
	if word in __ignore__:
		return None
	
	_words = [{entry['word']:entry} for entry in words_db]
	
	for _word in _words:
		if word in _word.keys():
			_word[word]['score']+=score
			return _word[word]

	try:
		words_db.append({'word':word.encode('utf-8'),'score':score})
		return words_db[len(words_db)-1]
	except:
		return None

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

def examine_topic(topic):
	try:
		_result = json.loads(urllib.urlopen(__research_url__.replace('%search%',topic.lower())
			.replace(' ','_')).read())
	except:
		return None
	
	if _result and _result['result']:
		_result = _result['result'][0]
	else:
		return None
	
	if _result['score']<50:
		return None
	
	return _result

def get_related_topics(topic):
	if not topic in research_db['topics'].keys():
		return None
	
	logging.error('get_related_topics() is currently broken!')
	
	_ret = []
	
	#for node in research_db['topics'][topic]:
	#	_object = node_db[node]
	#	if _object['valuetype']=='object':
	#		_ret.append(_object)
	
	return _ret

def get_related_links(topic):
	if not topic in research_db['topics'].keys():
		return None
	
	_ret = []
	
	#for node in research_db['topics'][topic]:
	#	_object = node_db[node]
	#	if _object['valuetype']=='uri':
	#		_ret.append(_object)
	
	return _ret

def research_topic(mid,callback,parent=None):
	"""Scrapes data from topic 'mid', creating nodes."""
	try:
		_result = json.loads(urllib.urlopen(__topic_url__.replace('%mid%',mid)
			.replace(' ','_')).read())['property']
	except:
		print 'Failed',mid
		return None
	
	_relevant_objects = []
	
	for type in _result:
		if _result[type]['valuetype'] == 'object':
			for object in _result[type]['values']:
				_tmp = object.copy()
				
				_tmp = {'text':object['text'].encode('utf-8'),
					'id':object['id'].encode('utf-8'),
					'valuetype':_result[type]['valuetype'],
					'researched':False}
				
				_node_ref = add_node(_tmp,parent=parent,callback=callback)
				
				#if type.count(topic):
				_relevant_objects.append(_node_ref)
		
		elif _result[type]['valuetype'] == 'uri':
			for object in _result[type]['values']:
				_tmp = {'text':object['text'].encode('utf-8'),
				'valuetype':_result[type]['valuetype'],
				'researched':False}
				
				#Sometimes we can't use certain URLs
				#Call it lazy on my behalf, but I would just
				#like to avoid having a ton of japanese
				#characters in the node mesh...
				if _tmp['text'].count('jp.wikipedia'):
					continue
				
				_node_ref = add_node(_tmp,parent=parent,callback=callback)
				_relevant_objects.append(_node_ref)
	
	return _relevant_objects

def find_node(search,callback):
	_ret = []
	
	for node in callback.node_db:
		if node['text'].count(search):
			_ret.append(node)
	
	if _ret:
		if len(_ret)==1:
			_word = 'entry'
		else:
			_word = 'entries'
		
		_s = 'I\'ve located %s %s for \'%s\' in the mesh.\n' % (len(_ret),_word,search)
		
		if len(_ret)>15:
			return '%sThere are too many results to list! Tighten your search.' % _s
		
		_nodes = []
		for entry in _ret:
			if not entry['valuetype'] == 'object':
				continue
				
			_nodes.append('%s (#%s)' % (entry['text'],callback.node_db.index(entry)))
		
		#callback.msg(channel,'Nodes matching \'%s\': %s' % (_search,', '.join(_nodes)))
		return '%sNodes matching \'%s\': %s' % (_s,search,', '.join(_nodes))
			
	else:
		#callback.msg(channel,'\'%s\' does not exist in the mesh.' % _search,to=user['name'])
		return '\'%s\' does not exist in the mesh.' % search

def show_node(index,callback):
	try:
		_node = callback.node_db[index]
	except ValueError:
		return '\'%s\' is not an integer.' % index
	except IndexError:
		return 'Node #%s does not exist.' % index
	
	return 'Node #%s: %s' % (index,', '.join([str(_node[key]) for key in
		_node.iterkeys()]))

def research_node(node,callback,parent=None,topic=None):
	if node['researched']:
		logging.error('Node already marked as researched!')
		return None
	
	_start_index = len(callback.node_db)-1
	_research = research_topic(node['id'],callback,parent=node)
	node['researched'] = True	
	
	print 'Researching',node['text'],node['id']
	
	if _research:
		for _object in _research:
			if not _object in node['related']:
				node['related'].append(_object)
	
	return [i for i in range(_start_index+1,len(callback.node_db)-1)]

def expand_nodes(nodes,callback,limit=25):
	_topic_count = 0
	_relevant_objects = []
	
	#TODO: Finish this!
	for _node in nodes:
		node = callback.node_db[_node]
		if node['researched'] or not node['valuetype']=='object':
			continue
		
		_relevant_objects.extend(research_node(node,callback))
		
		if _topic_count>=limit:
			return _relevant_objects
		else:
			_topic_count+=1
		
	return _relevant_objects

def expand_all_nodes(limit=25):
	_topic_count = 0
	_relevant_objects = []
	
	for node in node_db:
		if node['researched'] or not node['valuetype']=='object':
			continue
		
		_relevant_objects.extend(research_node(node))
		
		if _topic_count>=limit:
			return _relevant_objects
		else:
			_topic_count+=1
		
	return _relevant_objects

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

def build_view(node):
	_ret = node['related'][:]
	_tmp = []
	
	while not _ret == _tmp:
		_tmp = _ret[:]
		
		for _node in _tmp:
			for __node in node_db[_node]['related']:
				if not __node in _tmp:
					_tmp.append(__node)
		
		_ret = _tmp[:]
	
	return _ret