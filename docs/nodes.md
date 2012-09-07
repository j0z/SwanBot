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

Structure
---------
Nodes consist of the following information:

    ID: Int. Unique identifier automatically assigned by the
        node mesh.
    OWNER: String. Username of the creator.
    DATE: String. Datetime string of when the node was added
        to the mesh.
    TYPE: String. Describes in vague terms what data the node
        carries.
    FILTER: String. If used, the node forfeits 'data' and
        begins to connect existing and incoming nodes to
        itself if 'type' is matched by 'filter'
    PUBLIC: Boolean. Decides whether the node is visible to
        the public.
    DATA: Anything. Can be any data type that dumps to a
        valid JSON string.