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

def init():
	global words_db,research_db,node_db
	words_db = {'words':[],'nodes':[]}
	
	try:
		_file = open(os.path.join('data','words.json'),'r')
		words_db = json.loads(_file.readline())
		
		for entry in words_db['words']:
			for key in entry:
				if isinstance(entry[key],unicode):
					entry[key] = entry[key].encode("utf-8")
		
		_file.close()
		#node_db = words_db['nodes']
		words_db = words_db['words']
		logging.info('Success!')
	except:
		logging.error('Could not load words database from disk!')
		_file = open(os.path.join('data','words.json'),'w')
		_file.write(json.dumps(words_db))
		_file.close()
		logging.error('Created words database.')
		init()

def shutdown(core):
	global node_db
	
	logging.info('Offloading local words database to disk...')
	_file = open(os.path.join('data','local_words.json'),'w')
	_file.write(json.dumps({'words':words_db,'nodes':node_db},ensure_ascii=True))
	_file.close()
	logging.info('Success!')
	
	logging.info('Uploading words database to core...')
	
	chunk_size = 15000
	node_db_start_index = 0
	node_db_end_index = chunk_size
	node_db_string = json.dumps(node_db)
	
	core.start_send_node_db()
	
	while 1:
		_send = node_db_string[node_db_start_index:node_db_end_index]
		if not len(_send):
			break
		
		core.send_node_db(_send)
		
		node_db_start_index = node_db_end_index
		node_db_end_index += chunk_size
	
	logging.info('Uploaded words database to core!')

def load_node_db(data):
	global node_db
	
	logging.info('Received node_db from core.')
	node_db = data

def connected_to_core(core):
	core.get_node_db(load_node_db)

def add_node(data,parent=None):
	for _node in node_db:
		if _node['text'] == data['text']:
			if data.has_key('id') and data['id'] == _node['id']:
				return node_db.index(_node)
			else:
				return node_db.index(_node)
	
	data['related'] = []
	
	if parent:
		if not parent in data['related']:
			data['related'].append(node_db.index(parent))
	
	node_db.append(data)
	return len(node_db)-1

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

def research_topic(mid,parent=None):
	"""Scrapes data from topic 'mid', creating nodes."""
	try:
		_result = json.loads(urllib.urlopen(__topic_url__.replace('%mid%',mid)
			.replace(' ','_')).read())['property']
	except:
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
				
				_node_ref = add_node(_tmp,parent=parent)
				
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
				
				_node_ref = add_node(_tmp,parent=parent)
				_relevant_objects.append(_node_ref)
	
	return _relevant_objects

def research_node(node,parent=None,topic=None):
	if node['researched']:
		logging.error('Node already marked as researched!')
		return None
	
	_start_index = len(node_db)-1
	_research = research_topic(node['id'],parent=node)
	node['researched'] = True	
	
	print 'Researching',node['text'],node['id']
	
	if _research:
		for _object in _research:
			if not _object in node['related']:
				node['related'].append(_object)
	
	return [i for i in range(_start_index+1,len(node_db)-1)]

def expand_nodes(nodes,limit=25):
	_topic_count = 0
	_relevant_objects = []
	
	#TODO: Finish this!
	for _node in nodes:
		node = node_db[_node]
		if node['researched'] or not node['valuetype']=='object':
			continue
		
		_relevant_objects.extend(research_node(node))
		
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

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	#Age existing entries
	for word in words_db:
		if word['score']:
			word['score']-=1
		else:
			words_db.remove(word)
	
	if commands[0] == '.search' and len(commands)>=2:
		callback.msg(channel,'Result: %s' % (perform_search(' '.join(commands[1:]))),to=user['name'])
		
		for word in commands[1:]:
			add_word(word,score=10)
		
		return 1
	elif commands[0] == '.topic':
		_topics = get_topics()
		
		if _topics == 'No topic could be found.':
			callback.msg(channel,'No topic can be found!',to=user['name'])
			return 1
		
		for _topic in _topics[:2]:
			callback.msg(channel,'Topic: %s (%s)' % (_topic['word'],_topic['score']),to=user['name'])
		
		return 1
	elif commands[0] == '.topic_ext':
		_combined_topics = None
		_research = None
		_res_combined = None
		_topics = get_topics()
		
		if _topics == 'No topic could be found.':
			callback.msg(channel,'No topic can be found!',to=user['name'])
			return 1
		
		#Sometimes combining the first two topics can give us a better result
		if len(_topics)>=2 and _topics[1]['word']:
			_combined_topic = ' '.join([topic['word'] for topic in _topics[:2]])
			_res_combined = examine_topic(_combined_topic)
			
			if _res_combined:
				callback.msg(channel,'Combined topic: %s (%s) %s' % (_combined_topic,
					_res_combined['score'],_res_combined['notable']['id']),to=user['name'])
		
		_res = examine_topic(_topics[0]['word'])
		if _res:
			callback.msg(channel,'Single topic: %s (%s) %s' % (_topics[0]['word'],_res['score'],
				_res['notable']['id']),to=user['name'])
		
		if _res and _res_combined and _res['score']>_res_combined['score']:
			callback.msg(channel,'Single: %s' % get_info(_res['mid']),to=user['name'])
			_research = research_topic(_res['mid'],_res['notable']['id'])
			_research.extend(expand_nodes_in_range(_res))
		elif _res and _res_combined and _res['score']<_res_combined['score']:
			callback.msg(channel,'Combined: %s' % get_info(_res_combined['mid']),to=user['name'])
			_research = research_topic(_res_combined['mid'],_res_combined['notable']['id'])
			_research.extend(expand_nodes_in_range(_res_combined))
		elif _res: 
			callback.msg(channel,'Single: %s' % get_info(_res['mid']),to=user['name'])
			_research = research_topic(_res['mid'],_res['notable']['id'])
			_research.extend(expand_nodes_in_range(_res))
		elif _res_combined:
			callback.msg(channel,'Combined: %s' % get_info(_res_combined['mid']),to=user['name'])
			_research = research_topic(_res_combined['mid'],_res_combined['notable']['id'])
			_research.extend(expand_nodes_in_range(_res_combined))
		
		else:
			if _res:
				callback.msg(channel,'Not a valid topic: %s' % _topics[0]['word'],to=user['name'])
				add_word(_topics[0]['word'],score=-50)
			elif _res_combined:
				callback.msg(channel,'Not a valid topic: %s' % _combined_topic,to=user['name'])
				
				for word in _combined_topic:
					add_word(word,score=-50)
		
		if _research:
			callback.msg(channel,'I have built a node mesh of size %s.' %
				(len(_research),', '.join([node_db[entry]['text'] for entry in _research
				if node_db[entry]['valuetype'] == 'object'])[:300]),
				to=user['name'])
		
		return 1
	elif commands[0] == '.topic_related':
		_topics = get_topics()
		
		if _topics == 'No topic could be found.':
			callback.msg(channel,'No topic can be found!',to=user['name'])
			return 1
		
		#TODO: Cache this somehow
		_res = examine_topic(_topics[0]['word'])
		_related = get_related_topics(_res['notable']['id'])
		
		if _related:
			callback.msg(channel,'Related topics: %s' % len(_related),
				to=user['name'])
		else:
			callback.msg(channel,'No topic can be found!',to=user['name'])
		
		return 1
	
	elif commands[0] == '.research' and len(commands)>=2:
		_topic = ' '.join(commands[1:])
		callback.msg(channel,'Researching \'%s\'...' % _topic,to=user['name'])
		
		_res = examine_topic(_topic)
		
		if not _res:
			callback.msg(channel,'Nothing could be found.',to=user['name'])
			return 1
		
		_research = research_topic(_res['mid'])
		_research.extend(expand_nodes(_research))
		
		if _research:
			callback.msg(channel,'I have built a node mesh of size %s. Some related topics are: %s' %
				(len(_research),', '.join([node_db[entry]['text'] for entry in _research
				if node_db[entry]['valuetype'] == 'object'])[:300].encode('utf-8','ignore')),
				to=user['name'])
		
		return 1
	
	elif commands[0] == '.find_node' and len(commands)>=2:
		_search = ' '.join(commands[1:])
		_ret = []
		
		for node in node_db:
			if node['text'].count(_search):
				_ret.append(node)
		
		if _ret:
			if len(_ret)==1:
				_word = 'entry'
			else:
				_word = 'entries'
			
			callback.msg(channel,'I\'ve located %s %s for \'%s\' in the mesh.' % (len(_ret),_word,_search),
				to=user['name'])
			
			if len(_ret)>15:
				callback.msg(channel,'There are too many results to list! Tighten your search.')
				return 1
			
			_nodes = []
			for entry in _ret:
				if not entry['valuetype'] == 'object':
					continue
					
				_nodes.append('%s (#%s)' % (entry['text'],node_db.index(entry)))
			
			callback.msg(channel,'Nodes matching \'%s\': %s' % (_search,', '.join(_nodes)))
				
		else:
			callback.msg(channel,'\'%s\' does not exist in the mesh.' % _search,to=user['name'])
		
		return 1
	
	elif commands[0] == '.show_node' and len(commands)==2:
		try:
			_node = node_db[int(commands[1])]
		except ValueError:
			callback.msg(channel,'\'%s\' is not an integer.' % commands[1],to=user['name'])
			return 1
		except IndexError:
			callback.msg(channel,'Node #%s does not exist.' % commands[1],to=user['name'])
			return 1
		
		callback.msg(channel,'Node #%s: %s' % (commands[1],', '.join([str(_node[key]) for key in
			_node.iterkeys()])),to=user['name'])
		
		callback.msg(channel,get_info(_node['id']),to=user['name'])
		
		return 1
	
	elif commands[0] == '.research_node' and len(commands)==2:
		try:
			_node = node_db[int(commands[1])]
		except ValueError:
			callback.msg(channel,'\'%s\' is not an integer.' % commands[1],to=user['name'])
			return 1
		except IndexError:
			callback.msg(channel,'Node #%s does not exist.' % commands[1],to=user['name'])
			return 1
		
		callback.msg(channel,'Researching node #%s...' % commands[1],to=user['name'])
		callback.create_event(True,'Starting research for node #%s.' % commands[1],'mod_freebase')
		
		_research = research_node(_node,parent=_node)
		
		if _research:
			callback.msg(channel,'I have built a node mesh of size %s. Some related topics are: %s' %
				(len(_research),', '.join([node_db[entry]['text'] for entry in _research
				if node_db[entry]['valuetype'] == 'object'])[:300]),to=user['name'])
			
			callback.create_event(True,'Finished research for node #%s.' % commands[1],'mod_freebase')
		else:
			callback.msg(channel,'No new nodes were created.',to=user['name'])
			callback.create_event(False,'Finished research for node #%s.' % commands[1],'mod_freebase')
		
		return 1
	
	elif commands[0] == '.show_related_nodes' and len(commands)==2:
		try:
			_node = node_db[int(commands[1])]
		except ValueError:
			callback.msg(channel,'\'%s\' is not an integer.' % commands[1],to=user['name'])
			return 1
		except IndexError:
			callback.msg(channel,'Node #%s does not exist.' % commands[1],to=user['name'])
			return 1
		
		_related = []
		
		for node in _node['related']:
			_related.append('%s (%s)' % (node_db[node]['text'],commands[1]))
		
		if _related:
			callback.msg(channel,'Found %s nodes related to #%s: %s' % (len(_related),commands[1],
				', '.join(_related)),to=user['name'])
			
			callback.create_event(False,'Found %s nodes related to #%s.' % (len(_related),commands[1])
				,'mod_freebase')
		else:
			callback.msg(channel,'No related nodes were found.',to=user['name'])
			
			callback.create_event(False,'No related nodes were found for #%s.'
				% commands[1],'mod_freebase')
	
	elif commands[0] == '.build_view' and len(commands)==2:
		try:
			_node = node_db[int(commands[1])]
		except ValueError:
			callback.msg(channel,'\'%s\' is not an integer.' % commands[1],to=user['name'])
			return 1
		except IndexError:
			callback.msg(channel,'Node #%s does not exist.' % commands[1],to=user['name'])
			return 1
		
		if not _node['related']:
			callback.msg(channel,'No view could be built because node #%s has no related nodes.'
				% commands[1],to=user['name'])
			
			callback.create_event(False,'Failed to build view for node #%s' % commands[1],
				'mod_freebase')
			return 1
		
		_view = []
		
		for node in build_view(_node):
			_view.append('%s (%s)' % (node_db[node]['text'],node))
		
		callback.msg(channel,'Found %s nodes in view of node #%s: %s' % (len(_view),commands[1],
			', '.join(_view)),to=user['name'])
		
		callback.create_event(True,'Found %s nodes in view of node #%s: %s'
			% (len(_view),commands[1]),'mod_freebase')
	
	elif commands[0] == '.topic_links':
		if len(commands)==2:
			try:
				_limit = int(commands[1])
			except:
				_limit = 3
		else:
			_limit = 3
		_topics = get_topics()
		
		if _topics == 'No topic could be found.':
			callback.msg(channel,'No topic can be found!',to=user['name'])
			return 1
		
		#TODO: Cache this somehow
		_res = examine_topic(_topics[0]['word'])
		_related = get_related_links(_res['notable']['id'])
		
		if _related:
			callback.msg(channel,'Related links: %s' % ' '.join([entry['text'] for entry
				in _related][:_limit]),to=user['name'])
		else:
			callback.msg(channel,'No links can be found!',to=user['name'])
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

def on_user_join(user,channel,callback):	
	pass

def on_user_part(user,channel,callback):
	pass