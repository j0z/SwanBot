SwanBot API
===========
About
-----
This is revision 2 of the SwanBot API reference. It is
intended for those who are either porting the client to
another language, or those trying to understand the inner-
workings of SwanBot on the client's end.

For Coders
----------
If you are familiar with Python, it is highly recommended
that you take a look at client.py before implementing the
API in your language of choice. While everything is covered
in this document, there are certain aspects that are better
explained in code. These will be pointed out when the
situation arises.

Prerequisites include a working knowledge of sockets, JSON,
and SHA224.

Connecting and Authenticating
-----------------------------
By default, SwanBot listens for connections on port 9002
and expects JSON strings prefixed with one of the two
operations mentioned below and terminated with `\r\n`. It
is possible to stay constantly connected to SwanBot, but it
is recommended that you throw out the connection once a
response has been receieved unless you plan on making
another immediately afterwards.

That said, connecting and authenticating are one and the
same; regardless of what information is sent to SwanBot,
the dictionary must contain the key `apikey` with a valid
API key converted to SHA224. As long as this key is
included in the packet, you are considered "authenticated."

For the visual learners:
    {'apikey':,'22c7d75bd36e271adc1ef873aee4f95db6bc54a9c2f9f4bcf0cd18a8'}

Gets and Sends
--------------
Authenticating is fairly simple, and actually using SwanBot
is just as easy, as there are really only two commands used
to interact with the node mesh.

The two most basic operations are `api-get` and `api-send`,
which are named simply based on their interaction with the
node mesh: `api-get` can only search and retrieve entries
from the mesh, while `api-send` can modify the mesh in any
way, including adding, deleting, and changing nodes.

Gets
----
As previously mentioned, `api-get` can only read from the
node mesh. It can only really be used for finding and
retrieving nodes, which can be accomplished using the two
commands `find_nodes` and `get_nodes`. These two may look
the same, but they both perform very different tasks.

`find_nodes` searches the node mesh for nodes matching the
provided criteria and returns a list of node IDs that
match.

`get_nodes` accepts a list of node IDs and returns the
nodes themselves.

Using either one is fairly simple:

    'api-get:{'param': 'find_nodes','apikey': 'apikey','query': {'type': 'tweet'}}\r\n'
	    Returns a list of nodes of type 'tweet'.
	
	'api-get:{'param': 'get_nodes','apikey': 'apikey','nodes': [3,5,9]}\r\n'
	    Returns nodes 3, 5, and 9 in a list.