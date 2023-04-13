import socket
import sys
import json


jsonResult = {"first": "You're", "second": "Awesome!"}
jsonResult = json.dumps(jsonResult)

bytes_Result = bytes(jsonResult, 'utf-8')

while True:

	try:
		sock = socket.socket()
	except socket.error as err:
		print('Socket error because of %s' % (err))

	port = 1500
	address = "127.0.0.1"

	message=input('Enter message to send or q to quit: ')

	if message == 'q':
		break

	try:
		sock.connect((address, port))
		sock.send(bytes(message, encoding='utf8'))
	except socket.gaierror:

		print('There an error resolving the host')

		sys.exit()

	print(jsonResult, 'was sent!')

	sock.close()
