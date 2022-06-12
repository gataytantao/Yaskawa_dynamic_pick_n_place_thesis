from a4_image_recognition_singlecam import *


class camera_realtimeXYZ:
    img=None
    def __init__(self):
        self.imageRec=image_recognition()

    def load_background(self,background):
        self.bg=background# [0:240, :, :]

    def newline_Text(self, frame, position, text):
        font_scale = 0.4
        color = (169, 0, 255)
        thickness = 1                   # integer
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        line_height = text_size[1] + 5
        x, y0 = position
        for i, line in enumerate(text.split("\n")):
            y = y0 + i * line_height
            cv2.putText(frame,
                        line,
                        (x, y),
                        font,
                        font_scale,
                        color,
                        thickness)

    def detect_xyz(self,image):
        img = image.copy()
        # image = image[0:240, :, :]
        XYZ=[]
        obj_count, detected_points, angles, boxes, shapes = self.imageRec.run_detection(image,self.bg)
        if obj_count>0:
            for i in range(0,obj_count):
                x=detected_points[i][0]
                y=detected_points[i][1]
                w=detected_points[i][2]
                h=detected_points[i][3]
                cx=detected_points[i][4]
                cy=detected_points[i][5]
                anglez = angles[i]
                boxz = boxes[i]
                shapez = shapes[i]
                cv2.drawContours(img, [boxz], -1, (0, 255, 255), 1)
                # draw center
                cv2.circle(img,(cx,cy),3,(0,255,0),2)
                self.newline_Text(img,(x,y+h+30),"cx = "+str(self.truncate(cx,2))
                                +"px\ncy = "+str(self.truncate(cy,2))+"px\nangle = "+str(self.truncate(anglez,2))
                                +"deg\nShape: "+shapez)# +"\nColor: "+colorz)
                XYZ.append([cx, cy, anglez, shapez])
        return img, XYZ

    def truncate(self, n, decimals=0):
        n=float(n)
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier


### Test for order in XYZ

# test_1 = camera_realtimeXYZ()
# bg_0 = cv2.imread("bg_0.jpg")
# obj_0 = cv2.imread("obj_1.jpg")
# test_1.load_background(bg_0)
# shot, XYZ = test_1.detect_xyz(obj_0)
# print("XYZ =", XYZ)
# cv2.imshow("Test_1", shot)
# if cv2.waitKey(0) == ord('q'):
#     cv2.destroyAllWindows()
