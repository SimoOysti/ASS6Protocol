import os


# Will print a newline followed by the specified msg, if echoVar == True
def echo(echoVar, msg):
    if (echoVar):
        print("\n" + msg)



# Create the file specified as argument, IFF it doesn't exist yet.
# Returns False if file creation failed
# Returns True if file exists already OR if it was created successfully
def createFileIfNotExists(path):     
    if (not (os.path.isfile(path)) ):
        try:
            with open(path, "w") as f:
                f.close()
        except Exception as e:
            return False
        
    return True
    
