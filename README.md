# This project has been created for Python 2.
ASS6 Protocol - version 1

Author: Simo �ysti
Date: March 29th 2019

************
Introduction
************
ASS6 is a protocol used for keeping a server-sided TODO-list which clients can modify remotely


In this document, (SP) stands for a single space and is a required part of the syntaxes
ASS6 will use the port 1338 by default and transfer data as plain text.

**************
Request syntax
**************
The syntax used by the client should be as follows:
PROTOCOL(SP)METHOD(SP)ARGUMENT\r\n

PROTOCOL used in the request has to match one that the server is using.

List of valid METHODs:
- LIST
- ADD
- DONE


***************
Response syntax
***************
The response syntax should be as follows:
PROTOCOL(SP)RESPONSECODE(SP)TITLE(SP)BODY\r\n

If PROTOCOL specified in the request doesn't match the one used by the server, an error response is returned.

List of valid response codes:
- LIST
- ADDED
- REMOVED


***********************
All definitions & Usage
***********************

Protocol:
---------

The following should be set as PROTOCOL in the request when wishing to use the protocol specified in this document:

ASS6_V1


Request methods:
----------------

- LIST
  Will request the entire to-do list from the server. Argument will be ignored so it should be left blank.

- ADD
  Will add a new entry to the to-do list as specified by the argument. The ID of the task will be the next free number on the list.

- DONE
  Will delete a task from the list by ID that is specified in the argument.


Example requests:
-----------------

ASS6_V1 LIST \r\n
ASS6_V1 ADD Vaccuum the lawn\r\n
ASS6_V1 DONE 2\r\n


Response codes:
---------------

- ERROR
  Means that request could not be processed successfully.
  TITLE will be the error code and BODY will be a description of it.

- LIST
  Means that the LIST request was successful
  TITLE will be the count of tasks currently on the list
  BODY will be the whole list, with each task being in the format: ID)(SP)THING-TO-DO\n


- ADDED
  Means that the ADD request was successful
  TITLE will be the current ID of the task that was added (ID's can change when removing an entry in the middle)
  BODY will be the text body of the task that was added successfully.

- REMOVED
  Means that the DONE request was successful
  TITLE will be the ID that was removed from the list
  BODY will be the text body of the task that was removed successfully


Example responses:
------------------

ASS6_V1 LIST 2 1) Vaccuum the lawn\n2) Buy butter\n\r\n
ASS6_V1 ADDED 3 Buy milk\r\n
ASS6_V1 REMOVED 3 Buy milk\r\n
ASS6_V1 ERROR ASS6InvalidID Server was unable to find a task with the ID specified in the DONE request.\r\n


Error codes:
------------

- ASS6InvalidID
  Server was unable to find a task with the ID specified in the DONE request.

- ASS6InvalidRequest
  The client sent a request using invalid syntax that the server failed to parse.

- ASS6FileNotAccessible
  Server had a problem when trying to access the to-do list file.

- ASS6UnsupportedProtocol
  Server does not support the protocol which was specified by the client in the request.

If a connection error occurs while processing a request, the client will not receive any response.
Therefore the client should handle connection problems by utilizing a timeout.
