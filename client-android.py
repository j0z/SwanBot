from client import Client
import android

droid = android.Android()
HOST = '192.168.1.2'

_results = Client(HOST,'testkey').get({'param':'find_nodes',
                        'query':{'type':'speech'}})['results']

for node in Client(HOST,'testkey').get({'param':'get_nodes','nodes':_results})['results']:
	Client(HOST,'testkey').delete_nodes(node['id'])
	droid.ttsSpeak('%s' % (node['text']))