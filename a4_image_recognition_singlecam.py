import cv2
import numpy as np
import math
from a2_ShapeDetector import ShapeDetector
# from ColorLabeler import ColorLabeler

class image_recognition:
    def __init__(self):
        # valid contour parameters limits (in pixels)
        self.MIN_AREA = 900  # 30x30
        self.MAX_AREA = 90000  # 300x300
        # aspect ratio width/height
        self.MIN_ASPECTRATIO = 1 / 5
        self.MAX_ASPECTRATIO = 5
        self.OtsuSensitivity = 22

    def run_detection(self, img, bg):
        obj_count, contours_detected, contours_validindex = self.detectObjects(img, bg)
        obj_count,detected_points,angles,boxes,shapes = self.detectionOutput(obj_count,contours_validindex,contours_detected)
        return obj_count, detected_points, angles, boxes, shapes

    def detectObjects(self, image, bg_img, externalContours=True):
        img = image.copy()
        background_img = bg_img.copy()
        # Process Image Difference
        diff = self.calculateDifference_Otsu(img, background_img)
        # Find the Contours: use RETR_EXTERNAL for only outer contours... use RETR_TREE for all the hierarchy
        if externalContours:
            contours_detected, hierarchy = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours_detected, hierarchy = cv2.findContours(diff, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # calculate key variables
        height, width = img.shape[:2]
        # Identify the VALID Contours
        contours_validindex = self.identify_validcontours(contours_detected, height, width)
        obj_count = len(contours_validindex)
        return obj_count, contours_detected, contours_validindex

    def detectionOutput(self, obj_count, validcontours, diff_contours):
        detected_points = []
        boxes = []
        angles = []
        shapes = []
        SD = ShapeDetector()
        if len(validcontours) > 0:
            for i in range(0, len(validcontours)):
                cnt = diff_contours[validcontours[i]]
                # get vertical rectangle detected_points
                x, y, w, h = cv2.boundingRect(cnt)

                # get (rotated) rectangle (top-left x-y, width-height, +angle)
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)   # return 2D - box (4 corner points)
                box = np.int0(box)          # return array type int64
                boxes.append(box)           # draw the contours
                origin = box[0]
                rect_width, rect_height = rect[1]
                if rect_width > rect_height:
                    target = box[3]
                else:
                    target = box[1]
                dv = target[1] - origin[1]
                du = target[0] - origin[0]
                angle1 = math.atan2(dv, du)
                angle = angle1 * 180 / np.pi
                # Below adjust for our camera - our Homogeneous Transforms
                if angle >= 0: angle = 90 - angle
                else: angle = -90 - angle
                angles.append(angle)
                shape = SD.detect(cnt)
                shapes.append(shape)

                # get centroid
                M = cv2.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                points = [x, y, w, h, cx, cy]
                detected_points.append(points)

        # if (obj_count>1 or len(validcontours)==0):               
        #     self.previewImage("Multiple Objects Detected",img_output)
        #     one_object=False
        # else:
        #     self.previewImage("One Objects Detected",img_output)
        #     one_object=True
        return obj_count, detected_points, angles, boxes, shapes # , colors

    def calculateDifference_Otsu(self, img, background_img):
        # Background - Gray
        background_img_gray = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)
        # Image - Gray
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Calculate Difference
        diff_gray = cv2.absdiff(background_img_gray, img_gray)
        # Diff Blur and Threshold:
        diff_gray_blur = cv2.GaussianBlur(diff_gray, (5, 5), 0)
        ret, otsu_thresh = cv2.threshold(diff_gray_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if ret < self.OtsuSensitivity:
            diff = cv2.absdiff(background_img_gray, background_img_gray)
        else:
            diff = cv2.GaussianBlur(otsu_thresh, (5, 5), 0)
        return diff

    def identify_validcontours(self, cnt, height, width):  # Helps discard noise on contour detection.
        contours_validindex = []
        contour_index = -1
        for i in cnt:
            contour_index = contour_index + 1
            ca = cv2.contourArea(i)
            # Calculate W/H Ratio
            x, y, w, h = cv2.boundingRect(i)
            aspect_ratio = float(w) / h
            # Flag as edge_noise if the object is at a Corner
            edge_noise = False
            if x == 0:
                edge_noise = True
            if y == 0:
                edge_noise = True
            if (x + w) == width:
                edge_noise = True
            if (y + h) == height:
                edge_noise = True
            # DISCARD noise with measure if area not within parameters
            if ca > self.MIN_AREA and ca < self.MAX_AREA:
                # DISCARD as noise on ratio
                if aspect_ratio >= self.MIN_ASPECTRATIO and aspect_ratio <= self.MAX_ASPECTRATIO:
                    # DISCARD if at the Edge
                    if edge_noise == False:
                        contours_validindex.append(contour_index)
        return contours_validindex
