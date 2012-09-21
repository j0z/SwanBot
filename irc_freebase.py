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

import threading
import logging
import urllib
import json
import time
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
	global words_db,research_db
	
	words_db = {'words':[],'nodes':[]}
	
	try:
		_file = open(os.path.join('data','words.json'),'r')
		words_db = json.loads(_file.readline())
		
		for entry in words_db['words']:
			for key in entry:
				if isinstance(entry[key],unicode):
					entry[key] = entry[key].encode('utf-8')
		
		_file.close()
		words_db = words_db['words']
		logging.info('Success!')
	except:
		logging.error('Could not load words database from disk!')
		_file = open(os.path.join('data','words.json'),'w')
		_file.write(json.dumps(words_db))
		_file.close()
		logging.error('Created words database.')
		init()	

def shutdown():
	global node_db
	
	logging.info('Offloading local words database to disk...')
	_file = open(os.path.join('data','local_words.json'),'w')
	_file.write(json.dumps({'words':words_db,'nodes':node_db},ensure_ascii=True))
	_file.close()
	logging.info('Success!')

class research_thread(threading.Thread):
	def __init__(self,channel,user,callback,topic):
		self.channel = channel
		self.user = user
		self.callback = callback
		self.topic = topic
		
		threading.Thread.__init__(self)
		
		self.start()
	
	def run(self):
		self.callback.msg(self.channel,'Researching \'%s\'...' % self.topic,to=self.user['name'])
		
		_res = examine_topic(self.topic)
		
		if not _res:
			self.callback.msg(self.channel,'Nothing could be found.',to=self.user['name'])
			return 1
		
		_research = research_topic(_res['mid'])
		_research.extend(expand_nodes(_research))
		_related = nodes_to_string(_research)
		
		if _research:
			self.callback.msg(self.channel,
				'I have built a node mesh of size %s. Some related topics are: %s' %
					(len(_research),_related),to=self.user['name'])

class find_node_thread(threading.Thread):
	def __init__(self,channel,user,callback,search):
		self.channel = channel
		self.user = user
		self.callback = callback
		self.search = search
		
		threading.Thread.__init__(self)
		
		self.start()
	
	def run(self):
		_ret = find_node(self.search)
		
		self.callback.msg(self.channel,_ret,to=self.user['name'])

class show_node_thread(threading.Thread):
	def __init__(self,channel,user,callback,index):
		self.channel = channel
		self.user = user
		self.callback = callback
		self.index = index
		
		threading.Thread.__init__(self)
		
		self.start()
	
	def run(self):
		_ret = show_node(self.index)
		
		self.callback.msg(self.channel,_ret,to=self.user['name'])

def connected_to_core(callback):
	global core
	
	core = callback

def examine_topic(topic):
	global core
	
	_query = core.examine_topic(topic)
	_stime = time.time()
	
	while 1:
		if _query['done']:
			return json.loads(_query['data'])
		
		if time.time()-_stime>=15:
			print 'Timed out.'
			return None

def research_topic(mid):
	global core
	
	_query = core.research_topic(mid)
	_stime = time.time()
	
	while 1:
		if _query['done']:
			return json.loads(_query['data'])
		
		if time.time()-_stime>=15:
			print 'Timed out.'
			return None

def expand_nodes(nodes):
	global core
	
	_query = core.expand_nodes(nodes)
	_stime = time.time()
	
	while 1:
		if _query['done']:
			return json.loads(_query['data'])
		
		if time.time()-_stime>=15:
			print 'Timed out.'
			return None

def nodes_to_string(nodes):
	global core
	
	_query = core.nodes_to_string(nodes)
	_stime = time.time()
	
	while 1:
		if _query['done']:
			return json.loads(_query['data'])['text']
		
		if time.time()-_stime>=15:
			print 'Timed out.'
			return None

def find_node(search):
	global core
	
	_query = core.find_nodes(search)
	_stime = time.time()
	
	while 1:
		if _query['done']:
			return json.loads(_query['data'])['text']
		
		if time.time()-_stime>=15:
			print 'Timed out.'
			return None

def show_node(index):
	global core
	
	_query = core.show_node(index)
	_stime = time.time()
	
	while 1:
		if _query['done']:
			return json.loads(_query['data'])['text']
		
		if time.time()-_stime>=15:
			print 'Timed out.'
			return None

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
		
		research_thread(channel,user,callback,_topic)
		
		return 1
	
	elif commands[0] == '.find_node' and len(commands)>=2:
		_search = ' '.join(commands[1:])
		
		find_node_thread(channel,user,callback,_search)
		
		return 1
	
	elif commands[0] == '.show_node' and len(commands)==2:
		try:
			show_node_thread(channel,user,callback,int(commands[1]))
		except ValueError:
			pass
		
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
		
		#_ret = add_word(word,score=_score)

def on_user_join(user,channel,callback):	
	pass

def on_user_part(user,channel,callback):
	pass