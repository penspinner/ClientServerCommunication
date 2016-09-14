import os, sys
from socket import *
import subprocess
import thread
import struct

ports = dict()

def main():
    #load name server ports into dictionary
    try:
        f = open("manager.in")
    except IOError:
        print "File manager.in does not exist in the same directory."
        return
    
    for line in f:
        typ = line.replace("\n", "")
        server = subprocess.Popen(["python", "server2.py", typ],
                                  stdout = subprocess.PIPE)
        while True:
            line = server.stdout.readline()
            if "Listening on port" in line:
                port = line.split()[3]
                print "Type " + typ + " name server listening on port " + port
                ports[typ] = port
                break
    f.close()
            

    #create socket        
    managerport = 12345
    managersocket = socket(AF_INET, SOCK_STREAM)
    managersocket.bind(('', managerport))
    managersocket.listen(5)
    print "MANAGER: Listening on port " + str(managerport)

    #accept connections from clients
    while 1:
        clientsocket, clientaddr = managersocket.accept()
        print "MANAGER: IP " + clientaddr[0] + " connected"
        thread.start_new_thread(handler, (clientsocket, clientaddr))
    managersocket.close()

def handler(clientsocket, clientaddr):
    while True:
        try:
            msg = recv_one_message(clientsocket)
        except error:
            print "IP " + clientaddr[0] + " has been forcibly closed."
            clientsocket.close()
            break
        if (msg.split("\r\n\r\n")[0] == 'EXIT'):
            print "IP " + clientaddr[0] + " has disconnected."
            clientsocket.close()
            break
        else:
            print "MANAGER: Received request from IP " + clientaddr[0]
            typ = msg.split("\r\n\r\n")[1]
            if typ in ports:
                send_one_message(clientsocket, "200 OK\r\n\r\n" + ports[typ])
                print 'MANAGER: Request acknowledged: Response with' \
                      ' name server port sent'
            else:
                send_one_message(clientsocket, "404 Not Found\r\n\r\n")
                print 'MANAGER: Request not acknowledged: Name server type ' \
                      'requested not found'

#The socket is not going to receive the entire message at once. Therefore,
#it waits to combine the multiple packets into one message using the
#size of the message indicated in the first 4 bytes of the message
def recvall(clientsocket, count):
    buf = b''
    while count:
        newbuf = clientsocket.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

#Adds 4 bytes in the front to tell the receiver how many
#total bytes the receiver is going to receive for the message
def send_one_message(clientsocket, msg):
	length = len(msg)
	clientsocket.sendall(struct.pack('!I', length))
	clientsocket.sendall(msg)

def recv_one_message(clientsocket):
	lengthbuf = recvall(clientsocket, 4)
	length, = struct.unpack('!I', lengthbuf)
	return recvall(clientsocket, length)
    
if __name__ == '__main__':
    main()
