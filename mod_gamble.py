import random

__bets__ = []

class bet:
	def __init__(self,owner,callback):
		self.callback = callback
		self.betters = []
		self.money = 0
		self.owner = owner
		self.winning_number = random.randrange(1,6)
	
	def place(self,user,bet,money):
		_users = [n['user'] for n in self.betters]
		
		if user['money']-money<0:
			self.callback.msg(user['alert_channel'],'%s: You do not have enough money!'
				% user['name'])
			return 1
			
		user['money'] -= money
		self.money += money
		
		if not user in _users:
			self.betters.append({'user':user,'bet':bet})
		
		self.callback.msg(user['alert_channel'],'%s: Bet of %s placed. Current total is %s.'
			% (user['name'],money,self.money))
	
	def finalize(self):
		global __bets__
		__bets__.remove(self)
		_winners = 0
		
		for user in self.betters:
			if user['bet'] == self.winning_number:
				_winners+=1
		
		self.callback.msg(self.owner['alert_channel'],'Bet over! The winning number was %s.' %
			(self.winning_number))
		
		if not _winners:
			self.callback.msg(self.owner['alert_channel'],'Nobody won!' %
				(self.owner['name']))
		else:		
			for user in self.betters:
				if user['bet'] == self.winning_number:
					user['user']['money']+=self.money/_winners
			
			self.callback.msg(self.owner['alert_channel'],'Congrats, winners!')
		

def tick(user,callback):
	if not user.has_key('money'):
		user['money'] = 50

def get_bet(name):
	global __bets__
	
	for bet in __bets__:
		if bet.owner['name'] == name:
			return bet
	
	return None

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
	elif ' '.join(commands[0:2]) == 'check money':
		callback.msg(channel,'%s: You have $%s' %
			(user['name'],user['money']))
	elif ' '.join(commands[0:2]) == 'start bet':
		global __bets__
		
		_bet = get_bet(user['name'])
		
		if _bet:
			callback.msg(channel,'%s: You already have a running bet!' % user['name'])
			return 1
		
		__bets__.append(bet(user,callback))
		
		callback.msg(channel,'%s has started a bet! Type: place bet %s <bet> <money>' %
			(user['name'],user['name']))
	elif ' '.join(commands[0:2]) == 'place bet' and len(commands)==5:
		_bet = get_bet(commands[2])
		
		if not _bet:
			callback.msg(channel,'%s: Bet with owner \'%s\' does not exist.' %
				(user['name'],commands[2]))
			return 1
		
		_bet.place(user,int(commands[3]),int(commands[4]))
	
	elif ' '.join(commands[0:2]) == 'close bet':
		_bet = get_bet(user['name'])
		
		if not _bet:
			callback.msg(channel,'%s: Bet with owner \'%s\' does not exist.' %
				(user['name'],commands[2]))
			return 1
		
		_bet.finalize()			

def on_user_join(user,channel,callback):
	pass

def on_user_part(user,channel,callback):
	pass