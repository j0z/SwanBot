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
that says it all: a DLA operates passively or interactively,
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

Adaptive Learning
-----------------
Once SwanBot is configured to read your various inputs for
data, no user interaction is required- it uses the already
existing data to provide useful information to you in whatever
way possible.

In the above example, a text message was sent to the user's
phone. However, this isn't always the best way to communicate
with the user. Again, this is where inputs come into play: by
providing an input that fires when you enter your house/room,
SwanBot can then adjust where it outputs its data. In my case,
SwanBot users the text-to-speech function on my tablet to
fill me in on things that are relevant to what's going on.

You're probably wondering what kind of information SwanBot
outputs. For that, read the `modules` section below.

Sometimes data just isn't relevant. You want a break, you're
in a class, etc; although SwanBot tries its best to avoid
bothering you with alerts, it can be really hard to figure out
what time is best. Let's use the example of my morning
routine:

On Tuesdays I wake up at 9 AM, start breakfast, and check
Reddit's technology subreddit for breaking/interesting
news. I then check my email and eat while browsing the various
channels I follow on YouTube for new uploads. It's consistent-
I do this exact routine every Tuesday and Thursday, and have
similar patterns for the other weekdays.

With SwanBot, I wake up and start breakfast, and am soon
greeted by my tablet's robotic voice:

    Good morning. News for <date>:
      Apple accused of plagiarizing iconic Swiss clock design
      ...


Modules
-------
Modules provide a way for SwanBot to fetch information from
sources specified by the user(s) via the node mesh.

Let's say the `mod_twitter` module was installed on the
server. When it runs, it scans each user's node mesh for
`twitter-details`, grabs the login credentials in the node's
`data` key, and watches for mentions, tweets, or direct
messages. If this information is relevant to you at all hours
of the day, SwanBot can be configured to alert you by whatever
means possible.

API
---
See `data/api.md`

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