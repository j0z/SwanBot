Fetches
=======
`fetch` nodes are intended to be the result of a `watch`
node. In its most basic form, these nodes provide a way to
return formatted data from a series of different nodes
quickly and easily, in addition to extracting data from the
returned nodes and sending them to a string.

    {'type':'fetch','name':'morning-routine',
		'fetch':[{'type':'calendar_event'},{'type':'user_profile'}],
		'format':'Good morning, node[2].first_name node[1].title'}
		