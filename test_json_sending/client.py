import socket
import json
import time

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000        # The port used by the server

def start_client():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                print(f"Connected to {HOST}:{PORT}")
                data = {"name": "John", "age": 30}
                s.sendall(json.dumps(data).encode())
                response = s.recv(1024)
                print("Server Response:", json.loads(response.decode()))
                time.sleep(5)
        except:
            print("Lost connection with server. Reconnecting in 5 seconds...")
            time.sleep(5)

start_client()
