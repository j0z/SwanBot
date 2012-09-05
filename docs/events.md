Events
======
`events` provide a way for one client to talk to another
without establishing direct contact. They are only sent
to clients authenticated as the user who created the
event.

Structure
=========
While events are entirely optional, the methods used to
both send and receive them are similar to sending data
packets, except there is no concept of "send" or "get"-
all incoming event packets sent to the client are
assumed to be from the server and require no response,
just handling by the client.

    event:type:value - Sends an event of 'type' to all
		connected clients authenticated as the user who
		created the event.'value' can be anything.

If the `client.py` module is being used, a helper
function is available.

    client.fire_event(type,value)
