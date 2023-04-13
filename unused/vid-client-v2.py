import cv2
import socket
import pickle
import struct
import datetime

# Socket connection setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '127.0.1.1'  # Replace with the IP address of the server
port = 9999
client_socket.connect((host_ip, port))
data = b""
payload_size = struct.calcsize("L")

# Video recording setup
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
record = False
out = None
filename = None

while True:
    # Receive the serialized frames from the server and deserialize them using pickle
    while len(data) < payload_size:
        packet = client_socket.recv(4*1024)
        if not packet:
            break
        data += packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]
    
    while len(data) < msg_size:
        data += client_socket.recv(4*1024)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    
    # Display the received frames
    cv2.imshow('Received Video', frame)
    key = cv2.waitKey(1)
    
    # Record video if 'r' key is pressed
    if key == ord('r') and not record:
        record = True
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"record_{timestamp}.mp4"
        out = cv2.VideoWriter(filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
        print(f"Recording started. Saving to {filename}")
    elif key == ord('r') and record:
        record = False
        out.release()
        print(f"Recording stopped. Saved to {filename}")
        filename = None
        
    # Write frames to video file if recording is enabled
    if record:
        out.write(frame)
        
    # Exit if 'q' key is pressed
    if key == ord('q'):
        break

# Clean up resources
if out is not None:
    out.release()
cv2.destroyAllWindows()
client_socket.close()
