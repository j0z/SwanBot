#Just a silly little module :)
import logging
import random
import json
import os

__word_bank__ = [{'type':'greeting','words':['hi','hello']},
	{'type':'addressing','words':['you']},
	{'type':'report','words':['status']}]

def init():
	global db,phrase_bank,look_for
	
	db = {'phrase_bank':[],'look_for':[]}
	
	try:
		_file = open(os.path.join('data','phrases.json'),'r')
		db = json.loads(_file.readline())
		_file.close()
		
		phrase_bank = db['phrase_bank']
		look_for = db['look_for']
		
		logging.info('Success!')
	except:
		logging.error('Could not load phrase database from disk!')
		_file = open(os.path.join('data','phrases.json'),'w')
		_file.write(json.dumps(db))
		_file.close()
		logging.error('Created phrase database.')
		init()

def shutdown():
	logging.info('Offloading phrase database to disk...')
	_file = open(os.path.join('data','phrases.json'),'w')
	_file.write(json.dumps({'phrase_bank':phrase_bank,'look_for':look_for},ensure_ascii=True))
	_file.close()
	logging.info('Success!')

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def get_word(type):
	for entry in __word_bank__:
		if entry['type'] == type:
			return random.choice(entry['words'])

def parse(commands,callback,channel,user):	
	if channel in callback.factory.channels:
		return 1
	
	#Returning...
	return 0
	
	_phrases = ' '.join(commands).lower().split('.')
	_found_types = []
	_found_phrases = []
	_response = ''
	_ask_back = []
	
	if look_for:
		for entry in look_for:
			if not entry['user'] == user:
				continue
			
			for _entry in phrase_bank:
				if _entry['phrase'] == entry['question']:
					return 1
			
			phrase_bank.append({'phrase':entry['question'],'answer':' '.join(commands)})
			look_for.remove(entry)
			return 1
	
	for entry in __word_bank__:
		for phrase in _phrases:
			for word in entry['words']:
				if word in phrase.replace('?','').split(' '):
					_found_types.append({'type':entry['type'],'phrase':phrase})
	
	for phrase1 in _phrases:
		for entry in phrase_bank:
			if phrase1.count(entry['phrase']):
				_found_phrases.append(entry['answer'])
	
	if not _found_types and not _found_phrases:
		return 1
	
	for entry in _found_types:
		if entry['type'] == 'greeting':
			_response += get_word('greeting')
		
		elif entry['type'] == 'report':
			_events = callback.get_events(limit=1)
			
			if _events:
				_response += _events[0]['text']
		
	for entry in _found_phrases:
		if len(_response):
			_response += '. '
		
		_response += entry
	
	if not len(_response):
		_ask_back.append(_phrases[0])
	
	if len(_ask_back):
		callback.msg(channel,_ask_back[0])
		look_for.append({'user':user,'question':_ask_back[0]})
	
	callback.msg(channel,_response)

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass