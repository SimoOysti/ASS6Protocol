# -*- coding: cp1252 -*-

# A client program for utilizing my custom ASS6 protocol
# Simo �ysti

import socket
import time
import sys
import os
from Script.Helpers import echo
os.system("mode con: cols=100 lines=30")


# The protocol version we should request to use with the server.
DEFAULT_PROTOCOL = "ASS6_V1"

# How many times we should try (when facing an error with the server) before giving up?
MAX_FAILED_TRIES = 3

#How many seconds to wait between aforementioned tries?
SECONDS_BETWEEN_TRIES = 1.5

# How many seconds to wait before closing the connection, if nothing happens with the socket?
TIMEOUT_SECONDS = 4

# Default IP address of the ASS4 fileserver
DEFAULT_ADDR = "127.0.0.1"

# Default port to connect to
DEFAULT_PORT = 1338

#If True, client will print some more of it's actions to help with debugging
ECHO = False



##################
class Client:

    #Welcome message and call self.startClient()
    def __init__(self):


        print ("\n"*100)
        print ("\n\n###########################")
        print ("# Welcome to ASS6 client! #")
        print ("###########################\n")

        self.main()


    #Main program which initializes object properties and then calls upon other class methods to proceed with execution
    def main(self):

        #Set to True so the loop will always start at the beginning
        self.start_over = True

        while (self.start_over):
            #Instantly change to False, so program will always exit unless specifically told to continue
            self.start_over = False

            #Initialization
            self.server_addr = False
            self.server_port = False
            self.protocol_version = DEFAULT_PROTOCOL
            self.sock = False
            self.failed_tries = 0


            ######################
            # Main program start #
            ######################

            #Get user input for server IP
            while (not self.server_addr):
                self.askServerAddress()

            #Get user input for server port
            while (not self.server_port):
                self.askServerPort()


            #Get user input for which action to perform, and deal with them.
            #Will loop forever until stopped from within the function by user action.
            conSuccess = self.askUserAction()
            if ( not conSuccess() ):
                self.start_over = True


    #End of main()




    # Will ask the user to enter an IP address and then set self.server_addr to that value.
    # Currently there is no checking whether the entered value is a valid IP address or not!
    # If nothing is entered, will use DEFAULT_ADDR value.
    def askServerAddress(self):
        server_addr = raw_input("\n\nPlease enter the IP address of the ASS6 server you'd like to connect to (default " + DEFAULT_ADDR + ")\n>")

        if (server_addr == ""):
            print (">" + str(DEFAULT_ADDR) + "\n")
            self.server_addr = DEFAULT_ADDR
            return

        self.server_addr = server_addr
        return
        #TODO regex pattern check the IP



    # Will ask the user to enter a port between 1024 and 65535 and then set self.server_port to that value.
    # If invalid port is entered, self.server_port will be set to False.
    # If nothing is entered, will use DEFAULT_PORT value.
    def askServerPort(self):
        server_port = raw_input("\n\nPlease enter the port of the server (default " + str(DEFAULT_PORT) + ")\n>")

        if server_port == "":
            print (">" + str(DEFAULT_PORT) + "\n")
            self.server_port = DEFAULT_PORT
            return
        try:
            server_port = int( server_port )

            if ( (server_port < 1024) or (server_port > 65535) ):
                raise TypeError

            self.server_port = server_port
            return


        except TypeError:
            print ("\nInvalid port entered. Must be a number between 1024 and 65535")
            self.server_port = False
            return


    #Ask for user input to perform an action
    #Will loop forever until closed
    #Return False means that a connection failed and user wishes to start over
    def askUserAction(self):
        while (True):
            action = False
            valid_actions = ["1","2","3","4","5","6","7",]

            while (not action):
                print("\n\n\n(1) Print the to-do list")
                print("(2) Add a task to the to-do list")
                print("(3) Remove a task from the to-do list")
                print("(4) Send a custom request string to server manually.")
                print("(5) Change server IP/port (currently using '" + self.server_addr + ":" + str(self.server_port) + "')")
                print("(6) Change protocol version to use (currently using '" + self.protocol_version + "')")
                print("(7) Exit program.")
                action = raw_input("\nSelect the action you would like to perform (no default)\n>")

                if (action not in valid_actions):
                    action = False

            #List files
            if (action == "1"):
                if ( not self.connect() ):
                    return False
                self.method = "LIST"
                self.arg = ""

                request = self.sendRequest()
                if (request):
                    echo (ECHO, "Successfully sent the following request:")
                    echo (ECHO, repr(request) )
                    response = self.getResponse()
                    if (response):
                        responseParts = response.split(" ", 3)
                        sys.stdout.write("Total task count: ")
                        sys.stdout.flush()
                        print( responseParts[2] )
                        print( responseParts[3] )


            #Add a task to the list
            elif (action == "2"):
                self.method = "ADD"
                self.arg = raw_input("Please type the task you wish to add to the list\n>")

                #Connect
                if ( not self.connect() ):
                    return False

                #Send the request
                request = self.sendRequest()
                if (request):
                    echo (ECHO, "Successfully sent the following request:")
                    echo (ECHO, repr(request))

                    #Get the response
                    response = self.getResponse()
                    if (response):
                        #Split the response to 4 parts
                        responseSplit = response.split(" ",3)

                        #Remove 2 characters '\r\n' from the end of the string as well as extra spaces
                        responseSplit[3] = responseSplit[3][:-2]
                        responseSplit[3] = responseSplit[3].strip()

                        #Print the response of the server
                        if (responseSplit[1] == "ERROR"):
                            print("The following error was sent by the server:")
                            print(response)

                        else:
                            print("Task '" + responseSplit[3] + "' was successfully added to the list with an ID of '" + responseSplit[2] + "'")


            #Remove a task from the list
            elif (action == "3"):
                self.method = "DONE"
                self.arg = raw_input("Please type the ID of the task you wish to remove from the list\n>")

                #Connect
                if ( not self.connect() ):
                    return False

                #Send the request
                request = self.sendRequest()
                if (request):
                    echo (ECHO, "Successfully sent the following request:")
                    echo (ECHO, repr(request))

                    #Get the response
                    response = self.getResponse()
                    if (response):
                        #Split the response to 4 parts
                        responseSplit = response.split(" ",3)

                        #Remove 2 characters '\r\n' from the end of the string as well as extra spaces
                        responseSplit[3] = responseSplit[3][:-2]
                        responseSplit[3] = responseSplit[3].strip()

                        #Print the response of the server
                        if (responseSplit[1] == "ERROR"):
                            print("The following error was sent by the server:")
                            print(response)

                        else:
                            print("Task '" + responseSplit[3] + "' was successfully removed from the list. (had an ID of '" + responseSplit[2] + "')")

            #Send custom request string
            elif (action == "4"):
                requestString = raw_input("Enter the whole request string matching documentation WITHOUT the ending '(SP)\\r\\n'\n>")

                if (requestString == ""):
                    print "Cannot send an empty string."
                    raw_input("Press enter to continue..")
                else:
                    if ( not self.connect() ):
                        return False

                    request = self.sendRequest(requestString + " \r\n")
                    if (request):
                        print ("Successfully sent the following request:")
                        print ( repr(request.decode("utf-8")) )

                        response = self.getResponse()
                        if (response):
                            print(response)



            #Change server IP/port
            elif (action == "5"):
                self.server_addr = False
                self.server_port = False

                #Get user input for server IP
                while (not self.server_addr):
                    self.askServerAddress()

                #Get user input for server port
                while (not self.server_port):
                    self.askServerPort()

            #Change protocol version
            elif (action == "6"):
                self.protocol_version = raw_input("Enter the new protocol to use\n>")

            #Exit program
            elif (action == "7"):
                print("Quitting.")
                sys.exit()


            #Close connection, set action to False to start the loop over again
            if (self.sock):
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.sock = False
                raw_input("Connection closed. Press enter to continue..")
            action = False


    # Creates a new socket and connects it to the specified IP:port
    # Returns the created socket
    # If connection is unsuccessful, returns False instead.
    def openSock(self,addr,port):
        sock = socket.socket()
        sock.settimeout(TIMEOUT_SECONDS)

        try:
            sock.connect((addr,port))
            return sock
        except socket.error:
            return False


    # Will call to openSock() with self.server_addr and self.server_port and retry if unsuccessful, according to MAX_FAILED_TRIES and SECONDS_BETWEEN_TRIES.
    # Will also offer the option to start over or quit, if connection was unsuccessful.
    # Returns False if connection was unsuccessful, which indicates user wants to re-enter IP/port.
    # Returns True if connection was successful.
    def connect(self):
        self.sock = False
        #Attempt to connect
        sys.stdout.write("Connecting..")
        while (not self.sock):
            self.sock = self.openSock(self.server_addr, self.server_port)
            sys.stdout.write(".")
            sys.stdout.flush()

            if (not self.sock):
                self.failed_tries += 1
                if (self.failed_tries < MAX_FAILED_TRIES):
                    continue

                #Failed connection too many times
                else:
                    print ("\nFailed to connect to server after " + str(MAX_FAILED_TRIES) + " tries.")
                    choice = raw_input("Do you wish to start over? (y/n) (default n)\n>")
                    if ( (choice == "y") or (choice == "Y") ):
                        return False
                    else:
                        print(">n")
                        print ("Quitting.")
                        sys.exit()

            #Connection successful
            self.failed_tries = 0
            print("\nConnected to " + self.server_addr + ":" + str(self.server_port) + "\n")
            return True


    # Will send the request through self.sock according to the protocol documentation
    # Uses values self.protocol_version, self.method and self.arg for building the request
    #    Exception to this is if the request string is supplied as an argument
    # Returns True if successfully sent the request through the socket, or False if unsuccessful

    def sendRequest(self, request=""):
        try:
            if (request == ""):
                request = (self.protocol_version + " " +
                          self.method + " " +
                          self.arg + "\r\n").encode("utf-8")
            else:
                request = request.encode("utf-8")

            self.sock.send(request)

        except socket.error:
            print ("Connection error while trying to send request..")
            return False

        except socket.timeout:
            print ("Socket timed out while trying to send..")
            return False

        return request.decode("utf-8")


    # Receive a response from self.sock
    # Will call to itself again recursively if unsuccessful and obey MAX_FAILED_TRIES and SECONDS_BETWEEN_TRIES
    # Returns False if unsuccessful, returns the received message as string if successful
    def getResponse(self):
        if (self.failed_tries >= MAX_FAILED_TRIES):
            print("Failed to receive a response from server after " + str(MAX_FAILED_TRIES) + " tries.")
            print("THIS IS A CURRENTLY KNOWN BUG which occurs when the server was just restarted. Simply try again!")
            if (self.sock):
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.sock = False
                raw_input("Connection closed. Just try again!")
            return False

        wholeResponse = ""
        while True:
            try:
                receivedString = self.sock.recv(1024).decode('utf-8')
                wholeResponse += receivedString

                if (wholeResponse[-2:] == "\r\n"):
                    self.failed_tries = 0
                    return wholeResponse
                else:
                    continue

            except socket.timeout:
                print ("\nNo response from server (timeout)")
                return False

            except Exception as e:
                self.failed_tries += 1
                time.sleep(SECONDS_BETWEEN_TRIES)
                return self.getResponse()

        if (self.sock):
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.sock = False
            raw_input("Connection closed. Press enter to continue..")


Client()
