import numpy as np
import struct
import pickle
import cv2
import socket
import threading
import json
from queue import Queue


class Server:
    def __init__(self, host='', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sockets = []
        self.message_queue = Queue()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connected to {client_address}")
            self.client_sockets.append(client_socket)

            # Start a new thread to handle this client
            client_thread = threading.Thread(
                target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        while True:
            try:
                # Receive the message from the client
                message = client_socket.recv(1024).decode()
                if message:
                    # Add the message to the queue
                    self.message_queue.put((client_socket, message))
                else:
                    # The client has disconnected
                    self.client_sockets.remove(client_socket)
                    print(f"Disconnected from {client_socket.getpeername()}")
                    break
            except ConnectionResetError:
                # The client has disconnected
                self.client_sockets.remove(client_socket)
                print(f"Disconnected from {client_socket.getpeername()}")
                break

    def broadcast(self, message):
        # Add the message to the queue for each client
        for client_socket in self.client_sockets:
            self.message_queue.put((client_socket, message))

    def send_to_client(self, client_socket, message):
        # Add the message to the queue for the specified client
        self.message_queue.put((client_socket, message))
		

class Client:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_queue = Queue()

    def connect(self):
        self.client_socket.connect((self.host, self.port))

        # Start a new thread to handle incoming messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                # Receive the message from the server
                message = self.client_socket.recv(1024).decode()
                if message:
                    # Add the message to the queue
                    self.message_queue.put(message)
                else:
                    # The server has disconnected
                    print("Disconnected from the server")
                    break
            except ConnectionResetError:
                # The server has disconnected
                print("Disconnected from the server")
                break

    def send_message(self, message):
        # Send the message to the server
        self.client_socket.sendall(message.encode())

    def get_message(self):
        # Get the next message from the queue
        if not self.message_queue.empty():
            message = self.message_queue.get()
            return json.loads(message)
        else:
            return None


# 1.1. Handling messages on the server side
# In the previously provided implementation of the Server class, incoming messages 
# are stored in a message queue, but they are not processed. 
# You can add a process_messages method to the Server class that reads messages from 
# the queue and processes them. For example, you could write a function that takes a 
# JSON message and performs some action based on its content. Here's an example implementation:


    def handle_message(self, client_socket, message):
        # Parse the message as JSON
        data = json.loads(message)

        # Extract the type of the message
        message_type = data.get("type")

        # Handle different types of messages
        if message_type == "echo":
            # Echo the message back to the client
            self.send_to_client(client_socket, message)
        elif message_type == "broadcast":
            # Broadcast the message to all clients
            self.broadcast(message)
        elif message_type == "quit":
            # Disconnect the client
            self.client_sockets.remove(client_socket)
            client_socket.close()
            print(f"Disconnected from {client_socket.getpeername()}")
        else:
            # Unknown message type
            raise ValueError(f"Unknown message type: {message_type}")


# 1.2. Stopping the server
# It's also useful to be able to stop the server when it's no longer needed. 
# You can add a stop method to the Server class that stops the server and closes 
# all client connections. Here's an example implementation:

# def stop(self):
#        for client_socket in self.client_sockets:
#             client_socket.close()
#         self.server_socket.close()


# 2.1. Disconnecting from the server
# In the previously provided implementation of the Client class, the client socket 
# is not closed when the client is disconnected from the server. You can add a 
# disconnect method to the Client class that sends a "quit" message to the server 
# and closes the client socket. Here's an example implementation:
# def disconnect(self):
#     # Send a "quit" message to the server
#     message = {"type": "quit"}
#     self.send_message(json.dumps(message))

#     # Close the client socket
#     self.client_socket.close()


# 2.2. Reconnecting to the server
# It's also useful to be able to reconnect to the server
# def reconnect(self):
#        # Close the current client socket if it's open
#        if self.client_socket:
#             self.client_socket.close()

#         # Create a new client socket and connect to the server
#         self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.client_socket.connect((self.host, self.port))

#         # Start the message receiving thread
#         self.receive_thread = threading.Thread(target=self.receive_messages)
#         self.receive_thread.start()

#         # Send a "hello" message to the server to re-establish the connection
#         message = {"type": "hello", "username": self.username}
#         self.send_message(json.dumps(message))

# In this implementation, the reconnect method first closes the current client socket 
# if it's open. Then it creates a new client socket using the same host and port, and 
# connects to the server. It also starts a new message receiving thread. Finally, it sends 
# a "hello" message to the server to re-establish the connection, including the client's username 
# in the message.

# Note that if the client is currently connected to the server when the reconnect method is called, 
# the connection will be closed and any unsent messages will be lost. You may want to add additional 
# logic to handle this case depending on your use case.


# 1.1. Keep-alive messages
# To ensure that the server doesn't disconnect the client due to inactivity, you can add a keep-alive mechanism 
# to the Client class. This involves periodically sending a special message to the server to let it know that the 
# client is still connected. Here's an example implementation:

# class Client:
#     ...

#     def send_keep_alive(self):
#         while self.connected:
#             time.sleep(self.keep_alive_interval)
#             message = {"type": "keep_alive"}
#             self.send_message(json.dumps(message))

#     def start_keep_alive(self, interval=60):
#         self.keep_alive_interval = interval
#         self.keep_alive_thread = threading.Thread(target=self.send_keep_alive)
#         self.keep_alive_thread.start()

# In this implementation, the start_keep_alive method takes an optional interval argument that specifies how often to 
# send keep-alive messages (in seconds). It creates a new thread that calls the send_keep_alive method every interval seconds. 
# The send_keep_alive method sends a "keep_alive" message to the server using the send_message method.


# 1.1. File transfer
# You can add the ability for clients to send files to the server. Here's an example implementation:
# class Client:
#     ...

#     def send_file(self, file_path):
#         with open(file_path, "rb") as f:
#             file_name = os.path.basename(file_path)
#             file_size = os.path.getsize(file_path)
#             message = {"type": "file", "name": file_name, "size": file_size}
#             self.send_message(json.dumps(message))

#             # Send the file data in chunks
#             while True:
#                 data = f.read(self.buffer_size)
#                 if not data:
#                     break
#                 self.client_socket.sendall(data)

#     def receive_file(self, file_name, file_size):
#         with open(file_name, "wb") as f:
#             bytes_received = 0
#             while bytes_received < file_size:
#                 data = self.client_socket.recv(self.buffer_size)
#                 f.write(data)
#                 bytes_received += len(data)


# Sure, here are a few ways to increase the speed of file transfer in the Client and Server classes:

# 1. Client:
# 1.1. Use a larger buffer size
# One way to increase the speed of file transfer is to use a larger buffer size when sending and receiving 
# file data. By default, we're using a buffer size of 1024 bytes in our previous implementation. We can increase 
# this to a larger value, like 8192 bytes, to speed up the transfer:

# class Client:
#     ...

#     def send_file(self, file_path):
#         with open(file_path, "rb") as f:
#             file_name = os.path.basename(file_path)
#             file_size = os.path.getsize(file_path)
#             message = {"type": "file", "name": file_name, "size": file_size}
#             self.send_message(json.dumps(message))

#             # Send the file data in larger chunks
#             while True:
#                 data = f.read(8192)
#                 if not data:
#                     break
#                 self.client_socket.sendall(data)

#     def receive_file(self, file_name, file_size):
#         with open(file_name, "wb") as f:
#             bytes_received = 0
#             while bytes_received < file_size:
#                 data = self.client_socket.recv(8192)
#                 f.write(data)
#                 bytes_received += len(data)


# 1.2. Use multiple threads
# Another way to increase the speed of file transfer is to use multiple threads for sending and receiving file data. 
# This can help utilize multiple CPU cores and increase the throughput of the transfer. Here's an example implementation:


# class Client:
#     ...

#     def send_file(self, file_path):
#         with open(file_path, "rb") as f:
#             file_name = os.path.basename(file_path)
#             file_size = os.path.getsize(file_path)
#             message = {"type": "file", "name": file_name, "size": file_size}
#             self.send_message(json.dumps(message))

#             # Send the file data in multiple threads
#             threads = []
#             while True:
#                 data = f.read(8192)
#                 if not data:
#                     break
#                 thread = threading.Thread(
#                     target=self.client_socket.sendall, args=(data,))
#                 thread.start()
#                 threads.append(thread)

#             for thread in threads:
#                 thread.join()

#     def receive_file(self, file_name, file_size):
#         with open(file_name, "wb") as f:
#             bytes_received = 0
#             while bytes_received < file_size:
#                 data = self.client_socket.recv(8192)
#                 f.write(data)
#                 bytes_received += len(data)


# In this implementation, the send_file method spawns a new thread for each chunk of data to be sent, and then waits 
# for all the threads to finish using the join method. This can help send the file data more quickly. Similarly, the 
# receive_file method can also use multiple threads to receive file data in parallel.

# 2. Server:
# 2.1. Use multiple threads
# The server can also use multiple threads to handle file transfers from multiple clients in parallel. Here's an example implementation:


# class Server:
#     ...

#     def handle_client(self, client_socket, client_address):
#         ...
#         while True:
#             try:
#                 message = client_socket.recv(self.buffer_size).decode()
#                 self.handle_message(client_socket, message)
#             except Exception as e:
#                 self.disconnect_client(client_socket)
#                 print(f"Error receiving message from {client_address}: {e}")
#                 break

#     def handle_file_transfer(self, client_socket, file_name, file_size):
#         with open(file_name, "wb") as f:
#             bytes_received = 0
#             threads = []
#             while bytes_received < file_size:
#                 data = client_socket.recv(8192)
#                 f.write(data)
#                 bytes_received += len(data)

#                 # Spawn a new thread for each chunk of data received
#                 thread = threading.Thread(
#                     target=client_socket.recv, args=(8192,))
#                 thread.start()
#                 threads.append(thread)

#             # Wait for all the threads to finish
#             for thread in threads:
#                 thread.join()

#         print(
#             f"File '{file_name}' received from client {client_socket.getpeername()[0]}")


# In this implementation, the handle_file_transfer method receives file data in chunks of 8192 bytes and spawns a new thread 
# for each chunk of data to be received. This can help receive file data more quickly, as multiple threads can run in parallel 
# to receive data from the client socket. Finally, the method waits for all the threads to finish using the join method, and then 
# prints a message indicating that the file was successfully received.


class Client:
    ...

    def send_photo(self, file_path):
        with open(file_path, "rb") as f:
            # Read the photo file as binary data
            photo_data = f.read()

            # Create a dictionary with the photo data and file name
            data = {
                "type": "photo",
                "file_name": file_path.split("/")[-1],
                "photo_data": photo_data
            }

            # Serialize the dictionary as a JSON string and send it to the server
            message = json.dumps(data)
            self.socket.send(message.encode())


class Server:
    ...

    def handle_photo_transfer(self, client_socket, file_name, photo_data):
        with open(file_name, "wb") as f:
            f.write(photo_data)

        print(
            f"Photo '{file_name}' received from client {client_socket.getpeername()[0]}")





# To add fast live video functionality between the client and server using OpenCV and pickle, you could modify the Client and Server 
# classes to include methods for streaming and receiving video frames. Here's an example implementation:
# First, let's modify the Client class to include a method for sending live video frames using OpenCV and pickle:


# class Client:
#     ...

#     def send_video(self):
#         # Open the default camera device
#         cap = cv2.VideoCapture(0)

#         # Set the resolution of the camera device
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#         # Loop over the frames and send them to the server
#         while True:
#             ret, frame = cap.read()

#             # Serialize the frame as a pickle object and send it to the server
#             data = {
#                 "type": "video",
#                 "frame": pickle.dumps(frame)
#             }
#             # Serialize the dictionary as a JSON string and send it to the server
#             message = json.dumps(data)
#             self.socket.send(message.encode())
#         # Release the camera device
#         cap.release()

# In this implementation, the send_video method opens the default camera device, sets the resolution of the camera device, and loops over the frames. For each frame, it serializes the frame as a pickle object and sends it to the server as a JSON message.

# Next, let's modify the Server class to include a method for receiving live video frames using OpenCV and pickle:


# class Server:
#     ...

#     def handle_video_transfer(self, client_socket, frame_data):
#         # Deserialize the frame from the pickle object
#         frame = pickle.loads(frame_data)
#         # Display the frame
#         cv2.imshow("Server Video Stream", frame)
#         cv2.waitKey(1)
#         # Print a message indicating that a frame was received
#         print(f"Frame received from client {client_socket.getpeername()[0]}")
# To add fast live video functionality between the client and server using OpenCV and pickle, you could modify the Client and Server classes to include methods for streaming and receiving video frames. Here's an example implementation:

# First, let's modify the Client class to include a method for sending live video frames using OpenCV and pickle:

# python
# Copy code


class Client:
    ...

    def send_video(self):
        # Open the default camera device
        cap = cv2.VideoCapture(0)

        # Set the resolution of the camera device
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Loop over the frames and send them to the server
        while True:
            ret, frame = cap.read()

            # Serialize the frame as a pickle object and send it to the server
            data = {
                "type": "video",
                "frame": pickle.dumps(frame)
            }

            # Serialize the dictionary as a JSON string and send it to the server
            message = json.dumps(data)
            self.socket.send(message.encode())

        # Release the camera device
        cap.release()


# In this implementation, the send_video method opens the default camera device, sets the resolution of the camera device, and loops over the frames. For each frame, it serializes the frame as a pickle object and sends it to the server as a JSON message.

# Next, let's modify the Server class to include a method for receiving live video frames using OpenCV and pickle:

# python
# Copy code


class Server:
    ...

    def handle_video_transfer(self, client_socket, frame_data):
        # Deserialize the frame from the pickle object
        frame = pickle.loads(frame_data)

        # Display the frame
        cv2.imshow("Server Video Stream", frame)
        cv2.waitKey(1)

        # Print a message indicating that a frame was received
        print(f"Frame received from client {client_socket.getpeername()[0]}")


# In this implementation, the handle_video_transfer method receives the frame data as a pickle object, deserializes the frame, displays the frame using OpenCV, and prints a message indicating that a frame was received.

# By using OpenCV and pickle to stream and receive video frames, you can achieve fast live video functionality between the client and server.

# Finally, you could use the send_video method in the Client class to send live video frames, and the handle_video_transfer method in the Server class to receive the frames. For example:

# Sending live video from the client
# client = Client()
# client.connect("localhost", 8000)
# client.send_video()
# client.disconnect()

# # Handling the video stream on the server
# server = Server()
# server.start()




# To fully optimize the live video functionality between the client and server, we can implement a number of optimizations that can significantly improve the video streaming performance. Here are some potential optimizations:

# Use a more efficient video codec: By default, OpenCV uses the Motion-JPEG(MJPEG) codec for video streaming. While this codec produces high-quality video, it can be slow and consume a lot of bandwidth. Instead, we can use a more efficient codec such as H.264 or H.265 to reduce the bandwidth requirements and improve the streaming performance. OpenCV provides support for both H.264 and H.265 codecs, and we can select the codec using the cv2.VideoWriter class .

# Reduce the video frame size: Another way to reduce the bandwidth requirements and improve the streaming performance is to reduce the size of the video frames. This can be achieved by decreasing the resolution of the camera device or by resizing the frames before sending them over the network. However, we need to be careful not to reduce the frame size too much, as it can lead to a loss in video quality.

# Use UDP instead of TCP: While TCP is reliable and guarantees that all data is delivered, it can also be slow due to its overhead and congestion control mechanisms. UDP, on the other hand, is faster and more lightweight, but it is also less reliable and may lose some packets. Since live video streaming requires real-time delivery and can tolerate some packet loss, using UDP can be a good choice for improving the streaming performance. However, we need to implement some error correction mechanisms to handle packet loss and ensure that the video frames are not corrupted.

# Implement client-side buffering: One common issue with live video streaming is that the client may experience buffering or lag due to network latency or packet loss. To mitigate this issue, we can implement client-side buffering by buffering a few frames ahead of time and displaying them smoothly. This can improve the user experience and make the streaming more seamless.
# Here's an updated implementation of the Client and Server classes that incorporate these optimizations:


# class Client:
#     def __init__(self):
#         self.socket = None

#     def connect(self, host, port):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.socket.connect((host, port))

#     def send_video(self):
#         # Open the default camera device
#         cap = cv2.VideoCapture(0)

#         # Set the resolution of the camera device
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#         # Initialize the video writer with the H.264 codec
#         codec = cv2.VideoWriter_fourcc(*"H264")
#         writer = cv2.VideoWriter(
#             "temp.mp4", codec, 30.0, (640, 480), isColor=True)

#         # Loop over the frames and send them to the server
#         while True:
#             ret, frame = cap.read()

#             # Resize the frame to reduce the bandwidth requirements
#             resized_frame = cv2.resize(
#                 frame, (320, 240), interpolation=cv2.INTER_AREA)

#             # Serialize the frame as a byte string
#             _, buffer = cv2.imencode(".jpg", resized_frame)

#             # Pack the size of the frame and the frame data into a byte string
#             data = struct.pack(">L", len(buffer)) + buffer

#             # Send the frame data to the server using UDP
#             self.socket.send(data)

#             # Write the frame to the video file
#             writer.write(frame)

#         # Release the camera device and the video writer
#         cap.release()


# class Server:
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.socket.bind((host, port))

#     def receive_video(self):
#         # Create a window to display the video frames
#         cv2.namedWindow("Live Video", cv2.WINDOW_NORMAL)

#         # Initialize the video decoder and the buffer
#         decoder = cv2.VideoWriter_fourcc(*"H264")
#         buffer = b""

#         # Loop over the incoming packets and decode the video frames
#         while True:
#             # Receive the packet data and add it to the buffer
#             packet, _ = self.socket.recvfrom(65535)
#             buffer += packet

#             # Check if the buffer contains enough data to decode a frame
#             while len(buffer) > 4:
#                 # Unpack the size of the frame from the buffer
#                 size = struct.unpack(">L", buffer[:4])[0]

#                 # Check if the buffer contains enough data to decode the frame
#                 if len(buffer) < size + 4:
#                     break

#                 # Extract the frame data from the buffer
#                 data = buffer[4:size + 4]

#                 # Remove the extracted data from the buffer
#                 buffer = buffer[size + 4:]

#                 # Deserialize the frame data into a numpy array
#                 frame = cv2.imdecode(np.frombuffer(
#                     data, dtype=np.uint8), cv2.IMREAD_COLOR)

#                 # Decode and display the frame in the window
#                 cv2.imshow("Live Video", frame)
#                 cv2.waitKey(1)

#         # Destroy the window when the video streaming is complete
#         cv2.destroyAllWindows()


# To add support for video recording, we can modify the Server class to include a flag that specifies whether to record the live video stream or not . If the flag is set, the frames received from the client will be saved to a video file on the server-side. Here's the modified implementation:

# class Server:
#     def __init__(self, host, port, record=False, filename="output.mp4"):
#         self.host = host
#         self.port = port
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.socket.bind((host, port))
#         self.record = record
#         self.filename = filename
#         self.recording = False

#     def receive_video(self):
#         # Create a window to display the video frames
#         cv2.namedWindow("Live Video", cv2.WINDOW_NORMAL)

#         # Initialize the video decoder and the buffer
#         decoder = cv2.VideoWriter_fourcc(*"H264")
#         buffer = b""
#         writer = None

#         # Loop over the incoming packets and decode the video frames
#         while True:
#             # Receive the packet data and add it to the buffer
#             packet, _ = self.socket.recvfrom(65535)
#             buffer += packet

#             # Check if the buffer contains enough data to decode a frame
#             while len(buffer) > 4:
#                 # Unpack the size of the frame from the buffer
#                 size = struct.unpack(">L", buffer[:4])[0]

#                 # Check if the buffer contains enough data to decode the frame
#                 if len(buffer) < size + 4:
#                     break

#                 # Extract the frame data from the buffer
#                 data = buffer[4:size + 4]

#                 # Remove the extracted data from the buffer
#                 buffer = buffer[size + 4:]

#                 # Deserialize the frame data into a numpy array
#                 frame = cv2.imdecode(np.frombuffer(
#                     data, dtype=np.uint8), cv2.IMREAD_COLOR)

#                 # Decode and display the frame in the window
#                 cv2.imshow("Live Video", frame)
#                 cv2.waitKey(1)

#                 # Write the frame to the output video file if recording is enabled
#                 if self.record:
#                     if not self.recording:
#                         # Create the video writer and start recording
#                         writer = cv2.VideoWriter(
#                             self.filename, decoder, 30.0, (frame.shape[1], frame.shape[0]))
#                         self.recording = True
#                     # Write the frame to the output video file
#                     writer.write(frame)

#         # Release the video writer when the video streaming is complete
#         if writer:
#             writer.release()
#         # Destroy the window when the video streaming is complete
#         cv2.destroyAllWindows()

# This implementation adds a record flag to the Server class constructor, which specifies whether to record the live video stream or not . If record is set to True, the frames received from the client will be saved to a video file specified by the filename parameter. The video recording starts as soon as the first frame is received, and stops when the streaming is complete.
