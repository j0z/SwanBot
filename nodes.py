#Defines functions used to create and modify nodes on the
#node mesh.

NODE = {'id':None,
	'owner':None,
	'date':None,
	'type':'',
	'filter':'',
	'public':'',
	'data':''}

def create_node():
	return NODE.copy()