Nodes
=====
SwanBot's main attraction is the 'node mesh', a spiderweb of
interconnected chunks of data that is sectioned off by user,
then sub-divided into categories of data also specified by
the user. Users start off with a blank section of the node
mesh and are free to add/remove as many nodes as they like.

For example, a user might create a node called "Tweets",
then set all incoming events of type "Twitter-*" to be
attached to this node. This creates sub-nodes attached to the
parent "Twitter" node, allowing you to manage all of your
Twitter-related nodes simultaneously while also giving you
fine-grained control over each one.

If you decided that your tweets need to be private, you could
set the main "Twitter" node to be private, which would
then make all attached nodes (your tweets) hidden from the
public.