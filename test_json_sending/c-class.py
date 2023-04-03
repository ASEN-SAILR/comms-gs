import socket
import json
import time
import threading
import queue

class Client:
	def __init__(self, host, port):

		self.host = host
		self.port = port
		self.connected = False
		self.received_queue = queue.Queue()
		self.sending_queue = queue.Queue()

		self.resend_attempts = 3

	# def (self):
	# 	send_data_thread = threading.Thread(
    #         target=self.send_message(), args=(self.socket, self.received_queue))
	# 	send_data_thread.start()
	# 	send_data_thread.join()

	def add_message(self, message):
		
		self.sending_queue.put(message)

	def start(self):
		self.connect()

		# Start a thread to receive responses from the server
		response_thread = threading.Thread(
			target=self.receive_responses, args=())
		response_thread.start()

		sending_thread = threading.Thread(
			target=self.send_messages, args=())
		sending_thread.start()

	def connect(self):

		while not self.connected:
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.socket.connect((self.host, self.port))
				self.connected = True
				print(f"Connected to {self.host}:{self.port}")
			except:
				print(
                    f"Error connecting to {self.host}:{self.port}, retrying in 5 seconds...")
				time.sleep(3)
	
	def check_connection(self,):
		try:
			self.socket.getpeername()
			self.connected = True
			return True
		except:
			self.connected = False
			return False

	def send_messages(self):
		
		while True:
			attempts = 0
			message = self.sending_queue.get()
			message_data = json.dumps(message).encode()
			while True:
				try:
					while True:
						self.socket.sendall(message_data)
						print(f"Sent message: {message}")
						response_data = self.socket.recv(1024)
						if response_data != b'':
							break
					# response = json.loads(response_data.decode())
					# print(f"Received response: {response}")
					self.received_queue.put(response_data.decode())
					break
				except:
					attempts += 1
					if attempts > self.resend_attempts:
						print(f"Error sending message: {message}")
						break
					print(
						f"Error sending message {message}, retrying in 5 seconds...")
					if not self.check_connection():
						print("Client no longer connected to server. Attempting to reconnect...")
						self.socket.close()
						self.connect()
					time.sleep(3)
				
			self.sending_queue.task_done()

	def receive_responses(self):
		while True:
			try:
				response = self.received_queue.get()
				print("Received Response:", json.loads(response))
			except:
				print("Failed to receive response from server.")
			finally:
				self.received_queue.task_done()


import random
def main():
	num_clients = 4
	client_dict = {}
	for i in range(1,num_clients+1):
		client_dict[i] = Client("localhost", 5000)
		client_dict[i].start()
	
	while True:
		client_num = random.randint(1, num_clients)
		message = {"client #": str(client_num),"text": "Hello, server from client "+str(client_num)+"!"}
		client_dict[client_num].add_message(message)
		time.sleep(5)
	# message = {"text": "Hello, server!"}
	# client.add_message(message)
	# message = {"text": "Another message"}
	# client.add_message(message)
	# counter = 0
	# while True:
	# 	time.sleep(3)
	# 	message = {"text": "Message #"+str(counter)}
	# 	client.add_message(message)
	# 	counter += 1
		
	# 	print(client.sending_queue.qsize())

if __name__ == "__main__":
    main()
