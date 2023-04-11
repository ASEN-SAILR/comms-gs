import sys

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

from PyQt6.QtGui import *

from PyQt6.QtMultimedia import *

from PyQt6.QtMultimediaWidgets import *

import cv2

import time

import os

import subprocess

import socket

import pickle

import struct

from pythonping import ping

import threading

import datetime

class mainWindow(QWidget):
    def __init__(self):
        super(mainWindow, self).__init__()


        # R-sync info
        self.system_password = 'asen-sailr'
        self.ground_station_path = '~/comms-gs/'
        # self.on_board_computer_ip = '10.203.178.120'
        # self.on_board_computer_ip = '192.168.1.2'
        self.on_board_computer_ip = '169.254.179.9'
        # self.on_board_computer_ip = '127.0.0.1'

        self.obc_user = 'sailr'
        self.on_board_computer_path = self.obc_user+'@' + self.on_board_computer_ip + ':~/SeniorProjects/automation/'
        self.commandStringStem = "sshpass -p '" + self.system_password+"' rsync -ave ssh "

        #Open files and clear contents
        self.outTxt = open("commands.txt",'w')
        self.outTxt.truncate(0)
        self.outTxt.close()

        #Initialize command counter
        self.commandNum = 0

        #Import font
        #fontid = QFontDatabase.addApplicationFont("PTF55F.ttf")
        #ptSer = QFontDatabase.applicationFontFamilies(fontid)

        self.setStyleSheet("QLabel, QLineEdit, QPushButton {font: PT Serif};")

        # Start video feed
        self.videoFeed = videoFeed()
        self.videoFeed.start()

        # Start video player
        self.mediaPlayer = QMediaPlayer()

        # Initialize widgets --------------------------

        # Video feed widget (live feed)

        # uncomment
        self.vidFeed = QLabel()


        #self.vidFeed.setFixedHeight(360)
        #self.vidFeed.setFixedWidth(460)

        #uncomment 
        self.videoFeed.imageUpdate.connect(self.imUpdate)

        # Video player widget (file playback)
        # self.vidPlayer = QVideoWidget()
        # self.mediaPlayer.setVideoOutput(self.vidPlayer)
        cwd = os.getcwd()
        # self.vidFileWatch = QFileSystemWatcher([cwd])
        # self.vidNumber = 1
        # self.vidFileWatch.directoryChanged.connect(self.playVid)
        # self.mediaPlayer.mediaStatusChanged.connect(self.playVid)

        self.imDisp = QLabel()
        self.imNum = 1
        #pixmap = QPixmap('SAILR logo.jpg')
        # pixmap = QPixmap("SAILR logo extended.jpg")
        pixmap = QPixmap("SAILR-Logo-extended.jpg")
        self.imDisp.setPixmap(pixmap)
        self.scrollAreaImage = QScrollArea()
        #self.scrollAreaImage.setWidgetResizable(True)
        self.scrollAreaImage.setFixedHeight(380)
        self.scrollAreaImage.setWidget(self.imDisp)
        self.imFileWatch = QFileSystemWatcher([cwd+"images"])
        self.imFileWatch.directoryChanged.connect(self.newIm)

        self.priorCommands = QLabel()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.priorCommands)

        self.togControl = QPushButton("Toggle manual control")
        self.controlMode = "manual"
        self.togControl.clicked.connect(self.toggleMode)

        self.controlIndicator = QLabel("Control Mode: Manual")

        self.degN = QLineEdit()
        self.degN.setPlaceholderText("Degrees north")
        self.degN.returnPressed.connect(self.LOI)

        self.degE = QLineEdit()
        self.degE.setPlaceholderText("Degrees east")
        self.degE.returnPressed.connect(self.LOI)

        self.forwardW = QLineEdit()
        self.forwardW.setPlaceholderText("Forward [m]")
        self.forwardW.returnPressed.connect(self.moveForward)

        self.backwardW = QLineEdit()
        self.backwardW.setPlaceholderText("Backward [m]")
        self.backwardW.returnPressed.connect(self.moveBackward)

        self.leftW = QLineEdit()
        self.leftW.setPlaceholderText("Turn Left [deg]")
        self.leftW.returnPressed.connect(self.turnLeft)

        self.rightW = QLineEdit()
        self.rightW.setPlaceholderText("Turn Right [deg]")
        self.rightW.returnPressed.connect(self.turnRight)

        self.stopButton = QPushButton("STOP")
        self.isStop = 0
        self.stopButton.clicked.connect(self.toggleStop)
        self.stopButton.setStyleSheet("background-color : red")

        self.recordingButton = QPushButton("START RECORDING")
        self.isRecording = False
        self.recordingButton.clicked.connect(self.toggleRecording)
        self.recordingButton.setStyleSheet("background-color : yellow")

        # implement file watching
        thread  = threading.Thread(target = self.changePosition).start()

        self.curPosition = QLabel("Current Position:")
        # self.fileWatch = QFileSystemWatcher()
        # self.fileWatch.addPath("telemetry.txt")
        # self.fileWatch.fileChanged.connect(self.changePosition)
        # add file manager and signal

        self.pingButton = QPushButton("PING")
        self.pingButton.clicked.connect(self.pingFunc)

        # self.startFeedButton = QPushButton("Start vid")
        # self.vidFeedOn = 0
        # self.startFeedButton.clicked.connect(self.startFeed)

        self.console = QLabel(" ")

        # Set layout
        self.layout = QGridLayout()

        # For live video stream
        #self.layout.addWidget(self.vidFeed, 0, 0, 3, 2)

        # For video file player
        self.layout.addWidget(self.vidFeed, 0, 0, 2, 4)

        self.layout.addWidget(self.scrollAreaImage, 2, 0, 1, 4)

        self.layout.addWidget(self.scrollArea, 0 , 4, 3, 1)

        self.layout.addWidget(QLabel("Location of Interest:"), 3, 0)

        self.layout.addWidget(self.degN, 3, 1)

        self.layout.addWidget(self.degE, 3, 2)

        self.layout.addWidget(self.togControl, 3, 3)

        self.layout.addWidget(self.controlIndicator, 3, 4)

        self.layout.addWidget(QLabel("Manual control:"), 4, 0)

        self.layout.addWidget(self.forwardW, 4, 1)

        self.layout.addWidget(self.backwardW, 4, 2)

        self.layout.addWidget(self.leftW, 4, 3)

        self.layout.addWidget(self.rightW, 4, 4)

        self.layout.addWidget(self.stopButton, 5, 0, 1, 3)

        self.layout.addWidget(self.curPosition, 5, 3, 1, 2)

        self.layout.addWidget(self.pingButton, 6, 0, 1, 3)

        self.layout.addWidget(self.recordingButton, 6, 3, 1, 2)

        # self.layout.addWidget(self.startFeedButton, 6, 3, 1, 2)

        self.layout.addWidget(self.console, 7, 0, 1, 5)

        self.setLayout(self.layout)

    def callSync(self, fileName):
        print(self.commandStringStem + self.ground_station_path + fileName + " " + self.on_board_computer_path + fileName)
        os.system(self.commandStringStem + self.ground_station_path + fileName + " " + self.on_board_computer_path + fileName)

    def playVid(self):
        # Function to play video when file is added to system or last video stops playing
        if os.path.isfile("video"+str(self.vidNumber)+".mp4"):
            if (self.mediaPlayer.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia) or (self.mediaPlayer.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia):
                self.mediaPlayer.setSource(QUrl.fromLocalFile("video"+str(self.vidNumber)+".mp4"))
                self.mediaPlayer.play()
                self.vidNumber += 1

    def newIm(self):
        # if os.path.isfile("image"+str(self.imNum)+".jpg"):
        #     pixmap = QPixmap("image" + str(self.imNum) + ".jpg")
        #     self.imDisp.setPixmap(pixmap)
        #     self.imNum += 1
        if os.path.isfile("pano.jpg"):
            pixmap = QPixmap("pano.jpg")
            self.imDisp.setPixmap(pixmap)

    def imUpdate(self, image):
        # Set pixelmap of vidFeed widget to display image
        self.vidFeed.setPixmap(QPixmap.fromImage(image))

    def toggleMode(self):

        self.commandNum += 1

        if self.controlMode == "manual":
            self.console.setText("CONTROL MODE SET TO AUTONOMOUS")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nControl mode set to autonomous")

            self.controlIndicator.setText("Control Mode: Autonomous")
            self.controlMode = "autonomous"

            # t = time.localtime()
            # current_time = time.strftime("%H:%M:%S", t)

            # outString = str(self.commandNum) + ", autonomous, " + current_time + "\n"

            # self.outTxt = open("out.txt",'a')
            # self.outTxt.write(outString)
            # self.outTxt.close()
            
            # self.callSync("out.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)


        elif self.controlMode == "autonomous":
            self.console.setText("CONTROL MODE SET TO MANUAL")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nControl mode set to manual")

            self.controlIndicator.setText("Control Mode: Manual")
            self.controlMode = "manual"

            # t = time.localtime()
            # current_time = time.strftime("%H:%M:%S", t)

            # outString = str(self.commandNum) + ", manual, " + current_time + "\n"

            # self.outTxt = open("out.txt",'a')
            # self.outTxt.write(outString)
            # self.outTxt.close()

            # self.callSync("out.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)



    def LOI(self):

        if self.degE.text().lstrip('-').replace('.','',1).isnumeric() and self.degN.text().lstrip('-').replace('.','',1).isnumeric():
            degENum = float(self.degE.text())
            degNNum = float(self.degN.text())

            if degENum < -180 or degENum > 180 or degNNum < -90 or degNNum > 90:
                #console.setText(u"LOI IGNORED: -90 " + u'≤' " Degrees North " + u'≤' + " , -180 " + u'≤' + " Degrees East "  + u'≤' )
                self.console.setText(u"LOI IGNORED: -90 ≤ Degrees North ≤ , -180 ≤ Degrees East ≤ 180")
            else:
                if self.controlMode == "autonomous":
                    self.commandNum += 1
                
                    self.console.setText("LOI ACCEPTED: " + self.degN.text() + " Degrees North, " + self.degE.text() + " Degrees East")
                    priorText = self.priorCommands.text()
                    self.priorCommands.setText(priorText + "\nLOI: " + self.degN.text() + u'\N{DEGREE SIGN}N ' + self.degE.text() + u'\N{DEGREE SIGN}E')

                    t = time.localtime()
                    current_time = time.strftime("%H:%M:%S", t)

                    # Write output to file
                    outString = str(self.commandNum) + ", " + self.controlMode + ", LOI, " + self.degN.text() + ", " + self.degE.text() + ", " + current_time + "\n"

                    self.outTxt = open("commands.txt",'a')
                    self.outTxt.write(outString)
                    self.outTxt.close()

                    self.callSync("commands.txt")

                    # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)
                elif self.controlMode == "manual":
                    self.console.setText("LOI IGNORED: Set control mode to autonomous")

        else:
            self.console.setText("LOI IGNORED: Invalid input given for either Degrees North, Degrees East or both")

        self.degE.clear()
        self.degN.clear()

    def moveForward(self):

        if self.forwardW.text().replace('.','',1).isnumeric() and self.controlMode == "manual":
            self.commandNum += 1            

            self.console.setText("MANUAL CONTROL ACCEPTED: Forward " + self.forwardW.text() + " meters")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nForward: " + self.forwardW.text() + " m")

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", manual, translate, " + self.forwardW.text() + ", " + current_time + "\n"

            self.outTxt = open("commands.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            
            self.callSync("commands.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)


        else:
            if self.controlMode != "manual":
                self.console.setText("MANUAL CONTROL IGNORED: Control mode set to autonomous")
            elif self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.forwardW.clear()

    def moveBackward(self):

        if self.backwardW.text().replace('.','',1).isnumeric() and self.controlMode == "manual":
            self.commandNum += 1

            self.console.setText("MANUAL CONTROL ACCEPTED: Backward " + self.backwardW.text() + " meters")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nBackward: " + self.backwardW.text() + " m")

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", manual, translate, -" + self.backwardW.text() + ", " + current_time + "\n"

            self.outTxt = open("commands.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            
            self.callSync("commands.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)

        else:
            if self.controlMode != "manual":
                self.console.setText("MANUAL CONTROL IGNORED: Control mode set to autonomous")
            elif self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.backwardW.clear()

    def turnLeft(self):

        if self.leftW.text().replace('.','',1).isnumeric and self.controlMode == "manual":
            self.commandNum += 1

            self.console.setText("MANUAL CONTROL ACCEPTED: Turn " + self.leftW.text() + " degrees left")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nLeft: " + self.leftW.text() + u'\N{DEGREE SIGN}')

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", manual, rotate, -" + self.leftW.text() + ", " + current_time + "\n"

            self.outTxt = open("commands.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            
            self.callSync("commands.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)


        else:
            if self.controlMode != "manual":
                self.console.setText("MANUAL CONTROL IGNORED: Control mode set to autonomous")
            elif self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.leftW.clear()

    def turnRight(self):

        if self.rightW.text().replace('.','',1).isnumeric() and self.controlMode == "manual":
            self.commandNum += 1

            self.console.setText("MANUAL CONTROL ACCEPTED: Turn " + self.rightW.text() + " degrees right")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nRight: " + self.rightW.text() + u'\N{DEGREE SIGN}')

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", manual, rotate, " + self.rightW.text() + ", " + current_time + "\n"

            self.outTxt = open("commands.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            
            self.callSync("commands.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)

        else:
            if self.controlMode != "manual":
                self.console.setText("MANUAL CONTROL IGNORED: Control mode set to autonomous")
            elif self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.rightW.clear()

    def toggleStop(self):

        self.commandNum += 1
        
        if self.isStop == 0:
            self.console.setText("EMERGENCY STOP INITIATED")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nEmergency stop initiated")

            self.stopButton.setText("START")
            self.isStop = 1

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", stop, " + current_time + "\n"

            self.outTxt = open("commands.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()

            self.callSync("commands.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)

        elif self.isStop == 1:
            self.console.setText("EMERGENCY STOP CANCELED")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nEmergency stop canceled")

            self.stopButton.setText("STOP")
            self.isStop = 0

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", start, " + current_time + "\n"

            self.outTxt = open("commands.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()

            self.callSync("commands.txt")

            # subprocess.run(["powershell","-Command",self.commandString], capture_output=True)
    

    def toggleRecording(self):
            
            if self.isRecording:
                self.console.setText("Stopped Recording")
                # priorText = self.priorCommands.text()
                # self.priorCommands.setText(priorText + "\nEmergency stop initiated")

                self.recordingButton.setText("START RECORDING")
                self.isRecording = False
                self.videoFeed.record_toggle()

            elif not self.isRecording:
                self.console.setText("Started Recording")
                # priorText = self.priorCommands.text()
                # self.priorCommands.setText(priorText + "\nEmergency stop canceled")

                self.recordingButton.setText("STOP RECORDING")
                self.isRecording = True
                self.videoFeed.record_toggle()


    def changePosition(self):
        while True:
            locationTxt = open("telemetry.txt",'r')
            roverLoc = locationTxt.read().splitlines()[-1].split(', ')
            roverCoords = roverLoc[0].split(',')
            self.curPosition.setText("Current Position: " + roverLoc[0] + " Time: " + roverLoc[1])
            locationTxt.close()
            time.sleep(1)
        

    def pingFunc(self):
        if 0 == os.system('ping '+self.on_board_computer_ip+' -c 1 -W 1'):
            self.console.setText("Connected to OBC")
            return 1
        else:
            self.console.setText("NOT Connected to OBC")
            return 0

    def startFeed(self):
        if self.vidFeedOn == 0:
            self.videoFeed = videoFeed(self.on_board_computer_ip)
            self.videoFeed.run()
            self.videoFeed.imageUpdate.connect(self.imUpdate)
            self.console.setText("Video feed started")
            self.startFeedButton.setText("Stop vid")
            self.vidFeedOn = 1
        elif self.vidFeedOn == 1:
            self.videoFeed.stop()
            self.console.setText("Video feed stopped")
            self.startFeedButton.setText("Start vid")
            self.vidFeedOn = 0


class videoFeed(QThread):
    # Using code from https://www.codepile.net/pile/ey9KAnxn and https://www.youtube.com/watch?v=dTDgbx-XelY
    
    # Create signal for when image in video feed should be updated
    imageUpdate = pyqtSignal(QImage)

    # Create a socket object
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host = '127.0.2.1'  # replace with the server IP address
    host = '169.254.179.9'
    port = 9999
    # socket_address = (host_ip, port)
    connected = False
    # frame_width = struct.unpack("I", client_socket.recv(4))[0]
    # frame_height = struct.unpack("I", client_socket.recv(4))[0]

    # Video recording setup
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    recording = False
    out = None
    filename = None
    frame = None

    # Method to start video feed
    def run(self):

        # Connect to the server
        self.connect()

        # Boolean for if video active
        self.videoActive = True

        # Initialize video capture of default device

        #vidCap = cv2.VideoCapture(0)
        while self.videoActive:
            
            # isFrame bool for presence of frame, frame contains current frame
            # isFrame , frame = vidCap.read()
            # if isFrame:
            #     # convert frame color space from BGR to RGB
            #     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            #     # Horizontally flip image
            #     flippedIm = cv2.flip(image,1)

            #     # Convert image to PyQt format
            #     qtImage = QImage(flippedIm.data, flippedIm.shape[1], flippedIm.shape[0], QImage.Format.Format_RGB888)

            #     # Scale qtImage to desired size
            #     # pic = qtImage.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

            #     # send signal with image (pic/qtImage)
            #     self.imageUpdate.emit(qtImage)

                    # Receive the frame size from the server
            try:
                data_size = struct.unpack("I", self.socket.recv(4))[0]
            except:
                # if not self.check_connection():
                self.connected = False
                print(f"Error receiving live video, retrying in 3 seconds...")
                self.socket.close()
                self.connect()
                continue

            # Receive the frame from the server
            data = b""
            while len(data) < data_size:
                packet = self.socket.recv(data_size - len(data))
                if not packet:
                    break
                data += packet

            # Convert the byte string to a frame
            self.frame = pickle.loads(data)

            image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            # Record video frame
            if self.recording:
                self.out.write(self.frame)

            # Horizontally flip image
            flippedIm = cv2.flip(image,1)

            # Convert image to PyQt format
            qtImage = QImage(flippedIm.data, flippedIm.shape[1], flippedIm.shape[0], QImage.Format.Format_RGB888)

            self.imageUpdate.emit(qtImage)


        # TODO maintain connections

    def connect(self):

        while not self.connected:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.connect((self.host, self.port))
                self.connected = True
                print(f"Connected to {self.host}:{self.port}")
            except:
                print(
                    f"Error connecting to {self.host}:{self.port}, retrying in 3 seconds...")
                time.sleep(3)

    def check_connection(self,):
        try:
            self.socket.getpeername()
            print(self.socket.getpeername())
            self.connected = True
            return True
        except:
            self.connected = False
            return False

    # Method to stop video feed                
    def stop(self):
        if self.out is not None:
            out.release()
        self.socket.close()
        self.videoActive = False
        self.quit()

    def record_toggle(self):
        if not self.recording:
            self.recording = True
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.filename = f"record_{timestamp}.mp4"
            self.out = cv2.VideoWriter(self.filename, self.fourcc, 20.0, (self.frame.shape[1], self.frame.shape[0]))
            print(f"Recording started. Saving to {self.filename}")
        elif self.recording:
            self.recording = False
            self.out.release()
            print(f"Recording stopped. Saved to {self.filename}")
            self.filename = None


app = QApplication(sys.argv)
root = mainWindow()
root.setWindowTitle("Ground Station")
root.showMaximized()
sys.exit(app.exec())