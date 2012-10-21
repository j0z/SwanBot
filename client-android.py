from client import Client
import android

droid = android.Android()
HOST = '192.168.1.2'

_results = Client(HOST).get({'param':'find_nodes',
                        'query':{'type':'speech','public':True},
                        'apikey':'testkey'})['results']

for node in Client(HOST).get({'param':'get_nodes','nodes':_results,'apikey':'testkey'})['results']:
	droid.ttsSpeak('%s' % (node['text']))