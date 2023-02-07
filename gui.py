import sys

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

from PyQt6.QtGui import *

from PyQt6.QtMultimedia import *

from PyQt6.QtMultimediaWidgets import *

import cv2

import time

import os

class mainWindow(QWidget):
    def __init__(self):
        super(mainWindow, self).__init__()

        # R-sync info
        self.system_password = 'asen4018'
        self.sender_path = '/root/comms-gs/out.txt'
        self.receiver_ip = '192.168.56.102'
        self.receiver_path = self.receiver_ip +':/root/comms-gs/out.txt'

        #Open files and clear contents
        self.outTxt = open("out.txt",'w')
        self.outTxt.truncate(0)
        self.outTxt.close()

        #Initialize command counter
        self.commandNum = 0

        #Import font
        fontid = QFontDatabase.addApplicationFont("PTF55F.ttf")
        #ptSer = QFontDatabase.applicationFontFamilies(fontid)

        self.setStyleSheet("QLabel, QLineEdit, QPushButton {font: PT Serif};")

        # Start video feed
        self.videoFeed = videoFeed()
        self.videoFeed.start()

        # Start video player
        self.videoPlayer = QMediaPlayer()

        # Initialize widgets --------------------------

        # Video feed widget (live feed)
        self.vidFeed = QLabel()
        self.videoFeed.imageUpdate.connect(self.imUpdate)

        # Video player widget (file playback)
        self.vidPlayer = QVideoWidget()
        self.videoPlayer.setVideoOutput(self.vidPlayer)
        cwd = os.getcwd()
        self.vidFileWatch = QFileSystemWatcher([cwd])
        self.vidNumber = 1
        self.vidFileWatch.directoryChanged.connect(self.playVid)
        self.videoPlayer.mediaStatusChanged.connect(self.playVid)

        self.imDisp = QLabel()
        #pixmap = QPixmap('SAILR logo.jpg')
        pixmap = QPixmap('SAILR logo extended.jpg')
        self.imDisp.setPixmap(pixmap)
        self.scrollAreaImage = QScrollArea()
        #self.scrollAreaImage.setWidgetResizable(True)
        self.scrollAreaImage.setFixedHeight(380)
        self.scrollAreaImage.setWidget(self.imDisp)

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

        self.curPosition = QLabel("Current Position:")
        self.fileWatch = QFileSystemWatcher()
        self.fileWatch.addPath("roverLocation.txt")
        self.fileWatch.fileChanged.connect(self.changePosition)
        # add file manager and signal

        self.console = QLabel(" ")

        # Set layout
        self.layout = QGridLayout()

        # For live video stream
        #self.layout.addWidget(self.vidFeed, 0, 0, 3, 2)

        # For video file player
        self.layout.addWidget(self.vidPlayer, 0, 0, 2, 4)

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

        self.layout.addWidget(self.console, 6, 0, 1, 5)

        self.setLayout(self.layout)

    def playVid(self):
        # Function to play video when file is added to system or last video stops playing
        if os.path.isfile("video"+str(self.vidNumber)+".mp4"):
            if (self.videoPlayer.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia) or (self.videoPlayer.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia):
                self.videoPlayer.setSource(QUrl.fromLocalFile("video"+str(self.vidNumber)+".mp4"))
                self.videoPlayer.play()
                self.vidNumber += 1

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

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            outString = str(self.commandNum) + ", mode, autonomous, " + current_time + "\n"

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)


        elif self.controlMode == "autonomous":
            self.console.setText("CONTROL MODE SET TO MANUAL")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nControl mode set to manual")

            self.controlIndicator.setText("Control Mode: Manual")
            self.controlMode = "manual"

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            outString = str(self.commandNum) + ", mode, manual, " + current_time + "\n"

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)



    def LOI(self):

        if self.degE.text().lstrip('-').replace('.','',1).isnumeric() and self.degN.text().lstrip('-').replace('.','',1).isnumeric():
            degENum = float(self.degE.text())
            degNNum = float(self.degN.text())

            if degENum < -180 or degENum > 180 or degNNum < -90 or degNNum > 90:
                #console.setText(u"LOI IGNORED: -90 " + u'≤' " Degrees North " + u'≤' + " , -180 " + u'≤' + " Degrees East "  + u'≤' )
                self.console.setText(u"LOI IGNORED: -90 ≤ Degrees North ≤ , -180 ≤ Degrees East ≤ 180")
            else:
                self.commandNum += 1
            
                self.console.setText("LOI ACCEPTED: " + self.degN.text() + " Degrees North, " + self.degE.text() + " Degrees East")
                priorText = self.priorCommands.text()
                self.priorCommands.setText(priorText + "\nLOI: " + self.degN.text() + u'\N{DEGREE SIGN}N ' + self.degE.text() + u'\N{DEGREE SIGN}E')

                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)

                # Write output to file
                outString = str(self.commandNum) + ", mode, " + self.controlMode + ", LOI, " + self.degN.text() + ", " + self.degE.text() + ", " + current_time + "\n"

                self.outTxt = open("out.txt",'a')
                self.outTxt.write(outString)
                self.outTxt.close()
                #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)

        else:
            self.console.setText("LOI IGNORED: Invalid input given for either Degrees North, Degrees East or both")

        self.degE.clear()
        self.degN.clear()

    def moveForward(self):

        if self.forwardW.text().isnumeric() and self.controlMode == "manual":
            self.commandNum += 1            

            self.console.setText("MANUAL CONTROL ACCEPTED: Forward " + self.forwardW.text() + " meters")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nForward: " + self.forwardW.text() + " m")

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", mode, manual, translate, " + self.forwardW.text() + ", " + current_time + "\n"

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)


        else:
            if self.controlMode != "manual":
                self.console.setText("MANUAL CONTROL IGNORED: Control mode set to autonomous")
            elif self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.forwardW.clear()

    def moveBackward(self):

        if self.backwardW.text().isnumeric() and self.controlMode == "manual":
            self.commandNum += 1

            self.console.setText("MANUAL CONTROL ACCEPTED: Backward " + self.backwardW.text() + " meters")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nBackward: " + self.backwardW.text() + " m")

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", mode, manual, translate, -" + self.backwardW.text() + ", " + current_time + "\n"

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)

        else:
            if self.controlMode != "manual":
                self.console.setText("MANUAL CONTROL IGNORED: Control mode set to autonomous")
            elif self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.backwardW.clear()

    def turnLeft(self):

        if self.leftW.text().isnumeric and self.controlMode == "manual":
            self.commandNum += 1

            self.console.setText("MANUAL CONTROL ACCEPTED: Turn " + self.leftW.text() + " degrees left")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nLeft: " + self.leftW.text() + u'\N{DEGREE SIGN}')

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", mode, manual, rotate, -" + self.leftW.text() + ", " + current_time + "\n"

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)


        else:
            if self.controlMode != "manual":
                self.console.setText("MANUAL CONTROL IGNORED: Control mode set to autonomous")
            elif self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.leftW.clear()

    def turnRight(self):

        if self.rightW.text().isnumeric() and self.controlMode == "manual":
            self.commandNum += 1

            self.console.setText("MANUAL CONTROL ACCEPTED: Turn " + self.rightW.text() + " degrees right")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nRight: " + self.rightW.text() + u'\N{DEGREE SIGN}')

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            # Write output to file
            outString = str(self.commandNum) + ", mode, manual, rotate, " + self.rightW.text() + ", " + current_time + "\n"

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)

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

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
            #os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)

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

            self.outTxt = open("out.txt",'a')
            self.outTxt.write(outString)
            self.outTxt.close()
    
    def changePosition(self):
        locationTxt = open("roverLocation.txt",'r')
        roverLoc = locationTxt.read().split(',')
        if len(roverLoc) == 2:
            self.curPosition.setText("Current Position: " + roverLoc[0] + "\N{DEGREE SIGN}N, " + roverLoc[1] + "\N{DEGREE SIGN}E")

class videoFeed(QThread):
    # Using code from https://www.codepile.net/pile/ey9KAnxn and https://www.youtube.com/watch?v=dTDgbx-XelY
    
    # Create signal for when image in video feed should be updated
    imageUpdate = pyqtSignal(QImage)

    # Method to start video feed
    def run(self):
        
        # Boolean for if video active
        self.videoActive = True

        # Initialize video capture of default device
        
        vidCap = cv2.VideoCapture(0)
        while self.videoActive:
            # isFrame bool for presence of frame, frame contains current frame
            isFrame , frame = vidCap.read()
            if isFrame:
                # convert frame color space from BGR to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Horizontally flip image
                flippedIm = cv2.flip(image,1)

                # Convert image to PyQt format
                qtImage = QImage(flippedIm.data, flippedIm.shape[1], flippedIm.shape[0], QImage.Format.Format_RGB888)

                # Scale qtImage to desired size
                # pic = qtImage.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

                # send signal with image (pic/qtImage)
                self.imageUpdate.emit(qtImage)

    # Method to stop video feed                
    def stop(self):
        self.videoActive = False
        self.quit()

app = QApplication(sys.argv)
root = mainWindow()
root.setWindowTitle("Ground Station")
root.showMaximized()
sys.exit(app.exec())