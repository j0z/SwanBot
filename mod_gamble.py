import random

def tick(user,callback):
	pass

def roll_dice(number):
	_numbers = []
	
	if number>25:
		return [69]
	
	for n in range(number):
		_numbers.append(random.randrange(1,6))
	
	return _numbers

def parse(commands,callback,channel,user):
	if commands[0] == 'roll':
		if commands[1] == 'dice':
			if len(commands)==3:
				callback.msg(channel,'%s: %s' %
					(user['name'],', '.join(str(n) for n in roll_dice(int(commands[2])))))
			else:
				callback.msg(channel,'%s: %s' % 
					((user['name'],', '.join(str(n) for n in roll_dice(2)))))

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass