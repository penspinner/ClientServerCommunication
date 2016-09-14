# Steven Liao
# Course project

import sys
from socket import *
import struct

def main():
	# Get the server hostname and port as command line arguments
	argv = sys.argv
	host = argv[1]
	port = int(argv[2])
	print host + str(port)
	 
	# Create TCP client socket
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((host, port))

	correctNumArgs = False

	# Start looping 
	while True:

		userInput = raw_input("> ")
		userInputList = userInput.split(" ")

		if userInputList[0] == 'help':
			help()
			continue
		elif userInputList[0] == 'put':
			correctNumArgs = put(userInputList[1:], clientSocket)
		elif userInputList[0] == 'get':
			correctNumArgs = get(userInputList[1:], clientSocket)
		elif userInputList[0] == 'del':
			correctNumArgs = delete(userInputList[1:], clientSocket)
		elif userInputList[0] == 'browse':
			correctNumArgs = browse(clientSocket)
		elif userInputList[0] == 'exit':
			send_one_message(clientSocket, "EXIT\r\n\r\n")
			break
		else:
			print userInput + ': command not found.\nEnter \'help\' to see accepted commands.'

		# Determine if we should receive from server depending on whether
		# the correct number of arguments was inserted.
		if correctNumArgs:
			response = recv_one_message(clientSocket)
			#print response

                        # Error 100
			if response == '100 Empty Database\r\n\r\n':
				print 'Error 100: Database is empty.'
			# Error 404
			elif response == '404 Not Found\r\n\r\n':
				print 'Error 404: Name record cannot be found in database.'
			# Return code 200 successful
			elif response == '200 OK\r\n\r\n':
				print 'Command has been completed.'
			# Return successful with more in body.
			elif '200 OK\r\n\r\n' in response:
				# Retrieve and store the value or message behind the successful return code
				# into a variable and print it.
				val = response.split('200 OK\r\n\r\n')[1]
				print val

		correctNumArgs = False

	# Close the client socket.
	clientSocket.close()

def help():
	print 'The commands include:\n' + \
			'help\t --Prints out the commands available.\n' + \
			'put [name] [value] [type]\t --Puts the specified name record into the server.\n' + \
			'get [name] [type]\t --Retrieves the specified name record from the server.\n' + \
			'del [name] [type]\t --Deletes the specified name record from the server.\n' + \
			'browse\t --Prints a list of all the name records in the server.\n' + \
			'exit\t --Exits the program.'

def put(list, clientSocket):
	# Make sure there are only 3 arguments after put.
	if len(list) == 3:

		# Need to check the types and values inside the list
		if (list[2] == 'A' or list[2] == 'NS'):
			# Sends the parameters as a string.
			message = 'PUT\r\n\r\n' + ' '.join(list)
			send_one_message(clientSocket, message)
			return True
		else:
			print 'Invalid record type.'
	else:
		print 'Incorrect number of arguments.'
		return False

def get(list, clientSocket):
	# Make sure there are only 2 arguments after get.
	if len(list) == 2:

		#S Sends the parameters as a string.
		message = 'GET\r\n\r\n' + ' '.join(list)
		send_one_message(clientSocket, message)
		return True
	else:
		print 'Incorrect number of arguments.'
		return False

def delete(list, clientSocket):
	# Make sure there are only 2 arguments after delete.
	if len(list) == 2:

		# Sends the parameters as a string.
		message = 'DEL\r\n\r\n' + ' '.join(list)
		send_one_message(clientSocket, 'DEL\r\n\r\n' + ' '.join(list))
		return True
	else:
		print 'Incorrect number of arguments.'
		return False

def browse(clientSocket):
	print 'Browsing the server...'
	send_one_message(clientSocket, 'BROWSE\r\n\r\n')
	return True

# This function sends a message to the socket server.	
def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

# This function receives a message from the socket server.
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
