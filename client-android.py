from datetime import datetime
from client import Client
import android
import time

droid = android.Android()
HOST = '10.238.82.100'
ACCEL_LAST_X = None
ACCEL_LAST_Y = None
ACCEL_LAST_Z = None
SCREEN_ON = False

def check_for_speech(droid):
	_results = Client(HOST,'testkey').get({'param':'find_nodes',
                        'query':{'type':'speech'}})

	if not _results.has_key('results'):
		return False
	
	_results = _results['results']
	
	for node in Client(HOST,'testkey').get({'param':'get_nodes','nodes':_results})['results']:
		Client(HOST,'testkey').delete_nodes([node['id']])
		droid.ttsSpeak('%s' % (node['text']))

def check_for_screen(droid):
	return droid.checkScreenOn().result

def check_for_movement(droid):
	global ACCEL_LAST_X,ACCEL_LAST_Y,ACCEL_LAST_Z
	_return = False
	
	_accel = droid.sensorsReadAccelerometer()
	
	if not ACCEL_LAST_X:
		ACCEL_LAST_X = _accel.result[0]
	
	if not ACCEL_LAST_Y:
		ACCEL_LAST_Y = _accel.result[1]
	
	if not ACCEL_LAST_Z:
		ACCEL_LAST_Z = _accel.result[2]
	
	if _accel.result[2]:
		if abs(_accel.result[2]-ACCEL_LAST_Z)>=2:
			_return = True
	
	ACCEL_LAST_X,ACCEL_LAST_Y,ACCEL_LAST_Z = _accel.result
	
	return _return

def get_time_asleep(droid):
	_results = Client(HOST,'testkey').get({'param':'find_nodes',
		'query':{'type':'action','action':'tablet-asleep'}})
	
	if not _results.has_key('results'):
		return -1
	
	_results = _results['results']
	
	node = Client(HOST,'testkey').get({'param':'get_nodes','nodes':_results})['results'][0]
	_fell_asleep_time = datetime.strptime(str(node['created']),'%m/%d/%Y %H:%M:%S')
	
	return (datetime.now()-_fell_asleep_time).seconds

def main():
	global droid,host,SCREEN_ON
	
	droid.startSensingTimed(1,500)
	
	while 1:
		check_for_speech(droid)
		
		if check_for_movement(droid) and not SCREEN_ON:
			if get_time_asleep(droid)>5:
				Client(HOST,'testkey').create_node({'type':'action','action':'tablet-awake','public':True})
				droid.wakeLockAcquireDim()
				print 'MOVED!!!!!!!!!!!!!!!!'
		
		if check_for_screen(droid):
			if not SCREEN_ON:
				Client(HOST,'testkey').create_node({'type':'action','action':'tablet-awake','public':True})
				SCREEN_ON = True
				
		else:
			if SCREEN_ON:
				Client(HOST,'testkey').create_node({'type':'action','action':'tablet-asleep','public':True})
				SCREEN_ON = False
		
		time.sleep(3)

main()