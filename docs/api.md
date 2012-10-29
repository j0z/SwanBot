API
===
SwanBot's API focuses mostly on two different commands: `send`
and `get`. While these are vague terms (what are we sending/
getting?) it all fits into the motto "send anything, get
anything" that I've been following since I started this
project.

Connecting
----------
For this example, I'll be using Python to demonstrate the
basic `send` and `get` functions. However, feel free to write
your own implementation in whatever language you feel the most
comfortable in; all you need is access to sockets/JSON!

Note: There's a library included with SwanBot called
"client.py". Use it instead of writing your own!

    import socket
    import json

    #Connect to SwanBot
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect(('localhost',9002))

    #Create a node that looks for nodes of type `tweet`.
    payload = {'param':'create_node','query':{'type':'twitter','public':True,
               'filter':{'type':'tweet'}},
               'apikey':'<APIKEY>'}

    #Send it all down the pipe!
    self.conn.sendall('api-send:%s\r\n' % json.dumps(payload))

    #Wait for a response...
    print json.loads(connection.recv(1024).strip())

    connection.close()

Payloads
--------
Payloads are extremely simple, and outside of the `param` key,
accept basically any form of data. Let's take the above example
and break it apart.

    {'param':'create_node','query':{'type':'twitter','public':True,
        'filter':{'type':'tweet'}},
        'apikey':'<APIKEY>'}

When the server sees that the `param` is set to `create_node`,
the contents of `query` is sent to a function that creates and
returns a node with the same information. The only required
key is `type`, leaving everything else up to you.

However, there are a few keys SwanBot looks for. These can be
found in `nodes.md`.