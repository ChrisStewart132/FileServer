# FileServer
Command line file server and client python scripts

Server binds to localhost (127.0.0.1) and when requested responds with the queried file if it is in the servers directory.
	py server.py PORT_NUMBER

Client sends requests to the server for a specified file and downloads it into the client directory if possible.
	py client.py SERVER_ADDRESS SERVER_PORT_NO FILENAME