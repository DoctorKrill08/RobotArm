import cv2
import numpy as np
import math
import array
def distance(X1,Y1,X2,Y2):
        return math.sqrt(((Y2 - Y1) ** 2) + (X2 - X1) ** 2)
class Camera():
    Ready = False

    cap = None
    target_x = 0
    target_y = 0
    visible = False

    WIDTH = 640
    HEIGHT = 320

    CENTER_X = WIDTH/2
    CENTER_Y = HEIGHT/2

    def update():
        ret, image = Camera.cap.read()

        if not ret:
            print("Error: Can't receive image.")
            return
        
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red = np.array([160, 50, 70])
        upper_red = np.array([180, 255, 255])

        mask = cv2.inRange(image_hsv, lower_red, upper_red)

        color_image = cv2.bitwise_and(image, image, mask=mask)
        #cv2.imshow('Red Only', color_image)
        
        #Now that the image is only black and red, convert to gray and then black and white via threshold
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        #cv2.imshow('Gray', gray_image)
        
        #Threshold - anything not black is white
        (thresh, binary_image) = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)

        #cv2.imshow('Black and White', binary_image)

        kernel = np.ones((7, 7), np.uint8)
        color_image = cv2.dilate(color_image, kernel, iterations=1)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image)
        contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        drawing = np.zeros((binary_image.shape[0], binary_image.shape[1], 3), dtype=np.uint8)
        Camera.visible = False
        for i in range(1,len(contours)):
            cnt = contours[i]
            M = cv2.moments(cnt)
            area = M['m00']
            if (area  < 900):
                continue
            rect = cv2.minAreaRect(cnt)
            (cx, cy), (w, h), angle = rect
            a = w * h
            box = cv2.boxPoints(rect)
            box = np.int_(box)

            x0,y0 = box[0]
            x1,y1 = box[1]
            x3,y3 = box[3]
            x,y = 0,0
            d1 = distance(x0,y0,x1,y1)
            d3 = distance(x0,y0,x3,y3)
            d = 0
            short = 0
            if (d1 >= d3):
                x,y = x1,y1
                d = d1
                short = d3
            else:
                x,y = x3,y3
                d = d3
                short = d1
            theta = math.atan2(-(y-y0),x-x0)
            theta = abs(theta * 180/math.pi)

            true_width = 0
            true_height = 0

            if ((theta > 0 and theta < 45) or 
                (theta > 135 and theta < 225) or
                (theta > 315)):
                true_width = d
                true_height = short
            else:
                true_width = short
                true_height = d
            if (area / a < 0.6):
                continue
            if (w > 50 and true_height > 20 and area < 200000 and (true_width/true_height > .5) and (((true_width / true_height) < 1.2 and theta > 60 and theta < 150) or (y0 >= 450))):
                    Camera.visible = True
                    Camera.target_x = cx
                    Camera.target_y = cy
                    cv2.drawContours(drawing,[box],0,(0,0,255),2)
                    cv2.drawContours(drawing, contours, i, (0,255,0), 3)
        
        cv2.imshow('Red Contour', drawing)

    def start():
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam.")
        else:
            Camera.Ready = True

    def end():
        Camera.cap.release()
        cv2.destroyAllWindows()

