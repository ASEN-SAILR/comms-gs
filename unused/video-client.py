import cv2
import socket
import pickle
import struct
import datetime

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '127.0.1.1'  # replace with the server IP address
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

# grab the width, height, and fps of the frames in the video stream.

# initialize the FourCC and a video writer object
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# output = cv2.VideoWriter('output.avi', fourcc, 10.0, (frame_width, frame_height))


##############################################################################
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
file_name = f"video_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.avi"
out = cv2.VideoWriter(file_name, fourcc, 5.0, (frame_width, frame_width))


# Start receiving the video
while True:
    # Receive the frame size from the server
    data_size = struct.unpack("I", client_socket.recv(4))[0]

    # Receive the frame from the server
    data = b""
    while len(data) < data_size:
        packet = client_socket.recv(data_size - len(data))
        
            break
        data += packetif not packet:
            break
        data += packet

    # Convert the byte string to a frame
    frame = pickle.loads(data)

    out.write(frame)

    # Display the frame in the window
    cv2.imshow('Live Streaming', frame)

    # # Write the frame to the output video file if recording is enabled
    # if record:
    #     if not recording:
    #         # Create the video writer and start recording
    #         writer = cv2.VideoWriter(
    #             filename, cv2.VideoWriter_fourcc(*'MJPG'), 30.0, (frame_width, frame_height))
    #         recording = True
    #     # Write the frame to the output video file
    #     writer.write(frame)

    # Exit on ESC
    if cv2.waitKey(1) == 27:
        break

# Clean up
# Release the video writer when the video streaming is complete
out.release()

cv2.destroyAllWindows()
client_socket.close()
