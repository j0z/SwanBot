from client import Client
import android

droid = android.Android()
HOST = '10.238.82.100'

_results = Client(HOST).get({'param':'find_nodes',
                        'query':{'type':'tweet','public':True},
                        'apikey':'testkey'})['results']

for node in Client(HOST).get({'param':'get_nodes','nodes':_results,'apikey':'testkey'}):
	droid.say('Tweet from %s. %s' % (node['from'],node['text']))