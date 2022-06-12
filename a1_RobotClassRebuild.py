#!/usr/bin/env python3
# !/usr/bin/env python2

import socket
import time
import numpy as np

# Camera Intrinsics - New Camera Matrix - CAM 1 & 2 
# fx = 833.0198; fy = 832.9188 # Focal Length in pixels
# cx = 309.8543; cy = 227.2984 # Principal Point - Optical Center in pixels

# Inverse New Camera Matrix
# CAM 1 and 2
fx = 0.0012; fy = 0.0012
cx = -0.3721; cy = -0.2729

class RobotControl:
    def __init__(self, udp_ip="192.168.1.16", udp_port=10040):
        self.UDP_IP = udp_ip
        self.UDP_PORT = udp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No need to use:
        # try:
        # result = self.sock.connect_ex((self.UDP_IP,self.UDP_PORT))
        # print("CONNECTED")
        # except self.sock.gaierror:
        # self.sock.close()
        # print("NO CONNECTION")
        ### Func. disconnect(self):
        # if self.sock.connect_ex((self.UDP_IP,self.UDP_PORT)) == 0:
        # self.sock.close()
        # print("DISCONNECTED FROM ROBOT")
        self.sock.settimeout(30)
        self.x_c = 185.0000         ### current pos
        self.y_c = 0.0000
        self.z_c = 125.0000
        self.r_x = 180.0000         ### current orientation
        self.r_y = 0.0000
        self.r_z = 0.0000
        self.v_r = 2000             ### Velocity of robot moving

    def Homo_Transform(self, x, y, z, angle = 0.0000):
        # Standard Camera 1
        a1 = fx * x + cx
        a2 = fy * y + cy
        s1 = 0.1776 / 50
        s2 = 0.1728 / 50

        a1 = a1 / s1
        a2 = a2 / s2
        # Robot Parameter 1
        l1 = 242
        l2 = 154
        
        T1 = np.matrix([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        T2 = np.matrix([[0, 1, 0, l1], [-1, 0, 0, l2],[0, 0, 1, 0], [0, 0, 0, 1]])
        T3 = np.matrix([[1, 0, 0, a1], [0, 1, 0, a2], [0, 0, 1, 0], [0, 0, 0, 1]])
        T = np.dot(T1, T2)
        T = np.dot(T, T3)
        xr = format(T.item(0, 3)-4, '.3f')
        yr = format(T.item(1, 3)-4, '.3f')
        zr = format(z, '.3f')
        angle = format(angle, '.3f')
        return xr, yr, zr, angle

    def servoON(self):  # ID=00 00 after 03 01
        data = bytes.fromhex(
            '59 45 52 43 20 00 04 00 03 01 00 00 00 00 00 00 '
            '39 39 39 39 39 39 39 39 83 00 02 00 01 10 00 00 01 00 00 00')
        self.sock.sendto(data, (self.UDP_IP, self.UDP_PORT))
        time.sleep(0.1)

    def servoOFF(self): # ID= 00 01 after 03 01
        data = bytes.fromhex(
            '59 45 52 43 20 00 04 00 03 01 00 01 00 00 00 00 '
            '39 39 39 39 39 39 39 39 83 00 02 00 01 10 00 00 02 00 00 00')
        self.sock.sendto(data, (self.UDP_IP, self.UDP_PORT))
        time.sleep(0.1)
        ###
        # self.sock.close()
        # time.sleep(0.1)

    def CheckToolOn(self):  # ID=05
        data = self.ReadTool()
        n = len(data)   # ID = 06 (ReadTool), length of data received is 33 bytes
        while data[11] != 6 and n != 33:
            data = self.ReadTool()
            n = len(data)
        if data[32] == 1:
            print("Tool On")
        else:
            self.JobStart()
            print("Change to Tool On")
            time.sleep(0.1)

    def CheckToolOff(self):  # ID=05
        data = self.ReadTool()
        n = len(data)
        while data[11] != 6 and n != 33:
            data = self.ReadTool()
            n = len(data)
        if data[32] == 0:
            print("Tool Off")
        else:
            self.JobStart()
            print("Change to Tool Off")
            time.sleep(0.1)

    def ReadTool(self):  # ID = 00 06
        data = bytes.fromhex(   # #01001 => General Output; or #3001 => 0BB9 (Hex) => B9 0B
            '59 45 52 43 20 00 00 00 03 01 00 06 00 00 00 00 39 39 39 39 39 39 39 39 '
            '78 00 E9 03 01 0E 00 00')
        self.sock.sendto(data, (self.UDP_IP, self.UDP_PORT))
        data, addr = self.sock.recvfrom(1024)
        data = list(data)
        time.sleep(0.1)
        return data

    def JobStart(self):  # ID = 00 07
        self.JobSelect()
        time.sleep(0.1)
        data = bytes.fromhex(
            '59 45 52 43 20 00 04 00 03 01 00 07 00 00 00 00 39 39 39 39 39 39 39 39 '
            '86 00 01 00 01 10 00 00 01 00 00 00')
        self.sock.sendto(data, (self.UDP_IP, self.UDP_PORT))

    def JobSelect(self):  # ID=03
        data = bytes.fromhex(
            '59 45 52 43 20 00 24 00 03 01 00 03 00 00 00 00 39 39 39 39 39 39 39 39 '
            '87 00 01 00 00 02 00 00 54 4F 4F 4C 50 00 00 00 00 00 00 00 00 00 00 00 '
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
        self.sock.sendto(data, (self.UDP_IP, self.UDP_PORT))

    def Check_Pos(self, x_d, y_d, z_d):
        data = self.Read_Robot_XYZ()
        n = len(data)
        while data[11] != 2 and n < 75:
            data = self.Read_Robot_XYZ()
            n = len(data)
        if n > 75:
            self.x_c, self.y_c, self.z_c, self.r_x, self.r_y, self.r_z = self.pos_robot(data)
            a = self.compare_pos(x_d, y_d, z_d, self.x_c, self.y_c, self.z_c)
        else:
            a = 1
        return a

    def Read_Robot_XYZ(self):  # ID = 00 02
        data = bytes.fromhex(
            '59 45 52 43 20 00 00 00 03 01 00 02 00 00 00 00 39 39 39 39 39 39 39 39 '
            '75 00 65 00 00 01 00 00')
        self.sock.sendto(data, (self.UDP_IP, self.UDP_PORT))
        data, addr = self.sock.recvfrom(1024)
        data = list(data)
        time.sleep(0.1)
        return data

    def pos_robot(self, data):
        # X 52 55
        x = self.to_int(data[52], data[53], data[54], data[55])
        # Y 56 59
        y = self.to_int(data[56], data[57], data[58], data[59])
        # Z 60 63
        z = self.to_int(data[60], data[61], data[62], data[63])
        # Rx 64 67
        rx = self.to_int(data[64], data[65], data[66], data[67])
        # Ry 68 71
        ry = self.to_int(data[68], data[69], data[70], data[71])
        # Rz 72 75
        rz = self.to_int(data[72], data[73], data[74], data[75])
        return x, y, z, rx, ry, rz

    def Write_Robot_XYZ(self, x_d, y_d, z_d, angle = "0.0000"): # ID = 00 04
        rx = "180.0000"
        ry = "0.0000"
        rz = angle
        data = bytes.fromhex(
            '59 45 52 43 20 00 68 00 03 01 00 04 00 00 00 00 39 39 39 39 39 39 39 39 '
            '8A 00 01 00 01 02 00 00')
        x, y, z, rx, ry, rz = self.char2int(x_d, y_d, z_d, rx, ry, rz)
        robot = bytes.fromhex('01 00 00 00 00 00 00 00')
        speed_type = bytes.fromhex('01 00 00 00')
        speed = self.to_hex(self.v_r)
        coor = self.to_hex(16)
        xhex = self.to_hex(x)
        yhex = self.to_hex(y)
        zhex = self.to_hex(z)
        rxhex = self.to_hex(rx)
        ryhex = self.to_hex(ry)
        rzhex = self.to_hex(rz)
        behind = bytes.fromhex(
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 '
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
            '00 00 00 00 00 00 00 00 00 00 00 00')
        datas = robot + speed_type + speed + coor + xhex \
                + yhex + zhex + rxhex + ryhex + rzhex + behind
        datas = data + datas
        self.sock.sendto(datas, (self.UDP_IP, self.UDP_PORT))
        time.sleep(0.1)
        while self.Check_Pos(x_d, y_d, z_d) == 1:
            pass

    def to_int(self, x, y, z, a):
        re = a * (16 ** 6) + z * (16 ** 4) + y * (16 ** 2) + x
        if re > 2147483648:  # 2^31
            re = re - 16 ** 8
        return re

    def compare_pos(self, xc, yc, zc, x, y, z):
        xg, yg, zg, rxg, ryg, rzg = self.char2int(xc, yc, zc, 0, 0, 0)
        if abs(xg - x) < 100 and abs(yg - y) < 100 and abs(zg - z) < 100:
            return 0
        else:
            return 1

    def char2int(self, x, y, z, rx, ry, rz):
        x = int(float(x) * 1000)
        y = int(float(y) * 1000)
        z = int(float(z) * 1000)
        rx = int(float(rx) * 10000)
        ry = int(float(ry) * 10000)
        rz = int(float(rz) * 10000)
        return x, y, z, rx, ry, rz

    def to_hex(self, z):
        if z < 0:
            z = z + 16 ** 8
        z1 = int(z / (16 ** 6))
        ztem = z - z1 * (16 ** 6)
        z2 = int(ztem / (16 ** 4))
        ztem = ztem - z2 * (16 ** 4)
        z3 = int(ztem / (16 ** 2))
        z4 = ztem - z3 * (16 ** 2)
        v1 = [z4, z3, z2, z1]
        bv = bytes(v1)
        return bv


z_inc = 4.0000
# Home position 1
xc = "185.0000"; yc = "0.0000"; zc = "125.0000"
# Home position 2
xc2 = "250.0000"; yc2 = "0.0000"; zc2 = "0.0000"; zc2_test = "-20.0000"
# Conveyor Sensor
x2 = "250.0000"; y2 = "100.0000"; z2 = "-60.0000"
# Disk Sensor
x3 = "-36.0000"; y3 = "-250.0000"; z3 = "0.0000"# z3 = "-61.0000"

# r = RobotControl()
# print(r.Homo_Transform(320,240))  ### came center pixel
# print(r.Homo_Transform(778,480))  ### pick pos pixel 1st        ### yr = "0.0000"
# print(r.Homo_Transform(630,480))  ### pick pos pixel 2nd        ### yr = "-50.0000"
# print(r.Homo_Transform(482,480))  ### pick pos pixel 3rd        ### yr = "-100.0000"


# r.servoON()
# r.Check_Pos(xc, yc, zc)
# print(r.x_c, r.y_c, r.z_c)

# r.Write_Robot_XYZ(xc2, yc2, zc2, "0.0000")
# r.CheckToolOff()

# r.servoOFF()


