# https://github.com/eyalabraham/computer-vision/blob/master/colorlabeler.py
# https://github.com/SBZed/object-detection-using-opencv-python/blob/master/Colordetector.py 
#   https://docs.opencv.org/3.4/de/d25/imgproc_color_conversions.html#color_convert_rgb_lab 
###############################################################################
#
#   Source object color: https://www.pyimagesearch.com/2016/02/15/determining-object-color-with-opencv/
#
#   June 28, 2018
#
###############################################################################

# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
import cv2

class ColorLabeler(object):

    def __init__(self):
        # initialize the colors dictionary, containing the color
        # name as the key and the RGB tuple as the value
        colors = OrderedDict({
                "Red": (255, 0, 0),
                "Green": (0, 255, 0),
                "Blue": (0, 0, 255),
                "Orange": (255,160,0),
                "Yellow": (255, 255, 0),
                "White": (255,255,255)})

        # allocate memory for the L*a*b* image, then initialize
        # the color names list
        self.lab = np.zeros((len(colors), 1, 3), dtype="uint8")
        self.colorNames = []

        # loop over the colors dictionary
        for (i, (name, rgb)) in enumerate(colors.items()):
            # update the L*a*b* array and the color names list
            self.lab[i] = rgb
            self.colorNames.append(name)

        # convert the L*a*b* array from the RGB color space
        # to L*a*b*
        #cv2.imshow('self lab RGB', self.lab)
        self.lab = cv2.cvtColor(self.lab, cv2.COLOR_RGB2LAB)
        #cv2.imshow('self lab', self.lab)

    def label(self, image, c):
        """Color detector and labler. Returns string with color name from dictionary."""

        # construct a mask for the contour, then compute the
        # average L*a*b* value for the masked region
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)
        mask = cv2.erode(mask, None, iterations=2)
        mean = cv2.mean(image, mask=mask)[:3]

        # initialize the minimum distance found thus far
        minDist = (np.inf, None)

        # loop over the known L*a*b* color values
        for (i, row) in enumerate(self.lab):
            # compute the distance between the current L*a*b*
            # color value and the mean of the image
            d = np.linalg.norm(row[0] -  mean) # d = dist.euclidean(row[0], mean)

            # if the distance is smaller than the current distance,
            # then update the bookkeeping variable
            if d < minDist[0]:
                minDist = (d, i)

        # return the name of the color with the smallest distance
        return self.colorNames[minDist[1]]
