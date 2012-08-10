import subprocess
import sys

_args = ['python','swanbot.py']
_args.extend(sys.argv[1:])

while 1:
	try:
		subprocess.call(_args)
	except KeyboardInterrupt:
		break
