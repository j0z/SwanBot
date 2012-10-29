#Defines functions used to create and modify nodes on the
#node mesh.
from datetime import datetime

NODE_ID = 0

NODE = {'id':None,
	'owner':None,
	'date':None,
	'filter':{},
	'type':'',
	'public':'',
	'data':''}

def create_node():
	global NODE_ID
	NODE_ID+=1
	
	_node = NODE.copy()
	_node['id'] = NODE_ID
	_node['parents'] = []
	_node['children'] = []
	_node['created'] = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

	return _node