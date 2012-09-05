import time

def tick(callback):
	pass

def user_tick(user,callback):
	pass

def add_task(user,task):
	if not user.has_key('tasks'):
		user['tasks'] = []
	
	user['tasks'].append({'task':task,
		'when':time.strftime('%A, %B %d at %H:%M')})

def get_tasks(user,callback):
	_had_task = False
	
	if not user.has_key('tasks'):
		return 1
	
	for task in user['tasks']:
		callback.msg(user['name'],'%s: %s' %
			(str(task['when']),str(task['task'])))
		_had_task = True

	if not _had_task:
		callback.msg(user['name'],'You have no tasks.')

def delete_task(user,number,callback):	
	number = int(number)
	
	if not user.has_key('tasks') or 0 >= number or number > len(user['tasks']):
		return 1
	
	user['tasks'].pop(number-1)
	
	callback.msg(user['name'],'Task deleted!')

def parse(commands,callback,channel,user):
	if commands[0] == 'task' and len(commands)>=2:
		if (len(commands)>=3 and commands[1] in ['add']):
			add_task(user,' '.join(commands[2:]))
			callback.msg(user['name'],'%s, task added!' % user['name'])
		elif commands[1] == 'list':
			get_tasks(user,callback)
		elif commands[1] == 'delete' and len(commands)==3:
			delete_task(user,commands[2],callback)

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass
	