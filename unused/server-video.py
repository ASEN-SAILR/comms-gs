import cv2
import socket
import numpy
import pickle
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "127.0.0.1"
port = 6666
s.bind((ip, port))
while True:
    x = s.recvfrom(1000000)
    clientip = x[1][0]
    data = x[0]
    print(data)
    data = pickle.loads(data)
    print(type(data))
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    cv2.imshow('server', data)  # to open image
    if cv2.waitKey(10) == 13:
        break
cv2.destroyAllWindows()
