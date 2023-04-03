import socket
import json
import time
import threading
import queue

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5000        # Port to listen on (non-privileged ports are > 1023)


def handle_client(conn, addr, message_queue):
    print(f"Connected by {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            received_data = json.loads(data.decode())
            print("Received Data:", received_data)
            response_data = {"status": "OK"}
            message_queue.put((conn, json.dumps(response_data).encode()))
        except:
            print(f"Lost connection with client {addr}")
            conn.close()
            return


def send_responses(message_queue):
    while True:
        try:
            conn, response = message_queue.get()
            conn.sendall(response)
        except:
            print("Failed to send response to client.")
        finally:
            message_queue.task_done()


def start_server():
    message_queue = queue.Queue()

    # Start a thread to send responses to clients
    response_thread = threading.Thread(
        target=send_responses, args=(message_queue,))
    response_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            try:
                conn, addr = s.accept()
                thread = threading.Thread(
                    target=handle_client, args=(conn, addr, message_queue))
                thread.start()
            except:
                print("Lost connection with client. Waiting for new connection...")
                time.sleep(5)


start_server()
