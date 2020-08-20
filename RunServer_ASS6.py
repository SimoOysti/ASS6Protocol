# -*- coding: cp1252 -*-

# A server-sided to-do list utilizing my custom ASS6 protocol
# Simo Öysti

import Script.Server_ASS6
from Script.Server_ASS6 import Server


########################
# SERVER CONFIGURATION #
########################

#Time to wait in seconds when no actions occur with the client until closing the connection.
CLIENT_TIMEOUT = 5

#The location of the to-do list on the server
LIST_FILE = "todo.txt"

#If True, server will print most of the actions it's doing to help with debugging
ECHO = True

#Port for the server to use if none is specified at object creation
DEFAULT_PORT = 1338

#Default IP address to bind the server's listener to, if none is specified at object creation
DEFAULT_IP = "127.0.0.1"

#The first one in this list will be used as default in a response (in the case the client has specified an unsupported protocol)
SUPPORTED_PROTOCOL_VERSIONS = [
    "ASS6_V1",
    ]

VALID_REQUEST_METHODS = [
    "LIST",
    "ADD",
    "DONE",
    ]

ERROR_DESCRIPTIONS = {
    "InvalidID":( "ASS6InvalidID", "Server was unable to find a task with the ID specified in the DONE request." ),
    "InvalidRequest":( "ASS6InvalidRequest", "The client sent a request using invalid syntax that the server failed to parse." ),
    "FileNotAccessible":( "ASS6FileNotAccessible", "Server had a problem when trying to access the to-do list file." ),
    "UnsupportedProtocol":( "ASS6UnsupportedProtocol", "Server does not support the protocol which was specified by the client in the request." ),
    }

#Create the server and bind to localhost with the default port
Server()

#Custom IP address and port can be specified as optional arguments
#Example: Server("123.123.123.123", 60123)

###################
# Things to note: #
###################

# all possible response codes from this server are:
#    ERROR, LIST, ADDED, REMOVED
# More information in the protocol documentation .txt file

########################
# END OF CONFIGURATION #
########################
