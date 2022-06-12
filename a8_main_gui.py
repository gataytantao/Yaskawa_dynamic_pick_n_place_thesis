### https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1 
### https://realpython.com/python-pyqt-layout/
### https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
from a6_main_loop import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QGridLayout, 
                            QLineEdit, 
                            QMessageBox, 
                            QTabWidget, 
                            QWidget, 
                            QApplication, 
                            QLabel, 
                            QVBoxLayout, 
                            QHBoxLayout, 
                            QPushButton,
                            QGroupBox,
                            QMessageBox,
                            QComboBox)
from PyQt5.QtGui import (QPixmap, 
                        QImage, 
                        QPalette, 
                        QBrush, 
                        QIntValidator)
import sys, threading
from PyQt5.QtCore import QLine, pyqtSlot, Qt, QSize
from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class App(QWidget):             # Inherit from QWidget
    def __init__(self):
        super().__init__()      # Inherit from QWidget.__init__
        self.thread1 = Main_loop()  # Main Thread is GUI, thread 1 is camera program
        self.filename = ""      # Input img filename
        self.setWindowTitle("Capturing...")
        self.disply_width = 640
        self.display_height = 480
        self.setFont(QtGui.QFont("Arial", 12))
        self.image_label = QLabel(self)     # create the label that holds the image
        self.image_label.resize(self.disply_width, self.display_height)
        self.update_image(np.zeros([480,640,3],dtype=np.uint8)) # Set a background for Video (black)
        self.captureButton = QPushButton('Capture')
        self.stopButton = QPushButton('Stop Cam')
        self.startButton = QPushButton('Start Cam')
        self.input_fileimg = QPushButton("Input Imgfile Name")
        self.txt_fileimg = QLineEdit()  # Input img filename on GUI
        
        logolabel = QLabel()            # Insert Bach Khoa Logo on GUI
        logolabel.setPixmap(QPixmap('logo_BK.png').scaled(100, 
                                                          100, 
                                                          Qt.KeepAspectRatio, 
                                                          Qt.FastTransformation))
        
        titlelabel = QLabel('THESIS\n---DYNAMIC OBJECT CLASSIFICATION ON YASKAWA MANIPULATOR---')
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        font.setBold(True)
        titlelabel.setFont(font)
        titlelabel.setStyleSheet('color: red')

        group1 = QGroupBox("Chosen Object Parameters")
        g1 = QGridLayout()
        group1.setLayout(g1)                ### SetLayout also for group1
        g1.addWidget(QLabel("X (mm) = "),0,0)
        g1.addWidget(QLabel("Y (mm) = "),1,0)
        g1.addWidget(QLabel("Z (mm) = "),2,0)
        g1.addWidget(QLabel("Angle (deg) = "),3,0)
        g1.addWidget(QLabel("V (mm/s) = "),4,0)
        g1.addWidget(QLabel("Shape = "),5,0)
        self.group1_txt = [QLineEdit() for i in range(7)]
        for i in range(6):
            self.group1_txt[i].setReadOnly(True)
            g1.addWidget(self.group1_txt[i], i, 1)
        g1.addWidget(QLabel(""),6,0,1,2)     # This blank label occupies 1 row and 2 columns
        g1.addWidget(QLabel("# of Objects = "),7,0)
        self.group1_txt[6].setReadOnly(True)
        g1.addWidget(self.group1_txt[6],7,1)

        group2 = QGroupBox("RobotArm Parameters")
        g2 = QGridLayout()
        group2.setLayout(g2)                ### SetLayout also for group2
        g2.addWidget(QLabel("Xr (mm) = "),0,0)
        g2.addWidget(QLabel("Yr (mm) = "),1,0)
        g2.addWidget(QLabel("Zr (mm) = "),2,0)
        g2.addWidget(QLabel("Vr (mm/s) = "),3,0)
        self.group2_txt = [QLineEdit() for i in range(4)]   # Four parameters for robot pos and velocity
        for i in range(4): 
            self.group2_txt[i].setReadOnly(True)
            g2.addWidget(self.group2_txt[i], i, 1, 1, 2)    # Expand for 2 columns
        g2.addWidget(QLabel(""),4,0,1,2)
        g2.addWidget(QLabel("Set Vr (mm/s): "),5,0)
        self.vr_set_txt = QLineEdit()
        self.vr_set_txt.setValidator(QIntValidator())   # Just receive the Integer value
        self.vr_set_txt.setMaxLength(4)                 # The max length is 4
        g2.addWidget(self.vr_set_txt,5,1)
        self.vr_set_button = QPushButton("Set Vr")
        g2.addWidget(self.vr_set_button,5,2)

        group3 = QGroupBox("Manual Move:")
        g3 = QGridLayout(group3)
        g3.addWidget(QLabel("Xr_d (mm) = "),0,0)
        g3.addWidget(QLabel("Yr_d (mm) = "),1,0)
        g3.addWidget(QLabel("Zr_d (mm) = "),2,0)
        self.group3_txt = [QLineEdit() for i in range(3)]
        for i in range(3):
            self.group3_txt[i].setValidator(QIntValidator())   # Just receive the Integer value
            self.group3_txt[i].setMaxLength(3)                 # The max length is 3
            g3.addWidget(self.group3_txt[i], i, 1)
        self.go_button = QPushButton("Go")
        g3.addWidget(self.go_button,3,1)
        g2.addWidget(group3, 6, 0, 1, 2)

        self.r_backhome = QPushButton("MOVE HOME")
        g2.addWidget(self.r_backhome,7,0,1,3)
        
        ### ------- Setup GUI (below) ------- ###
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)     ### setLayout just once for self. and once for each tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)     # Add tabs into the main_window
        tab1 = QWidget()
        tab2 = QWidget()

        tabs.addTab(tab1, "Main Window")
        tabs.addTab(tab2, "TOF Distance Check")

        vbox1 = QVBoxLayout()
        tab1.setLayout(vbox1)       # setLayout for tab1 once
        vbox2 = QVBoxLayout()
        tab2.setLayout(vbox2)       # setLayout for tab1 once
        
        dy_canvas = FigureCanvas(Figure(figsize=(10,10),
                            tight_layout = True,
                            dpi = 100))
        self._dynamic_ax = dy_canvas.figure.subplots()  # Immerse the Matplotlib on GUI
        toolbar = NavigationToolbar(dy_canvas, self)    # Add toolbar for Graph
        self.plot_button = QPushButton("Plot")          # Press to load Graph
        self.obj_combobox = QComboBox()                 # Get the csv filelist
        label_h_check = QLabel("Height Check =")
        self.txt_h_check = QLineEdit()                  # Display the height deviation
        n = self.thread1.num_objs                       # Initial for counting csv file
        if n > 0:
            self.obj_combobox.addItems(["{}".format(i) for i in glob.glob("csv_files/*.csv")])
        vbox2.addWidget(toolbar)
        vbox2.addWidget(dy_canvas)
        hbox4 = QHBoxLayout()
        vbox2.addLayout(hbox4)
        hbox4.addWidget(self.plot_button)
        hbox4.addWidget(self.obj_combobox)
        hbox4.addStretch()
        hbox4.addWidget(label_h_check)
        hbox4.addWidget(self.txt_h_check)
        hbox4.addStretch()

        # self.setLayout(vbox1) # self.setLayout <-> setCentralWidget
        hbox1 = QHBoxLayout()
        vbox1.addLayout(hbox1)      # Add hbox1 into vbox1 !!!
        hbox2 = QHBoxLayout()
        vbox1.addLayout(hbox2)      # Add hbox2 into vbox1 !!!
        hbox3 = QHBoxLayout()
        vbox1.addLayout(hbox3)      # Add hbox3 into vbox1 !!!
        
        hbox1.addWidget(logolabel)
        hbox1.addWidget(titlelabel)
        hbox1.addStretch()

        hbox2.addWidget(self.image_label)
        hbox2.addWidget(group1)
        hbox2.addWidget(group2)
        
        hbox3.addWidget(self.startButton)
        hbox3.addWidget(self.stopButton)
        hbox3.addStretch()
        hbox3.addWidget(self.txt_fileimg)
        hbox3.addWidget(self.input_fileimg)
        hbox3.addWidget(self.captureButton)
        hbox3.addStretch()
        
        self.startButton.clicked.connect(self.start_capture)    # Start to connect buttons for execution
        self.stopButton.clicked.connect(self.stop_capture)
        self.input_fileimg.clicked.connect(self.input_filename)
        self.captureButton.clicked.connect(self.capture)
        self.vr_set_button.clicked.connect(self.vr_change)
        self.r_backhome.clicked.connect(self.r_call_backhome)
        self.go_button.clicked.connect(self.r_move_manually)
        self.plot_button.clicked.connect(self.tof_plot)

    def start_capture(self):
        if not self.thread1.cam_flag:
            self.thread1.change_pixmap_signal.connect(self.update_image)    # connect to get video
            self.thread1.start()
            self.thread2 = threading.Thread(target=self.thread1.robot_run_0)    # Thread 2 is robot_run_
            self.thread2.setDaemon(True)
            self.thread2.start()            ### Wait for robot stop -> be able to press Stop
            self.thread3 = threading.Thread(target=self.on_edit_textChanged)    # Thread 3 display data on GUI
            self.thread3.setDaemon(True)
            self.thread3.start()
            self.thread4 = threading.Thread(target=self.thread1.Kalman_Call)    # Thread 4 Proximity sensor
            self.thread4.setDaemon(True)
            self.thread4.start()

    def stop_capture(self):
        if self.thread1.cam_flag and not self.thread1.trigger:
            self.thread1.change_pixmap_signal.disconnect(self.update_image)     # Unconnect video
            self.thread1.quit()
            self.thread1.wait(500)     # Have to set ms wait for stop thread 1
            self.thread1.cam_flag = False   # Toggle the flags
            self.update_image(np.zeros([480,640,3],dtype=np.uint8)) # Set black background again

    def input_filename(self):
        self.filename = self.txt_fileimg.text() # Get the img input filename
    
    def capture(self):
        if self.thread1.cam_flag:   # When camera is on, save the current frame with the input filename
            cv2.imwrite('{}.jpg'.format(self.filename),self.thread1.frame)

    def vr_change(self):
        if not self.thread1.trigger:    # Just change the robot velocity while robot is off from thread 2
            self.thread1.r.v_r = int(self.vr_set_txt.text())

    def r_call_backhome(self):
        if not self.thread1.trigger:    # Just move robot back home when robot is off from thread 2
            self.thread1.robot_home()
    
    def r_move_manually(self):
        if not self.thread1.trigger:    # Just move robot when robot is off from thread 2
            x = self.group3_txt[0].text()
            y = self.group3_txt[1].text()
            z = self.group3_txt[2].text()
            if x == '' or y == '' or z == '':
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Input again the right format of x, y, z")
                msg.setWindowTitle("Warning !")
                msg.exec_()
            else:
                self.thread1.r.servoON()
                self.thread1.r.CheckToolOff() 
                self.thread1.r.Write_Robot_XYZ(x, y, z)
                self.thread1.r.servoOFF()

    def on_edit_textChanged(self):  # Thread 3: 
        while self.thread1.cam_flag:    # Just run when cam is on
            for i in range(6):
                self.group1_txt[i].setText(str(self.thread1.xyz_r[i]))
            self.group1_txt[6].setText(str(self.thread1.num_objs))
            self.group2_txt[0].setText(str(self.thread1.r.x_c))
            self.group2_txt[1].setText(str(self.thread1.r.y_c))
            self.group2_txt[2].setText(str(self.thread1.r.z_c))
            self.group2_txt[3].setText(str(self.thread1.r.v_r))
            m = self.thread1.num_objs   # Compare the # of files in folder with items in combobox
            n = self.obj_combobox.count()
            if m != n:
                self.obj_combobox.clear()
                self.obj_combobox.addItems(["{}".format(i) for i in glob.glob("csv_files/*.csv")])
            time.sleep(0.2)

    def tof_plot(self):     # Just plot the static graph when 1 object is found
        self._dynamic_ax.clear()
        self.read_csv()
        self._dynamic_ax.scatter(self.xlist,self.ylist,label='raw', marker = '*', color = 'green')        
        self._dynamic_ax.plot(self.xlist,self.zlist,label='filter',linestyle = '-', color = 'red')
        self._dynamic_ax.set_xlabel("Samples")
        self._dynamic_ax.set_ylabel("Distance (mm)")
        self._dynamic_ax.set_title("TOF Distance Sensor Value")
        self._dynamic_ax.legend(loc='upper right')            
        self._dynamic_ax.grid()
        self._dynamic_ax.figure.canvas.draw()
        temp = np.average(self.zlist[50::-1]) - np.amin(self.zlist[50:])
        self.txt_h_check.setText(str(format(temp, '.4f')))  # Value for height checking display

    def read_csv(self):
        import csv
        self.xlist = []; self.ylist = []; self.zlist = []
        try:
            with open('{}'.format(self.obj_combobox.currentText())) as f:
                data = csv.reader(f,delimiter=',')
                data.__next__()     # Ignore the first row
                for row in data:
                    self.xlist.append(eval(row[0]))
                    self.ylist.append(eval(row[1]))
                    self.zlist.append(eval(row[2]))
        except Exception:
            print("Cannot Read the File!")

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):     # Updates the image_label with a new opencv image
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
        
    def convert_cv_qt(self, cv_img):    # Convert from an opencv image to QPixmap
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, 
                                            w, 
                                            h, 
                                            bytes_per_line, 
                                            QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    oImage = QImage("bg_gui.jpeg")
    sImage = oImage.scaled(QSize(1280,720)) # resize Image to widgets size
    qp = QPalette()
    qp.setBrush(QPalette.Window, QBrush(sImage))    # Load the background image
    app.setPalette(qp)

    a = App()
    a.show()

    sys.exit(app.exec_())
