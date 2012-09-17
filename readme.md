# SwanBot
***
SwanBot was a vague project that has no real goal or intention.
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
up combining those two features, and then report their success
/failure to SwanBot.

But what happens next?

# My Journey to Create the Ultimate Personal Assistant
***
For a while I've been interested in the idea of a "DLA" (a
term that I believe was coined by the creator of Project
Jarvis.) DLA simply stands for "Digital Life Assistant", and
that says it all; a DLA operates passively or interactively,
but at the end of the day, is designed entirely to adapt to
the way you operate in your day-to-day life.

So what does SwanBot do?

Two key terms get tossed around a lot when I speak about
SwanBot: Inputs and Outputs. Inputs are just that- ways for
SwanBot to accept incoming data which is then stored in the
Node Mesh. What kind of data, though? Well, that's up to the
user. I've placed no limitations on what can be stored in the
Node Mesh. Even things like images can be stored inside the
mesh, then processed by OpenCV or any other user-specified
library.

Outputs provide a way for SwanBot to communicate with the
user in some way. I've also placed no limit on how outputs
should be properly structured or implemented, and have also
placed that into the hands of the user.

Here's a working example:
You're out and about, let's say 100+ miles from your home with
friends or on vacation. Suddenly you receive a text message:

    Severe weather warning for ***** is in effect until 6PM.

This is a message sent by SwanBot, which has magically found
out your current location and has warned you of possible
severe weather. Whoa!

Except, of course, it isn't magic: SwanBot barely has any work
to do, because chances are you're updating Twitter, Facebook,
or Google+ on the go. Taking pictures? Connecting via Wifi?
That works too. It's redundant to explicitly tell SwanBot
where you're at; It already has enough data to deduce that on
its own.

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
---
While I have my own idea for this project, I'm interested in
seeing what other people do it. And yeah, I understand it's
nothing special or groundbreaking, but I feel like I'd be
saving someone some time by publishing this.

If you write anything interesting/helpful, file a pull request
and I'll send it through (within reason) to the main repo for
other people to use.

Happy coding!

-flags