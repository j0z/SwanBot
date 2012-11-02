 _______ __   __  ______ __   _ _     _ _______
 |         \_/   |  ____ | \  | |     | |______
 |_____     |    |_____| |  \_| |_____| ______|

A Win8/RT Swanbot Libary for C#
==================================================

Requirements:

Windows 8/RT

Visual Studio 2012 Pro
-or-
Visual Studio 2012 Express for Windows 8- Metro app development only
-or-
Visual Studio 2012 Express for Desktop- for desktop/library development

All dependencies should be included in this repository. Although you may wish to use your own copy of JSON.NET, if one is available. I've included the current version in DLL form for convience. 

Usage:

CygnusClient client = new CygnusClient();
client.AddServer(ServerIP, ServerPort, APIKey);

Cygnus supports multiple servers with one client. The first argument for every command should be the index of the server in clients.Servers

