import cv2
import numpy as np
import math
import array

def distance(X1,Y1,X2,Y2):
    return math.sqrt(((Y2 - Y1) ** 2) + (X2 - X1) ** 2)


# 1. Initialize the webcam (0 is usually the default camera)
cap = cv2.VideoCapture(0)

# 2. Check if the webcam opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # 3. Capture frame-by-frame
    # 'ret' is a boolean (True if frame is captured), 'image' is the image array
    ret, image = cap.read()

    if not ret:
        print("Error: Can't receive image. Exiting...")
        break

    #Step 1. Gray Scale and make canny edge detector   + blur  
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #grayscale_image =cv2.GaussianBlur(grayscale_image,(3,3),0)

    kernel = np.ones((7, 7), np.uint8)
    t_lower = 10
    t_upper = 20

    # 3. Apply thresholding to mimic Canny's final selection step
    # This filters out weak "differences"
    edges = cv2.Canny(grayscale_image, t_lower, t_upper,5)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    cv2.imshow('Edges Only', edges)

    # Thicken white pixels
    thickened = cv2.dilate(edges, kernel, iterations=1)
    cv2.imshow('Thick edges', thickened)

    #Inverse thickend for contours
    thickened = cv2.bitwise_not(thickened)


    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thickened)

    ret, thresh = cv2.threshold(thickened, 100, 255, 0)
    contours, hierarchy = cv2.findContours(thickened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros((thickened.shape[0], thickened.shape[1], 3), dtype=np.uint8)

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
                cv2.drawContours(drawing,[box],0,(0,0,255),2)
                cv2.drawContours(drawing, contours, i, (0,255,0), 3)



    cv2.imshow('Webcam Feed', image)
    cv2.imshow('Grayscale', grayscale_image)
    cv2.imshow('Drawing',drawing)

    # 5. Press 'q' on the keyboard to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 6. Release the capture and close windows
cap.release()
cv2.destroyAllWindows()

