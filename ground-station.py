import gui 


app = QApplication(sys.argv)
root = mainWindow()
root.setWindowTitle("Ground Station")
root.showMaximized()
sys.exit(app.exec())