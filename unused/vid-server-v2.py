import cv2
import socket
import pickle
import struct

# OpenCV video capture object
cap = cv2.VideoCapture(0)

# Socket connection setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('Host IP:', host_ip)
port = 9999
socket_address = (host_ip, port)
server_socket.bind(socket_address)
server_socket.listen(5)
print("Listening at:", socket_address)

while True:
    client_socket, addr = server_socket.accept()
    print('Got connection from:', addr)
    if client_socket:
        while True:
            # Read frames from the video capture object
            ret, frame = cap.read()
            
            # Serialize the frames using pickle and send them over the socket
            data = pickle.dumps(frame)
            message_size = struct.pack("L", len(data))
            client_socket.sendall(message_size + data)
