#Defines functions used to create and modify nodes on the
#node mesh.

NODE_ID = 0

NODE = {'id':None,
	'owner':None,
	'date':None,
	'type':'',
	'filter':'',
	'public':'',
	'data':''}

def create_node():
	global NODE_ID
	NODE_ID+=1
	
	_n = NODE.copy()
	_n['id'] = NODE_ID
	
	return _n