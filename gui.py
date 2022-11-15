import sys

from PyQt6.QtCore import *

from PyQt6.QtWidgets import *

from PyQt6.QtGui import *

import cv2

class mainWindow(QWidget):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.videoFeed = videoFeed()
        self.videoFeed.start()

        # Initialize widgets
        self.vidFeed = QLabel()
        self.videoFeed.imageUpdate.connect(self.imUpdate)

        self.imDisp = QLabel()
        pixmap = QPixmap('SAILR logo.jpg')
        self.imDisp.setPixmap(pixmap)


        self.priorCommands = QLabel()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.priorCommands)

        self.togControl = QPushButton("Toggle manual control")
        self.isManual = 1
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

        self.console = QLabel(" ")

        # Set layout
        self.layout = QGridLayout()

        self.layout.addWidget(self.vidFeed, 0, 0, 3, 2)

        self.layout.addWidget(self.imDisp, 0, 2, 3, 2)

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

        self.layout.addWidget(self.console, 5, 0, 1, 5)

        self.setLayout(self.layout)

        
    def imUpdate(self, image):
        # Set pixelmap of vidFeed widget to display image
        self.vidFeed.setPixmap(QPixmap.fromImage(image))

    def toggleMode(self):
        self.isManual

        if self.isManual == 1:
            self.controlIndicator.setText("Control Mode: Automated")
            self.isManual = 0
        else:
            self.controlIndicator.setText("Control Mode: Manual")
            self.isManual = 1

    def LOI(self):
        if self.degE.text().isnumeric() and self.degN.text().isnumeric:
            degENum = float(self.degE.text())
            degNNum = float(self.degN.text())

            if degENum < -180 or degENum > 180 or degNNum < -90 or degNNum > 90:
                #console.setText(u"LOI IGNORED: -90 " + u'≤' " Degrees North " + u'≤' + " , -180 " + u'≤' + " Degrees East "  + u'≤' )
                self.console.setText(u"LOI IGNORED: -90 ≤ Degrees North ≤ , -180 ≤ Degrees East ≤ 180")
            else:
                self.console.setText("LOI ACCEPTED: " + self.degN.text() + " Degrees North, " + self.degE.text() + " Degrees East")
                priorText = self.priorCommands.text()
                self.priorCommands.setText(priorText + "\nLOI: " + self.degN.text() + u' \N{DEGREE SIGN}N ' + self.degE.text() + u' \N{DEGREE SIGN}E')
                outString = self.degN.text() + "," + self.degE.text()
                ## save to file/output
        else:
            self.console.setText("LOI IGNORED: Invalid input given for either Degrees North, Degrees East or both")

        self.degE.clear()
        self.degN.clear()

    def moveForward(self):
        if self.forwardW.text().isnumeric:
            self.console.setText("MANUAL CONTROL ACCEPTED: Forward " + self.forwardW.text() + " meters")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nForward: " + self.forwardW.text() + " m")
            
        else:
            if self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.forwardW.clear()

    def moveBackward(self):
        if self.backwardW.text().isnumeric():
            self.console.setText("MANUAL CONTROL ACCEPTED: Backward " + self.backwardW.text() + " meters")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nBackward: " + self.backwardW.text() + " m")
        else:
            if self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.backwardW.clear()

    def turnLeft(self):
        if self.leftW.text().isnumeric:
            self.console.setText("MANUAL CONTROL ACCEPTED: Turn " + self.leftW.text() + " degrees left")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nLeft: " + self.leftW.text() + u' \N{DEGREE SIGN}')
        else:
            if self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.leftW.clear()

    def turnRight(self):
        if self.rightW.text().isnumeric():
            self.console.setText("MANUAL CONTROL ACCEPTED: Turn " + self.rightW.text() + " degrees right")
            priorText = self.priorCommands.text()
            self.priorCommands.setText(priorText + "\nRight: " + self.rightW.text() + u' \N{DEGREE SIGN}')
        else:
            if self.forwardW.text() != "":
                self.console.setText("MANUAL CONTROL IGNORED: Input not numeric")
        
        self.rightW.clear()
    

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
root.show()
sys.exit(app.exec())