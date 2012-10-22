from client import Client
import android
import time

droid = android.Android()
HOST = '192.168.1.2'

def check_for_speech(droid):
	_results = Client(HOST,'testkey').get({'param':'find_nodes',
                        'query':{'type':'speech'}})['results']

	if not _results:
		return False
	
	for node in Client(HOST,'testkey').get({'param':'get_nodes','nodes':_results})['results']:
		Client(HOST,'testkey').delete_nodes([node['id']])
		droid.ttsSpeak('%s' % (node['text']))

def check_for_movement(droid):
	_accel = droid.sensorsReadAccelerometer()
	
	print _accel

def main():
	global droid
	
	droid.startSensingTimed(1,500)
	
	while 1:
		check_for_speech(droid)
		check_for_movement(droid)
		time.sleep(5)

#_results = Client(HOST,'testkey').get({'param':'find_nodes',
#                        'query':{'type':'speech'}})['results']
#
#for node in Client(HOST,'testkey').get({'param':'get_nodes','nodes':_results})['results']:
#	Client(HOST,'testkey').delete_nodes([node['id']])
#	droid.ttsSpeak('%s' % (node['text']))