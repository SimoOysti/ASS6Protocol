# -*- coding: cp1252 -*-



# A server-sided to-do list utilizing my custom ASS6 protocol
# Simo Öysti


######################################################################
# DEFAULT CONFIGURATION                                              #
# THIS FILE SHOULD NOT BE TOUCHED UNLESS YOU KNOW WHAT YOU ARE DOING #
# FOR CONFIGURATION, EDIT ../RunServer_ASS6.py                       #
######################################################################



import socket
import base64
from Helpers import createFileIfNotExists
from Helpers import echo
import os

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

# valid response codes from this server are:
# ERROR, LIST, ADDED, REMOVED

class Server:
    
    #########################################################################
    # Simply initialize the server's properties and then call startServer() #
    #########################################################################
    def __init__(self, listen_addr=DEFAULT_IP, listen_port=DEFAULT_PORT):
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.startServer()



    ############################################
    # Set up the socket and then call listen() #
    ############################################
    def startServer(self):
        print("\nSTARTING SERVER")

        createFileIfNotExists(LIST_FILE)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind( (self.listen_addr, self.listen_port) )
        self.sock.listen(5)
        print("\nServer is now running.")
        self.listen()

    ########################################################
    # Loop forever, dealing with new requests from clients #
    # Will call buildResponse() upon receiving a request   #
    # Uses the main thread for now                         #
    ########################################################
    def listen(self):
        while True:

            #Close client socket if it exists
            try:
                clientSock.shutdown(SHUT_RDWR)
                clientSock.close()
            except NameError:
                pass
            
            echo(ECHO, "Listening to new requests..")
            print("*")
            print("*")
            print("*")
            print("*")

            (clientSock,addr) = self.sock.accept()
            clientSock.settimeout(CLIENT_TIMEOUT)
            echo( ECHO, "New connection from address: " + str(addr) )
            
            wholeRequest = ""
            while True:
                try:
                    receivedString = clientSock.recv(1024).decode('utf-8')
                    wholeRequest += receivedString

                    if (wholeRequest[-2:] == "\r\n"):
                        self.buildResponse(clientSock, wholeRequest)
                        break
                    else:
                        if (receivedString):
                            continue
                        else:
                            #We will use the socket.timeout exception also when we receive a request without proper \r\n ending
                            raise socket.timeout
                        
                except socket.timeout:
                    echo(ECHO, "No message ending with '\\r\\n' was received from the client. Closed connection (timeout)")
                    break
                
    #end of listen()


    
    ###############################################################################################
    # If buildResponse() is called, it means that we received a request string ending with "\r\n" #
    # This function will simply generate the proper response string, based on the request.        #
    # After a response is generated, will call sendResponse() to the supplied socket.             #
    ###############################################################################################
    def buildResponse(self,clientSock,request):
        echo(ECHO, "Received a request string from the client. Processing it now.")

        cur_protocol = SUPPORTED_PROTOCOL_VERSIONS[0] #Default protocol
        responseString = ""
        
        try:
            #Split the request into 3 parts
            protocol,method,argument = request.split(" ",2)
            argument = argument[:-2] #remove \r\n from the end
            argument = argument.replace("\n", " ")
        except ValueError:
            echo(ECHO, "Unable to parse the request message. Client used invalid request syntax.")
            
            responseString = ( cur_protocol +
                              " ERROR " +
                              ERROR_DESCRIPTIONS["InvalidRequest"][0] + " " +
                              ERROR_DESCRIPTIONS["InvalidRequest"][1] + "\r\n" )
            
            self.sendResponse(clientSock, responseString)
            return


        ###################################################
        # If invalid protocol was specified by the client #
        
        if ( protocol not in SUPPORTED_PROTOCOL_VERSIONS ):

            echo(ECHO, "Unsupported protocol '" + protocol + "' was requested by the client.")
            
            responseString = ( cur_protocol +
                              " ERROR " +
                              ERROR_DESCRIPTIONS["UnsupportedProtocol"][0] + " " +
                              ERROR_DESCRIPTIONS["UnsupportedProtocol"][1] + "\r\n" )
            
            self.sendResponse(clientSock, responseString)
            return
        else:
            cur_protocol = protocol
        #                                                 #
        ###################################################






        
        #########################################################
        # If invalid request method was specified by the client #
        
        if ( method not in VALID_REQUEST_METHODS ):

            echo(ECHO, "Invalid request method '" + method + "' was specified by the client.")
            
            responseString = ( cur_protocol +
                              " ERROR " +
                              ERROR_DESCRIPTIONS["InvalidRequest"][0] + " " +
                              ERROR_DESCRIPTIONS["InvalidRequest"][1] + "\r\n" )
            
            self.sendResponse(clientSock, responseString)
            return
        #                                                       #
        #########################################################







        ###########################################################
        # If client requests to list contents of the list         #
        
        if (method == "LIST"):

            echo(ECHO, "Client successfully requested a list of to-do list contents.")
            
            responsecode = "LIST"
            body = ""
            try:
                #OTA LUKKO TODO
                with open(LIST_FILE, "r") as f:
                    title = len(f.readlines()) #Amount of lines in the file = amount of to-do entries
                    f.seek(0)
                    body = f.read() #Whole content of the to-do file

            except Exception as e:
                print (e)
                responsecode = "ERROR"
                title = ERROR_DESCRIPTIONS["FileNotAccessible"][0]
                body = ERROR_DESCRIPTIONS["FileNotAccessible"][1]

            title = str(title)
            responseString = ( cur_protocol + " " +
                               responsecode + " " +
                               title + " " +
                               body + "\r\n" )

            self.sendResponse(clientSock, responseString)
            return
        #                                                    #
        ######################################################







        ##################################################
        # If client requests to add an entry to the list #
        
        if (method == "ADD"):

            echo(ECHO, "Client successfully requested to add '" + argument + "' to the to-do list")

            responsecode = "ADDED"
            title = "0"
            body = argument

            try:
                #OTA LUKKO TODO
                #Make sure that the file exists already as we wanna throw an error if it doesn't exist at this point.
                with open(LIST_FILE, "r") as f:
                    currentList = f.readlines() #Whole content of the to-do file, split to a list of lines
                    currentList = [x.strip() for x in currentList] #Remove whitespaces
                    newList = list(currentList)
                    body = argument

                    #Loop every task in the list
                    for i in xrange(0, len(currentList)): 
                        
                        #Check if the current task ID is not equal to linenumber+1 (e.g. 0. line should be task ID 1, 1. line should be task ID 2 etc.)
                        lineID = ""
                        lineID += (character for character in currentList[i] if character in "1234567890") #TODO VITTU
                        if (lineID != str(i+1)):
                            
                            newList.append("NEW_ELEMENT")
                            newList[:i] = currentList[:i]
                            ID = str(i+1)
                            newList[i] = (ID + ") " + argument)
                            newList[i+1:] = currentList[i:]
                            title = ID
                            echo(ECHO, "The to-do list had a gap in running ID numbers, so the new task will be placed in the first gap found.")
                            break

                    #If the to-do list was already in perfect order, the previous code didn't trigger so we need to handle it.
                    if (title == "0"): 
                        ID = str(len(newList)+1)
                        newList.append(ID + ") " + argument)
                        title = ID
                        echo(ECHO, "The to-do list task ID numbering is already complete with no gaps, so the new task will simply be appended with a new ID.")

                
                #Replace the file with an updated version
                with open(LIST_FILE, "w") as f:
                    listToWrite = ""
                    for line in newList:
                        listToWrite += (line + "\n")
                    f.write(listToWrite)
                    echo(ECHO, "New to-do list successfully written! New task added with the ID '" + title + "'")
            except:
                responsecode = "ERROR"
                title = ERROR_DESCRIPTIONS["FileNotAccessible"][0]
                body = ERROR_DESCRIPTIONS["FileNotAccessible"][1]                    

            responseString = ( cur_protocol + " " +
                               responsecode + " " +
                               title + " " +
                               body + "\r\n" )

            self.sendResponse(clientSock, responseString)
            return
        #                                                #
        ##################################################


        #######################################################
        # If client requests to remove an entry from the list #
        
        if (method == "DONE"):

            echo(ECHO, "Client successfully requested to remove a task with an ID of '" + argument + "' from the to-do list")

            responsecode = "REMOVED"
            title = "0"
            body = ""

            try:
                #OTA LUKKO TODO
                #Make sure that the file exists already as we wanna throw an error if it doesn't exist at this point.
                with open(LIST_FILE, "r") as f:
                    
                    currentList = f.readlines() #Whole content of the to-do file, split to a list of lines
                    currentList = [x.strip() for x in currentList] #Remove whitespaces
                    newList = list(currentList)

                    #Loop every task in the list
                    for i in xrange(0, len(currentList)): 
                        
                        #Check if the current task ID is equal to the ID specified by the request
                        if (currentList[i][0] == argument):
                            body = currentList[i][3:]
                            del newList[i]
                            title = argument
                            echo(ECHO, "Specified task ID was found from to-do list, removing it.")
                            break

                    #If the list didn't include the specified ID
                    if (title == "0"): 
                        echo(ECHO, "The to-do list did not contain an ID that was specified. Nothing was changed.")
                        responsecode = "ERROR"
                        title = ERROR_DESCRIPTIONS["InvalidID"][0]
                        body = ERROR_DESCRIPTIONS["InvalidID"][1]

                    else:
                        #Replace the file with an updated version
                        with open(LIST_FILE, "w") as f:
                            
                            listToWrite = ""
                            for line in newList:
                                listToWrite += (line + "\n")
                            f.write(listToWrite)
                            echo(ECHO, "New to-do list successfully written! Task with the ID '" + title + "' was removed.")
            except:
                responsecode = "ERROR"
                title = ERROR_DESCRIPTIONS["FileNotAccessible"][0]
                body = ERROR_DESCRIPTIONS["FileNotAccessible"][1]                    


            title = str(title)
            responseString = ( cur_protocol + " " +
                               responsecode + " " +
                               title + " " +
                               body + "\r\n" )

            self.sendResponse(clientSock, responseString)
            return
        #                                                #
        ##################################################







        # If none of the above conditions were triggered
        # Just in case we still didn't manage to build a valid response
        # Mainly for testing, this condition should never actually trigger
        if (responseString == ""):

            echo(ECHO, "Response was not generated, this should never happen!")
            
            responsecode = "ERROR"
            title = "UNKNOWN_ERROR"
            body = "This should not be possible! Contact the developer ASAP."
            
            responseString = ( cur_protocol + " " +
                               responsecode + " " +
                               title + " " +
                               body + "\r\n" )
            
            self.sendResponse(clientSock, responseString)
            return

    #end of buildResponse()
        
    ###################################################################
    # Will send the supplied response string to the socket specified. #
    # Client should treat it as utf-8                                 #
    ###################################################################
    def sendResponse(self, clientSock, response):
        clientSock.send( response.encode('utf-8') )
        echo(ECHO, "The following response was sent to the client:")
        echo(ECHO, repr(response) )


#End of Server class
