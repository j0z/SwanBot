import subprocess
import time
import sys

_args = ['python','swanbot.py']
_args.extend(sys.argv[1:])

while 1:
	try:
		subprocess.call(_args)
		time.sleep(1)
	except KeyboardInterrupt:
		break
