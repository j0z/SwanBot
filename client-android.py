from client import Client
import android
import time

droid = android.Android()
HOST = '192.168.1.2'
ACCEL_LAST_X = None
ACCEL_LAST_Y = None
ACCEL_LAST_Z = None

def check_for_speech(droid):
	_results = Client(HOST,'testkey').get({'param':'find_nodes',
                        'query':{'type':'speech'}})

	if _results.has_key('results'):
		_results = _results['results']
	else:
		return False
	
	for node in Client(HOST,'testkey').get({'param':'get_nodes','nodes':_results})['results']:
		Client(HOST,'testkey').delete_nodes([node['id']])
		droid.ttsSpeak('%s' % (node['text']))

def check_for_movement(droid):
	global ACCEL_LAST_X,ACCEL_LAST_Y,ACCEL_LAST_Z
	
	_accel = droid.sensorsReadAccelerometer()
	
	if not ACCEL_LAST_X:
		ACCEL_LAST_X,ACCEL_LAST_Y,ACCEL_LAST_Z = _accel
	
	print abs(_accel[2]-ACCEL_LAST_Z)
	
	ACCEL_LAST_Z = _accel[2]
	
	print _accel[3]

def main():
	global droid
	
	droid.startSensingTimed(1,500)
	
	while 1:
		check_for_speech(droid)
		check_for_movement(droid)
		time.sleep(5)

main()
#_results = Client(HOST,'testkey').get({'param':'find_nodes',
#                        'query':{'type':'speech'}})['results']
#
#for node in Client(HOST,'testkey').get({'param':'get_nodes','nodes':_results})['results']:
#	Client(HOST,'testkey').delete_nodes([node['id']])
#	droid.ttsSpeak('%s' % (node['text']))