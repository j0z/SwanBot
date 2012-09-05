#Just a silly little module :)
import logging
import random
import json
import os

__keyphrases__ = [{'command':'status',
	'needs':
		[{'match':'status','required':True}],
	'keywords':['check','your']}]

def init():
	pass

def shutdown():
	pass

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def parse(commands,callback,channel,user):
	if commands[0] == 'status':
		_events = callback.get_events(limit=1)
		
		if _events:
			callback.msg(channel,_events[0]['text'],to=user['name'])
		else:
			callback.msg(channel,'I\'m not currently doing anything.',to=user['name'])

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass