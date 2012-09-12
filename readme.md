SwanBot
*******
SwanBot is a vague project that has no real goal or intention.
In its earlier forms, SwanBot was used to monitor a single IRC
channel and provide services like weather, Last.fm status, etc.
At one point I decided to write a module that allowed SwanBot
to fetch pages from Freebase, all while doing its own research
on related topics which was stored in something called the
"node mesh."

I decided I wanted to practice with Client/Server applications
again, so I set out to do just that by moving all the "node
mesh"-related code into a server program, which accepted
commands from clients to search the mesh and return data. This
proved to be an interesting idea, and I started to invest more
time in the server application.

At one point I started wanting to automate stuff in my dorm
room, so I set out to add stuff like OpenCV support to look
for me as I was coming into my room, and scanning for my phone
in the proximity of my computer's Bluetooth adapter. I ended
up combining those two features, and them report their success
/failure to SwanBot.

So what happens after SwanBot gets the data?

That's my current issue. Simply logging the data isn't very
useful, but keeping it around for reference could potentially
fire off a few ideas.

I'm publishing this Git repo in hopes that someone can make
use of it in its current state, which is very open-ended. I
have a few plans on features I'd like to implement, but
that's all up in the air right now.

API
---
The API is very simple, but some of the core functionality
is broken or non-existent. Like I've said before, this project
is very much a trial grounds for ideas I've had but never got
around to trying out, hence the aimlessness and sometimes
erratic/vague code strewn about.

For the client (contained in client.py, of all places) to
connect, SwanBot.py reads the file contained in:
	
	data/core_users.json

and compares the username/password and compares that with
the details in that file. At some point I'll expand on this,
but that's it... functions like:

	client.set_user_value()
	client.get_user_value()

are used to store and retrieve information. For an example on
how to use it properly, check the included "bluetoothbot.pyw"
program. It's a good example of how to make a program work in
conjunction with the client without getting in your way.

I highly recommend diving into SwanBot.py and editing things
that you feel need to be changed.

Thanks
------
While I have my own idea for this project, I'm interested in
seeing what other people do it. And yeah, I understand it's
nothing special or groundbreaking, but I feel like I'd be
saving someone some time by publishing this.

If you write anything interesting/helpful, file a pull request
and I'll send it through (within reason) to the main repo for
other people to use.

Happy coding!

-flags