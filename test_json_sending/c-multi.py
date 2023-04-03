import socket
import json
import time
import threading
import queue

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5000        # The port used by the server


def send_data(s, message_queue):
    while True:
        try:
            data = {"name": "John", "age": 30}
            s.sendall(json.dumps(data).encode())
            response = s.recv(1024)
            print("Server Response:", json.loads(response.decode()))
            message_queue.put(response)
            time.sleep(5)
        except:
            print("Lost connection with server. Reconnecting...")
            s.close()
            while True:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((HOST, PORT))
                    print(f"Reconnected to {HOST}:{PORT}")
                    break
                except:
                    print("Failed to reconnect. Retrying...")
                    time.sleep(5)


def receive_responses(message_queue):
    while True:
        try:
            response = message_queue.get()
            print("Received Response:", json.loads(response.decode()))
        except:
            print("Failed to receive response from server.")
        finally:
            message_queue.task_done()


def start_client():
    message_queue = queue.Queue()

    # Start a thread to receive responses from the server
    response_thread = threading.Thread(
        target=receive_responses, args=(message_queue,))
    response_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}")
            send_data_thread = threading.Thread(
                target=send_data, args=(s, message_queue))
            send_data_thread.start()
            send_data_thread.join()
        except:
            print("Failed to connect to server.")
            return


start_client()
