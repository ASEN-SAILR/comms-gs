import socket
import json
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5000        # Port to listen on (non-privileged ports are > 1023)


def start_server():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((HOST, PORT))
		s.listen()
		print(f"Server listening on {HOST}:{PORT}")
		while True:
			try:
				conn, addr = s.accept()
				print(f"Connected by {addr}")
				while True:
					data = conn.recv(1024)
					if not data:
						break
					received_data = json.loads(data.decode())
					print("Received Data:", received_data)
					response_data = {"status": "OK"}
					conn.sendall(json.dumps(response_data).encode())
			except:
				print("Lost connection with client. Reconnecting in 5 seconds...")
				time.sleep(5)

start_server()
