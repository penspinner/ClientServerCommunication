from socket import *
import threading
import thread
import struct

database = dict()
lock = threading.Lock()

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

#Loads the dictionary from the file. The keys to the dictionary
#are the names of the records and the dictionary returns a
#list of tuples containing the value and type of the record
def load_database(f):
	for line in f:
		name, value, typ = line.split()
		if name in database:
			database[name].append((value, typ))
		else:
			database[name] = [(value, typ)]
			
#Writes the database to the file
def save_database(f):
	msg = ""
	for key in database:
		for x in xrange(len(database[key])):
			msg += key + " " + database[key][x][0] + " " + database[key][x][1] + "\n"
	f.write(msg)


def handler(clientsocket, addr, f):
	while (1):
		request = recv_one_message(clientsocket)
		method, body = request.split("\r\n\r\n")		
		if method == "PUT":
			put(body, clientsocket, f)
		elif method == "GET":
			get(body, clientsocket)
		elif method == "DEL":
			delete(body, clientsocket, f)
		elif method == "BROWSE":
			browse(clientsocket)
		elif method == "EXIT":
			break

	f.truncate(0)
	save_database(f)
	clientsocket.close()
	print "Client " + str(addr) + " disconnected."
		
#Replaces the stored record with the record in the request if it already
#exists in the dictionary. If not, it is added to the dictionary. 
def put(body, clientsocket, f):
	lock.acquire()
	try:
		found = False
		name, value, typ = body.split(" ")
		if (name in database):
			for x in xrange(len(database[name])):
				if (database[name][x][1] == typ):
					database[name][x] = (value, typ)
					found = True
					break
			if (not found):
				database[name].append((value, typ))
		else:
			database[name] = [(value, typ)]
		send_one_message(clientsocket, "200 OK\r\n\r\n")
		f.truncate(0)
		save_database(f)
	finally:
		lock.release()

#Returns the value of a record with the name and type in the request
def get(body, clientsocket):
	lock.acquire()
	try:
		found = False
		name, typ = body.split(" ")
		if (name in database):
			for x in xrange(len(database[name])):
				if (database[name][x][1] == typ):
					found = True
					value = database[name][x][0]
					send_one_message(clientsocket, "200 OK\r\n\r\n" + value)
					break
			if (not found):
				send_one_message(clientsocket, "404 Not Found\r\n\r\n")
		else:
			send_one_message(clientsocket, "404 Not Found\r\n\r\n")
	finally:					      
		lock.release()

#Deletes a record with the name and type in the request
def delete(body, clientsocket, f):
	lock.acquire()
	try:
		found = False
		name, typ = body.split(" ")
		if (name in database):
			for x in xrange(len(database[name])):
				if (database[name][x][1] == typ):
					found = True
					#del database[name][x]
					database.pop(name)
					send_one_message(clientsocket, "200 OK\r\n\r\n")
					f.truncate(0)
					save_database(f)			
			if (not found):
				send_one_message(clientsocket, "404 Not Found\r\n\r\n")
		else:
			send_one_message(clientsocket, "404 Not Found\r\n\r\n")
	finally:					      
		lock.release()

#Shows all the records in the dictionary	
def browse(clientsocket):
	lock.acquire()
	try:
		if (not database):
			send_one_message(clientsocket, "100 Empty Database\r\n\r\n")
		else:
			msg = ""
			for key in database:
				for x in xrange(len(database[key])):
					msg += key + " " + database[key][x][1] + "\n"
			send_one_message(clientsocket, "200 OK\r\n\r\n" + msg)
			print msg
	finally:					      
		lock.release()

#Main
if __name__ == "__main__":
	f = None

	#Try to open the existing file.
	try:
		f = open("database.txt", "r+")
		load_database(f)
	#If file cannot be found, make a new file and write to that.
	except IOError:
		f = open("database.txt", "w+")
		
	serversocket = socket(AF_INET, SOCK_STREAM)
	serversocket.bind(('', 0))
	serversocket.listen(5)
	print "Listening on port", serversocket.getsockname()[1]	
	while (1):
		clientsocket, addr = serversocket.accept()
		print "Client " + str(addr) + "  connected."
		thread.start_new_thread(handler, (clientsocket, addr, f))
	serversocket.close()
	f.close()

				
