import cv2
import socket
import pickle
import struct

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '127.0.0.1'  # replace with the server IP address
port = 9999
socket_address = (host_ip, port)

# Connect to the server
client_socket.connect(socket_address)

# Receive the video dimensions from the server
frame_width = struct.unpack("I", client_socket.recv(4))[0]
frame_height = struct.unpack("I", client_socket.recv(4))[0]

# Create a window to display the video
cv2.namedWindow('Live Streaming', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Live Streaming', frame_width, frame_height)

# Start receiving the video
while True:
    # Receive the frame size from the server
    data_size = struct.unpack("I", client_socket.recv(4))[0]

    # Receive the frame from the server
    data = b""
    while len(data) < data_size:
        packet = client_socket.recv(data_size - len(data))
        if not packet:
            break
        data += packet

    # Convert the byte string to a frame
    frame = pickle.loads(data)

    # Display the frame in the window
    cv2.imshow('Live Streaming', frame)

    # Exit on ESC
    if cv2.waitKey(1) == 27:
        break

# Clean up
cv2.destroyAllWindows()
client_socket.close()
