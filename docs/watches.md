Watches
=======
At the end of the day, SwanBot is entirely useless without
something to parse and understand what is happening in the
Mesh.

`watches` are the answer to this issue. They can be thought
of like filter nodes, except instead of sorting nodes, they
"consume" them and produce an output. As always, here's a
working example:

User `mike` creates a watch node with the following params:

    {'type':'watch','input':{'type':'tablet-move',
    	'source':'mikes-tablet'},'output':''}
