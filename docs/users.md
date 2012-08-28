Users
=====
Similar to GNU/Linux, SwanBot supports multiple users, all of
which are all trumped by the "root" user, which has access to
the core functions, like adding and removing users from the
system, performing maintenance, and adding/removing modules.

Nodes
-----
Each user occupies a space known as a 'node,' which they can
use however they want. Data can be added or removed at will,
made public or private, or "routed" (see 'routing.md').

This ability to add/remove data on command enables SwanBot
to be used in any application that follows the API, providing
an open platform for storing/retrieving information which can
then be used across multiple applications.

Permissions
-----------
All users are given a certain amount of privacy within their
home "node." By default all added information is considered
personal and is hidden from the public eye. This can be
changed to allow certain info to be openly read by other nodes
on the system (writing from other nodes is also allowed.)

What is 'root'?
---------------
'root' is a user that has complete control of the system,
but does not have the same functions and abilities of a normal
user, like being able to add/remove information to/from the
account, which severely limits its use outside of maintenance
and general upkeep.

root-only Commands
==================

    adduser - Creates a new user.
	deluser <name> - Deletes user.
	shutdown - Terminates all connections, stores open
		databases to disk, and stops.
	loadmod <module> - Loads a module.
	delmod <module> - Unloads module.
	lmods - Lists all available modules and shows their status (Loaded or Unloaded.)
	modinfo <module> - Shows the status of the specified module.