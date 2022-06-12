### https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1 
### https://realpython.com/python-pyqt-layout/
from capture_cam_pos_adjust import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLineEdit, QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush
import sys
from PyQt5.QtCore import pyqtSlot, Qt, QSize
import numpy as np


# class VideoThread(QThread):
#     change_pixmap_signal = pyqtSignal(np.ndarray)

#     def run(self):
#         cap = cv2.VideoCapture(0)
#         while True:
#             ret, cv_img = cap.read()
#             if ret:
#                 self.change_pixmap_signal.emit(cv_img)


class App(QWidget):             # Inherit from QWidget
    def __init__(self):
        super().__init__()      # Inherit from QWidget.__init__
        self.isStarted = False
        self.img_name = ""

        self.setWindowTitle("Capturing...")
        self.disply_width = 640
        self.display_height = 480
        self.image_label = QLabel(self)     # create the label that holds the image
        self.image_label.resize(self.disply_width, self.display_height)
        self.update_image(np.zeros([480,640,3],dtype=np.uint8)) # Set a background for Video (black)
        self.textLabel = QLabel('Webcam')               # create a text label
        self.pushButton = QPushButton('Capture')
        self.stopButton = QPushButton('Stop Cam')
        self.startButton = QPushButton('Start Cam')
        self.setName = QLineEdit()
        self.updateName = QPushButton("SetName")
        
        self.logolabel = QLabel()
        # self.logolabel.setScaledContents(True)
        self.logolabel.setPixmap(QPixmap('logo_BK.png').scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
        
        self.titlelabel = QLabel('THESIS\n---DYNAMIC OBJECT CLASSIFICATION ON YASKAWA MANIPULATOR---')
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        font.setBold(True)
        self.titlelabel.setFont(font)
        self.titlelabel.setStyleSheet('color: red')
        
        vbox = QVBoxLayout()        # create a vertical box layout and add the two labels
        self.setLayout(vbox)        # set the vbox layout as the widgets layout
        hbox1 = QHBoxLayout()
        vbox.addLayout(hbox1)       # Add hbox1 into vbox !!!
        vbox.addWidget(self.image_label)
        hbox2 = QHBoxLayout()
        vbox.addLayout(hbox2)       # Add hbox2 into vbox !!!

        hbox1.addWidget(self.logolabel)
        hbox1.addWidget(self.titlelabel)
        # self.setLayout(hbox1)
        
        hbox2.addWidget(self.textLabel)
        hbox2.addStretch()
        hbox2.addWidget(self.startButton)
        hbox2.addWidget(self.stopButton)
        hbox2.addWidget(self.pushButton)
        hbox2.addWidget(self.setName)
        hbox2.addWidget(self.updateName)

        # self.setLayout(hbox2)

        self.startButton.clicked.connect(self.start_capture)
        self.stopButton.clicked.connect(self.stop_capture)
        self.updateName.clicked.connect(self.set_name_img)

    def start_capture(self):
        if not self.isStarted:
            self.thread1 = VideoThread()            # connect its signal to the update_image slot
            if not self.thread1.cam_flag:
                self.thread1.change_pixmap_signal.connect(self.update_image)
                self.thread1.start()
                self.thread2 = threading.Thread(target=self.thread1.printout)#,args=(self.img_name,))
                self.thread2.setDaemon(True)        # When Thread1 ends, Thread2 also ends
                self.thread2.start()
                self.pushButton.clicked.connect(self.thread1.capture)
                self.isStarted = True

    def stop_capture(self):
        if self.thread1.cam_flag and self.isStarted:
            self.thread1.change_pixmap_signal.disconnect(self.update_image)
            self.update_image(np.zeros([480,640,3],dtype=np.uint8)) # Set black background again
            # print(self.thread1.isRunning())
            self.thread1.quit()
            self.thread1.wait(1000)
            # print(self.thread1.isRunning())
            self.thread1.cam_flag = False
            self.isStarted = False

    def set_name_img(self):
        self.thread1.name = self.setName.text()
        # print(self.img_name)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):     # Updates the image_label with a new opencv image
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):    # Convert from an opencv image to QPixmap
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    oImage = QImage("bg_gui.jpeg")
    sImage = oImage.scaled(QSize(1280,720))                   # resize Image to widgets size
    qp = QPalette()
    qp.setBrush(QPalette.Window, QBrush(sImage))
    # qp.setColor(QPalette.ButtonText, Qt.black)
    # qp.setColor(QPalette.Window, Qt.gray)
    # qp.setColor(QPalette.Button, Qt.gray)
    app.setPalette(qp)

    a = App()
    a.show()
    sys.exit(app.exec_())
