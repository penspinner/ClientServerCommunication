# Steven Liao
# Course project

import sys 
from socket import *
import struct

# Runs from this main function.
def main():
	# Get the server hostname and port as command line arguments
	argv = sys.argv                      
	host = argv[1]
	port = int(argv[2])

	# Connect to the manager.
	managerSocket = socket(AF_INET, SOCK_STREAM)
	managerSocket.connect((host, port))

	print 'Commands:\n' + \
	'type [type]\t --Enter a type server with the specified type.\n' + \
	'exit\t\t --Exit the program.'

	while True:
		# Prompt user to enter the type of the name record.
		userInput = raw_input('> ')
		userInputList = userInput.split(' ')
		if userInput == 'exit':
                        send_one_message(managerSocket, 'EXIT\r\n\r\n')
			break
		elif userInputList[0] == 'type':
                        if len(userInputList) != 2:
                                print "Wrong number of arguments."
                                continue
			send_one_message(managerSocket, 'TYPE\r\n\r\n' + userInputList[1])
			print 'Sending type to manager...'

	        # Receive the string address from the manager.
                        try:
                                response = recv_one_message(managerSocket)
			except error:
                                print "Manager has been closed forcibly"
                                break
			if response == '404 Not Found\r\n\r\n':
				print 'Error 404: Type ' + userInput + ' server not found.'
			elif '200 OK\r\n\r\n' in response:
				print 'Receiving type server address from manager...'

				# Splits the 200 OK\r\n\r\n in the front of the string.
				val = response.split('\r\n\r\n')[1]

				# Gets the address and port of the server, and then connects to the server.
				# Initialize client socket that will be connected to a type server.
                                clientSocket = socket(AF_INET, SOCK_STREAM)
				address = host
				port = int(val)
				clientSocket.connect((address, port))
				print 'Connected to server' + ' ' + clientSocket.getsockname()[0] + ' ' + str(port)
				inServer(clientSocket, userInputList[1])
		else:
			print userInput + ': command not found.'

	# Close the manager socket.
	managerSocket.close()
	print 'Exiting program.'

# The client is now in the type server, and can perform commands to the server
# The type is not needed anymore.
def inServer(clientSocket, typ):
	print 'You are now connected to type ' + typ + ' server.'
	help()
	correctNumArgs = False

	# Start looping 
	while True:
		# Gets input from the user.
		userInput = raw_input('> ')
		userInputList = userInput.split(' ')

		if userInputList[0] == 'help':
			help()
			continue
		elif userInputList[0] == 'put':
			correctNumArgs = put(userInputList[1:], clientSocket, typ)
		elif userInputList[0] == 'get':
			correctNumArgs = get(userInputList[1:], clientSocket, typ)
		elif userInputList[0] == 'del':
			correctNumArgs = delete(userInputList[1:], clientSocket, typ)
		elif userInputList[0] == 'browse':
			correctNumArgs = browse(clientSocket)
		elif userInput == 'done':
			send_one_message(clientSocket, 'EXIT\r\n\r\n')
			break
		else:
			print userInput + ': command not found.\nEnter \'help\' to see accepted commands.'

		# Determine if we should receive from server depending on whether
		# the correct number of arguments was inserted.
		if correctNumArgs:
                        try:
                                response = recv_one_message(clientSocket)
                        except error:
                                print "Name server has been closed forcibly"
                                break

			# Error 100
			if response == '100 Empty Database\r\n\r\n':
				print 'Error 100: Database is empty.'
			# Error 404
			elif response == '404 Not Found\r\n\r\n':
				print 'Error 404: Name record does not exist in database.'
			# Return code 200 successful
			elif response == '200 OK\r\n\r\n':
				print 'Command has been completed.'
			# Return successful with more in body.
			elif '200 OK\r\n\r\n' in response:
				# Retrieve and store the value or message behind the successful return code
				# into a variable and print it.
				val = response.split('\r\n\r\n')[1]
				print val

		correctNumArgs = False

	# Close the client socket.
	clientSocket.close()
	print 'Disconnecting from type ' + typ + ' server.'

def help():
	print 'The commands include:\n' + \
			'help\t --Prints out the commands available.\n' + \
			'put [name] [value]\t --Puts the specified name record into the server.\n' + \
			'get [name]\t --Retrieves the specified name record from the server.\n' + \
			'del [name]\t --Deletes the specified name record from the server.\n' + \
			'browse\t --Prints a list of all the name records in the server.\n' + \
			'done\t --Disconnects from the server.'

def put(list, clientSocket, typ):
	# Make sure there are only 3 arguments after put.
	if len(list) == 2:

		# Sends the parameters as a string.
		message = 'PUT\r\n\r\n' + ' '.join(list) + " " + typ
		print message
		send_one_message(clientSocket, message)
		return True
	else:
		print 'Incorrect number of arguments or invalid record types.'
		return False

def get(list, clientSocket, typ):
	# Make sure there are only 2 arguments after get.
	if len(list) == 1:

		#S Sends the parameters as a string.
		message = 'GET\r\n\r\n' + ' '.join(list) + " " + typ
		print message
		send_one_message(clientSocket, message)
		return True
	else:
		print 'Incorrect number of arguments.'
		return False

def delete(list, clientSocket, typ):
	# Make sure there are only 2 arguments after delete.
	if len(list) == 1:

		# Sends the parameters as a string.
		message = 'DEL\r\n\r\n' + ' '.join(list) + " " + typ
		print message
		send_one_message(clientSocket, message)
		return True
	else:
		print 'Incorrect number of arguments.'
		return False

def browse(clientSocket):
	print 'Browsing the server...'
	send_one_message(clientSocket, 'BROWSE\r\n\r\n')
	return True

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

if __name__ == '__main__':
	main()
