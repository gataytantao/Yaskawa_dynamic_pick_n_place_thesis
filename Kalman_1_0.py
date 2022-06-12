import time
from a3_tof_read import *
# from a3_tof_arduino_comport import *  # Just use 1 of a3_.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use('bmh') 
# http://www.futurile.net/2016/02/27/matplotlib-beautiful-plots-with-style/

def save_data_csv(raw, filtered, f_shape = "Rectangle", f_height = 0):
    import glob, csv
    num_objs = len(glob.glob("csv_files/*.csv"))      # return the length of file list
    data_lst = [["index", 'raw', 'filtered']]         # store the data in rows
    for k in range(len(raw)):
        data_lst.append([k, raw[k], format(filtered[k],'.4f')]) # append the data in rows
    try:
        with open('csv_files/'+f_shape+'_'+str(f_height)+'.csv',# Format of 1 file: Rectangle_10.csv 
                    mode='w+', 
                    encoding='utf8',
                    newline='') as f:
            writer = csv.writer(f,delimiter = ',')  # Create the writer obj (as pointer)
            writer.writerows(data_lst)              # Write data in rows
            num_objs = len(glob.glob("csv_files/*.csv"))   # Update the number of objects (file list)
    except Exception:
        print("Saving Error! ")
    pass

n_iteration = 1000
value = 95.0
A = np.array([[1]])
Q = np.array([[1e-4]])
G = np.array([[1]])
R = np.array([[5e-3]])
list_of_x = []
list_of_y = []

x_hat = np.array([[value]])
sigma = np.array([[1.0]])
datas = []

for i in range(n_iteration):
    # Prediction
    x_hat = A @ x_hat
    sigma = A @ sigma @ A.T + Q
    list_of_x.append(float(x_hat))

    # Measurement
    pre = time.time()
    pre_value = value
    value, tof_err = TOF()
    if value < 50 or value > 200:
        value = pre_value
    if tof_err:
        break
    print('Distance =',value, "t_pass =", time.time()-pre)
    y = np.array([[value]])

    kalman_gain = sigma @ G.T @ np.linalg.inv(G @ sigma @ G.T + R)
    x_hat = x_hat + kalman_gain @ (y - G @ x_hat)
    sigma = (np.eye(len(sigma)) - kalman_gain @ G) @ sigma ### np.eye -> identity matrix
    print(x_hat)

    list_of_y.append(float(y))

if not tof_err:
    # temp = round(np.average(list_of_x[:4000:-1]),1) - round(np.amin(list_of_x[250:]),1)
    temp = np.average(list_of_x[50::-1]) - np.amin(list_of_x[50:])
    # temp = round(temp,1)
    print("Check =", temp)
    f_shape = "Rectangle"
    # if f_shape == "Rectangle" or f_shape == "Square":
    #     temp -= 5    # This ensure the area not affect on the sampling data
    if f_shape == "Triangle" or f_shape == "Circle":
        temp += 5    # This ensure the area not affect on the sampling data
    ###
    if 5 <= temp <= 15:
        temp = 10
    elif 15 < temp <= 25:
        temp = 20
    elif 25 < temp <= 35:
        temp = 30
    else:
        temp = 0
    ###


    # save_data_csv(list_of_y, list_of_x, f_height = temp)
    # plt.plot(list_of_y,'k+',label='tof data')
    plt.plot(list_of_y,'b-',label='tof data')
    plt.plot(list_of_x,'r-',label='filtered data')
    # plt.ylim(50,150)
    plt.legend()

    plt.xlabel('$t$')
    plt.ylabel('mm')
    plt.title('Kalman Filter')

    plt.show()
