### https://viblo.asia/p/da-luong-trong-python-multithreading-WAyK8MO6ZxX 
### https://lib24.vn/python-lap-trinh-da-luong.bvx 
###
from a6_main_loop import *
from threading import Thread

#### Need to modify a6_main_loop.py for cv2.imshow ...

loop=Main_loop()

t1 = Thread(target=loop.run)
t2 = Thread(target=loop.robot_run_5)
t2.setDaemon(True)
# t3 = Thread(target=loop.Kalman_Call)
# t3.setDaemon(True)
t1.start()
t2.start()
# t3.start()
# t1.join()
# t2.join()
# t3.join()

