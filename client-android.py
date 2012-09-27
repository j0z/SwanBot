from client import Client
import android

droid = android.Android()

_results = Client('localhost').get({'param':'find_nodes',
                        'query':{'type':'tweet','public':True},
                        'apikey':'testkey'})['results']

for node in Client('localhost').get({'param':'get_nodes','nodes':_results,'apikey':'testkey'}):
	droid.say('Tweet from %s. %s' % (node['from'],droid['text']))