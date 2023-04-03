import socket
import threading
import json
import queue


class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.connection = None
		self.address = None
		self.lock = threading.Lock()
		self.received_queue = queue.Queue()
		self.sending_queue = queue.Queue()

	def start(self):
		# Start a thread send responses to the clients
		response_thread = threading.Thread(
			target=self.send_responses, args=(self.received_queue,))
		response_thread.start()

		self.socket.bind((self.host, self.port))
		self.socket.listen()
		print(f"Listening on {self.host}:{self.port}")
		while True:
			client_socket, client_address = self.socket.accept()
			print(f"Connected to {client_address[0]}:{client_address[1]}")
			self.client_sockets.append(client_socket)

			client_thread = threading.Thread(
				target=self.handle_client, args=(client_socket,))
			client_thread.start()

	def handle_client(self):
		while True:
			data = self.connection.recv(1024)
			if data:

			if not data:
			print(
                            f"Connection lost with {self.address[0]}:{self.address[1]}")
			self.connection.close()
			break
			message = json.loads(data.decode())
			print(f"Received message: {message}")
			self.send_responses(message)

	def send_responses(self, message):
	response = {"status": "success",
             "message": f"Received message '{message}'"}
	response_data = json.dumps(response).encode()
	self.lock.acquire()
	try:
			self.connection.sendall(response_data)
			print(f"Sent response: {response}")
		except:
		print(
                    f"Error sending response to {self.address[0]}:{self.address[1]}")
		self.connection.close()
		finally:
			self.lock.release()


if __name__ == "__main__":
    server = Server("localhost", 5000)
    server.start()
