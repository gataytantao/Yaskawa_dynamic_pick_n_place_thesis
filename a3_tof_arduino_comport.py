import serial

# this port address is for the serial tx/rx pins on the GPIO header
SERIAL_PORT = '/dev/cu.usbmodem1101' 
# SERIAL_PORT = 'COM4'
# be sure to set this to the same rate used on the Arduino
SERIAL_RATE = 115200

tof_err = False
try:
    ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
except Exception:
    # print("Not Connect !")
    tof_err = True

### Note: the delay time is already 3ms -> Do not add time.sleep(0.03)
# isRun = False, SERIAL_PORT = 'COM4', SERIAL_RATE = 115200

def TOF():
    try:
        # if not isRun:
        #     ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
        #     isRun = True
        if ser.is_open:
            # using ser.readline() assumes each line contains a single reading
            # sent using Serial.println() on the Arduino
            reading = ser.readline().decode('utf-8')
            # reading is a string...do whatever you want from here
            # print(reading[:len(reading)-1])
            cal = int(reading[:len(reading)-1])
            # print(cal)
            return cal, False
    except Exception:
        print("TOF is Not Connected !")
        return 0, True

# if __name__ == "__main__":
#     TOF()

# import numpy as np
# import matplotlib.pyplot as plt
# plt.axis([0, 10, 0, 1])
# for i in range(10):
#     y = np.random.random()
#     # plt.scatter(i, y)
#     plt.plot(y,'k+',label='tof data')
#     plt.pause(0.05)
# plt.show()
