from a5_camera_realworldxyz import *
from a1_RobotClassRebuild import *
from a3_tof_read import *
# from a3_tof_arduino_comport import *  # Just use 1 of a3_.py
import cv2, time, glob, csv, numpy as np
from PyQt5.QtCore import pyqtSignal, QThread

class Main_loop(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)       # Initialize the frame from OPENCV

    def __init__(self):
        super().__init__()          # Inherit from QThread.__init__
        self.r = RobotControl()     # Initialize the robot connection
        self.cameraXYZ = camera_realtimeXYZ()   # Initialize the Image Processing 
        self.get_tof = False    # Kalman_Call enable
        self.trigger = False    # robot_run_ enable
        self.XYZ_obj = [[320, 240, 0.0000, "Unidentified"]] # raw objs for robot_on_
        self.zr_adj = 5.0000          # Kalman_Call output        old: z_add
        self.dx = []                    # object moves in 1 frame (pixel)
        self.dt = []                    # time between object-found frames
        self.v = 0.0000                 # object velocity - dynamic
        self.t_gap = 4.0000             # robot_run_ picking time
        # self.shape_chosen = "Unidentified"      # choose_xyz -> GUI 
        self.xyz_r = ["Unidentified" for i in range(6)] # choose_xyz; robot_run_
        self.order_place = {"Rectangle":[-36.0000,-250.0000],   # Original xy3
                            "Square":[-36.0000,-300.0000],      # x;y = 0;-50
                            "Triangle":[-106.0000,-250.0000],   # x;y = -70;0
                            "Circle":[34.0000, -250.0000]}      # x;y = 70;0
        self.cam_flag = False       # Need for webcam thread (OPENCV)
        self.num_objs = len(glob.glob("csv_files/*.csv"))       # The # of files also found objects

    def robot_home(self):           # This method used for meeting UDP error -> robot halt
        self.r.servoON()
        self.r.CheckToolOff()
        self.r.Write_Robot_XYZ(xc2, yc2, zc2, "0.0000")        # Home
        self.r.servoOFF()

    def choose_xyz(self):
        self.xyz_r = []
        for i in self.XYZ_obj:
            if i[3] == self.shape_chosen and i[3] != "Unidentified":
                self.xyz_r = i
                break
        if len(self.xyz_r) > 0: 
            return True
        else: 
            return False

    def run(self): # Named "run", cannot change !!! -> Used for QThread; This for OPENCV Webcam
        obj_count = 0
        bg_counter = 0
        id_counter = 0
        bg_capture = False
        self.cam_flag = True        # Set flags ON
        video = cv2.VideoCapture(0)   # Setup the camera index to run video
        while True:
            e1 = cv2.getTickCount()         ####### other way for getting the execution time
            ###
            _, self.frame = video.read()
            # self.frame = cv2.imread("test_imgs/obj_0.jpg")  ### Please Delete !!!

            if bg_capture:      # with background captured, image detection will now work
                obj_count_prev = obj_count
                # self.frame = cv2.imread("test_imgs/obj_36.jpg") ### Please Delete !!! 
                self.frame, XYZ = self.cameraXYZ.detect_xyz(self.frame)
                obj_count = len(XYZ)
                # start counter when same number of objects detected between frames
                if obj_count > 0 and obj_count == obj_count_prev and not self.trigger:
                    self.cameraXYZ.newline_Text(self.frame,(20, 20), "Object Detected")
                    ###
                    if id_counter == 0:# len(self.dx) == 0:
                        dx_pre = XYZ[len(XYZ)-1][0]         ### Initialize by = 0 ?????
                    else:
                        dx_check = XYZ[len(XYZ)-1][0] - dx_pre
                        if 0 < dx_check <= 15:              # In class <= 5, at home <= 15
                            self.dx.append(dx_check)
                            self.dt.append(ticktime)        ### other way to get the execution time
                        dx_pre = XYZ[len(XYZ)-1][0]
                    ###
                    id_counter += 1
                if id_counter > 15: # same number of objects in 30 frames, then trigger robot
                    self.get_tof = True     # Kalman_Call enable
                    self.XYZ_obj = XYZ      # Data for choose_xyz_
                    ###
                    if len(self.dx) > 0 and len(self.dt) > 0:
                        self.v = np.average(self.dx)/np.average(self.dt)
                    else: 
                        self.v = 0
                    self.dx = []
                    self.dt = []
                    ###
                    self.trigger = True     # robot_run_ enable
                    id_counter = 0
                    # bg_capture = False
            else:
                if bg_counter > 10: # counter reach 10 provides warm up, then capture background
                    self.cameraXYZ.load_background(self.frame)
                    print("BACKGROUND CAPTURED!")
                    bg_capture = True
                    bg_counter = 0
                else:
                    self.cameraXYZ.newline_Text(self.frame,(20, 20), "WARMING UP")
                    bg_counter += 1
            ### Stop camera
            if not self.cam_flag:           # Wait for press STOP -> cam_flag OFF
                break
            self.change_pixmap_signal.emit(self.frame)      # TRANSMIT the frames from OPENCV
            # if cv2.waitKey(1) % 256 == ord('q'):
            #     break
            # cv2.imshow("Capturing",self.frame)
            ###
            e2 = cv2.getTickCount()         ####### other way for getting the execution time
            ticktime = (e2 - e1)/cv2.getTickFrequency()
        # video.release()
        # cv2.destroyAllWindows()

    # Dynamic pick method 3_3 (REFIXED): obj found -> move to the predefined pos -> wait for obj to magnet on
    def robot_run_1(self):
        while self.cam_flag:# True:
            if self.trigger:
                time.sleep(0.1)
                x_pick_px = 482             # This for y_r = "-100.0000"
                obj_wait = 0
                r_past = time.time()        # Set time for robot picking
                self.r.servoON()
                self.r.CheckToolOff()
                temp = self.XYZ_obj[0]      # Choose the 1st object
                if temp[3] == "Rectangle" or temp[3] == "Square":
                    self.zr_adj -= 5    # This ensure the area not affect on the sampling data
                ###
                if self.zr_adj <= 15:   # Conditions for the filtered data 
                    self.zr_adj = -55.0000
                elif 15 < self.zr_adj <= 25:
                    self.zr_adj = -45.0000
                elif 25 < self.zr_adj:
                    self.zr_adj = -35.0000
                else:
                    self.zr_adj = 0.0000
                ###
                temp.insert(2,self.zr_adj)  # Add z or height component (default = -55.0000 for 1cm height)
                self.xyz_r[:4] = self.r.Homo_Transform(temp[0], temp[1], temp[2], temp[3])
                # self.xyz_r[4] = format(self.v, '.3f') # For GUI display - obj-velocity
                self.xyz_r[4] = format((0.0012*(self.v+320)-0.3721)/(0.1776/50)-3.3502, '.3f') # Change px/s -> mm/s
                self.xyz_r[5] = temp[4]     # Shape displayed on GUI
                if temp[0] < 320:           # Check the detection zone 
                    if self.v > 0:              # Dynamic
                        self.xyz_r[1] = "-100.0000"            ### Which pixel for wait???? -> Pixel 482th
                        obj_wait = (x_pick_px - temp[0])/self.v    # self.v = 0.0000 for static, 82.0000 for default
                    elif self.v == 0:           # Static
                        obj_wait = 0
                    self.r.Write_Robot_XYZ(self.xyz_r[0], self.xyz_r[1], self.xyz_r[2], self.xyz_r[3]) # Pick
                    self.t_gap = time.time() - r_past   # Compute the picking time
                    obj_wait -= (self.t_gap + 0.35)     # print("Wait more", obj_wait)
                    if obj_wait > 0:                    # delay if dynamic
                        time.sleep(obj_wait)
                    self.r.CheckToolOn()
                    self.r.Write_Robot_XYZ(xc2, yc2, zc2, "0.0000")         # Home
                    xy3 = self.order_place[self.xyz_r[3]]
                    self.r.Write_Robot_XYZ(xy3[0], xy3[1], z3, "0.0000")    # Place
                    self.r.CheckToolOff()
                    # time.sleep(0.1)
                    self.r.Write_Robot_XYZ(xc2, yc2, zc2, "0.0000")         # Home
                self.r.servoOFF()
                self.trigger = False
            else:
                time.sleep(0.0001)
        else: print("Robot Stop Completely!!!")
        pass

    # Demo at home:
    def robot_run_0(self):
        while self.cam_flag:
            if self.trigger:
                time.sleep(0.1)
                temp = self.XYZ_obj[0] # len(self.XYZ_obj)-1]      ### Which obj/contour chosen???
                
                temp.insert(2,self.zr_adj)      # Insert the zr component 
                self.xyz_r[:4] = self.r.Homo_Transform(temp[0], temp[1], temp[2], temp[3])
                # self.v = 82         ## Delete please ! 

                self.xyz_r[4] = format((0.0012*(self.v+320)-0.3721)/(0.1776/50)-3.3502, '.3f')
                # self.xyz_r[4] = format(self.v, '.3f')
                self.xyz_r[5] = temp[4] # In self.xyz_r, the order is: xr, yr, zr, angle, r_v, shape

                print("Robot ON")
                time.sleep(5)
                print("Robot OFF")

                self.trigger = False
            else:
                time.sleep(0.0001)
        else: print("Robot Stop Completely!!!")
        pass

    def Kalman_Call(self):
        value = 100.0           # Initial Value for the filter input state
        A = np.array([[1]])     # State-transition Matrix of Model
        Q = np.array([[1e-4]])  # Covariance Matrix of the process noise
        G = np.array([[1]])     # Observation Matrix of Model
        R = np.array([[1e-3]])  # Covariance Matrix of the observation noise
        list_of_x = []          # Kalman output
        list_of_y = []          # Kalman input or raw data from TOF()
        # Setup initial distribution parameters
        x_hat = np.array([[value]])
        sigma = np.array([[1.0]])
        while self.cam_flag:
            # Measurement Stage (have delay in it):
            pre_value = value
            value, self.tof_err = TOF() # time.sleep(0.03)  # Sampling Time
            if value < 50 or value > 200: # Check the outlayers (value may be 2000 or 0)
                value = pre_value       # If out of conditions, we get the previous value.
            if self.tof_err:            # If not connect, we stop the thread
                print("Tof cannot be read!"); break            
            if not self.get_tof:
                # Prediction Stage:
                x_hat = A @ x_hat
                sigma = A @ sigma @ A.T + Q
                list_of_x.append(float(x_hat))
                y = np.array([[value]])
                # Update (Correction) Stage:
                kalman_gain = sigma @ G.T @ np.linalg.inv(G @ sigma @ G.T + R)
                x_hat = x_hat + kalman_gain @ (y - G @ x_hat)
                sigma = (np.eye(len(sigma)) - kalman_gain @ G) @ sigma
                list_of_y.append(float(y))
                ### Cannot wait forever -> After 2000 samples -> Save and Restart
                if len(list_of_y) >= 2000:
                    self.save_data_csv(list_of_y, list_of_x, self.XYZ_obj[0][3], 0)
                    ### REFRESH THE STORAGES
                    list_of_x = []  # Kalman output
                    list_of_y = []  # Kalman input or raw data from TOF()
                    # Setup initial distribution parameters
                    x_hat = np.array([[0.0]])
                    sigma = np.array([[1.0]])
                    self.get_tof = False
            else:
                self.zr_adj = np.average(list_of_x[50::-1]) - np.amin(list_of_x[50:]) # Do not use "round()"
                print("Check =", self.zr_adj)
                # if self.XYZ_obj[0][3] == "Rectangle" or self.XYZ_obj[0][3] == "Square":
                #     self.zr_adj -= 5    # This ensure the area not affect on the sampling data

                if self.XYZ_obj[0][3] == "Triangle" or self.XYZ_obj[0][3] == "Circle":
                    self.zr_adj += 2#4    # This ensure the area not affect on the sampling data

                ###
                height = 0                  # Used for file rename
                if 5 <= self.zr_adj <= 15:
                    self.zr_adj = -55.0000
                    height = 10
                elif 15 < self.zr_adj <= 25:
                    self.zr_adj = -45.0000
                    height = 20
                elif 25 < self.zr_adj <= 35:
                    self.zr_adj = -35.0000
                    height = 30
                else:
                    self.zr_adj = 0.0000
                ###
                
                self.save_data_csv(list_of_y, list_of_x, self.XYZ_obj[0][3], height)
                #### Wait for robot stop    # while self.trigger: pass -> Lagging the thread
                time.sleep(7)
                if not self.trigger:
                    ### REFRESH THE DATA GETTING STORAGEs
                    list_of_x = []          # Kalman output
                    list_of_y = []          # Kalman input or raw data from TOF()
                    # Setup initial distribution parameters
                    x_hat = np.array([[0.0]])
                    sigma = np.array([[1.0]])
                    self.get_tof = False
        else: print("Stop reading TOF Completely !!! ")
        pass

    def save_data_csv(self, raw, filtered, f_shape, f_height): # 3 columns for stored data
        self.num_objs = len(glob.glob("csv_files/*.csv")) # return the length of file list
        data_lst = [["index", 'raw', 'filtered']]         # store the data in rows
        for k in range(len(raw)):
            data_lst.append([k, raw[k], format(filtered[k],'.4f')]) # append the data in rows
        try:
            with open('csv_files/'+f_shape+'_'+str(self.num_objs)+'_'+str(f_height)+'.csv',# Format of 1 file: Rectangle_1_10.csv 
                        mode='w+', 
                        encoding='utf8',
                        newline='') as f:
                writer = csv.writer(f,delimiter = ',')  # Create the writer obj (as pointer)
                writer.writerows(data_lst)              # Write data in rows
                self.num_objs = len(glob.glob("csv_files/*.csv"))   # Update the number of objects (file list)
        except Exception:
            print("Saving Error! ")
        pass
