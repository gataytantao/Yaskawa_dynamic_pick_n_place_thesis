# https://thetalog.com/machine-learning/kalman-filter/
import time
import smbus            # Library IO pins of Jetson Nano
bus = smbus.SMBus(1)    # Initialise the GPIO pin 1 

def TOF(address = 0x52):        # I2C scanning found by using: $ i2cdetect -y -r 1
    try:
        val1 = bus.read_byte_data(address, 0)
        val2 = bus.read_byte_data(address, 1)
        val = val1 << 8 | val2
        time.sleep(0.03)
        return val, False
    except Exception:
        print("TOF is not Connected !")
        return 0, True
