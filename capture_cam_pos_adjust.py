import cv2, time, threading, numpy as np
from PyQt5.QtCore import pyqtSignal, QThread

class VideoThread(QThread):         # Inherit from QThread
    change_pixmap_signal = pyqtSignal(np.ndarray)       # Initialize the frame from OPENCV

    def __init__(self):
        super().__init__()          # Inherit from QThread.__init__
        self.a = 0
        self.cam_flag = False       # Need for webcam thread (OPENCV)
        self.count_flag = True      # Need for other threads (i.e. printout)
        self.name = ''
        pass

    def run(self):                  # Always named "run" -> Cannot change
        video = cv2.VideoCapture(0)
        self.cam_flag = True        # Set flags ON
        self.count_flag = True
        while True:
            check, self.frame = video.read()        # check <=> ret -> if ret: ...
            ###
            # cv2.circle(self.frame, (320, 240), 2, (0, 255, 255), 2)
            # cv2.line(self.frame, (160, 120), (160, 400), (0, 255, 0), 2)
            # cv2.line(self.frame, (160, 120), (500, 120), (0, 255, 0), 2)
            # cv2.rectangle(self.frame, (0,100), (639,380), (0, 255, 0), 2)       ########## Ok in LAB YASKAWA
            # cv2.rectangle(self.frame, (0,130), (639,350), (0, 255, 255), 2)     ##### at home conveyor
            ###
            # cv2.imshow("Capturing",frame)
            # key = cv2.waitKey(1)
            # if key == ord('q'):
            #     break
            # if key == 13:       # Enter Key Press
            #     showPic = cv2.imwrite("test_imgs/obj_{}.jpg".format(self.a),frame)
            #     # cv2.imwrite("obj_{}.jpg".format(self.a),frame)
            #     self.a = self.a + 1
            ###
            if not self.cam_flag:           # Wait for press STOP -> cam_flag OFF
                self.count_flag = False     # Also set other threads flags OFF
                break
            self.change_pixmap_signal.emit(self.frame)      # TRANSMIT the frames from OPENCV

    def printout(self):
        while True:
            print(self.a, self.name)
            time.sleep(1)
            self.a += 1
            if not self.count_flag:         # WAIT FOR WEBCAM OFF -> OTHER THREADS OFF TOO  !
                break

    def capture(self):
        if self.count_flag:                 # JUST PRESS CAPTURE BUTTON WHEN WEBCAM IS ON !
            cv2.imwrite("{}.jpg".format(self.name),self.frame)
        pass


# c = trial()
# t1 = threading.Thread(target=c.webcam)
# t2 = threading.Thread(target=c.printout)
# t1.start()
# t2.start()
# t1.join()
# t2.join()
