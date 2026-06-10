import cv2
import numpy as np
import math
import array

from enum import Enum

def distance(X1,Y1,X2,Y2):
    return math.sqrt(((Y2 - Y1) ** 2) + (X2 - X1) ** 2)
class CameraResults():
    def __init__(self):
        self.visible = False
        self.image = None
        self.x = Camera.CENTER_X
        self.y = Camera.CENTER_Y
        self.width = 0
        self.height = 0
def center_box(a,b):
    return (b + a) / 2
def yolo_cup_detector_read(image):
    from ultralytics import YOLO
    MINIMUM_CONFIDENCE = 0.1

    # Load a pretrained YOLO26n model
    model = YOLO("runs/detect/train/weights/best.pt")
    results = model.predict(image,conf = MINIMUM_CONFIDENCE)  # Predict on an image

    # Render the bounding boxes onto the image array
    annotated_frame = results[0].plot()
    
    camera_result = CameraResults()
    camera_result.image = annotated_frame

    if len(results[0].boxes) > 0:
        # GFind closest box to center of cam
        closest_box = results[0].boxes
        min_distance = 1000
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = center_box(x2,x1)
            cy = center_box(y2,y1)
            dis = distance(cx,cy,Camera.CENTER_X,Camera.CENTER_Y)
            if (dis < min_distance):
                dis = min_distance
                closest_box = box

        x1, y1, x2, y2 = closest_box.xyxy[0].tolist()

        camera_result.visible = True
        camera_result.x = center_box(x2,x1)
        camera_result.y = center_box(y2,y1)
        camera_result.width = x2 - x1
        camera_result.height = y2 - y1


    return camera_result

class CameraMode(Enum):
    YOLO_CUP_DETECTOR = "YOLO_CUP_DETECTOR",
    COLOR_BLOB_DETECTOR = "COLOR_BLOB_DETECTOR"

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

    FIELD_OF_VIEW = 78 #Degrees

    mode = CameraMode.YOLO_CUP_DETECTOR

    def update():
        ret, image = Camera.cap.read()

        if not ret:
            print("Error: Can't receive image.")
            return

        cv2.imshow('Image', image)
        
        Camera.visible = False
        Camera.target_x = Camera.CENTER_X
        Camera.target_y = Camera.CENTER_Y

        camera_result = Camera.mode_to_output(image)
            

        cv2.imshow('Final', camera_result.image)

        Camera.visible = camera_result.visible
        if (Camera.visible):
            Camera.target_x = camera_result.x
            Camera.target_y = camera_result.y
        
        del camera_result

    def pixels_to_degrees_width(pixels):
        return (pixels / Camera.WIDTH) * Camera.FIELD_OF_VIEW
    def pixels_to_degrees_height(pixels):
        return (pixels / Camera.HEIGHT) * Camera.FIELD_OF_VIEW
    def status():
         return f"Visible: {Camera.visible}\n target x: {Camera.target_x}\n target y: {Camera.target_y}\n error x: {Camera.CENTER_X - Camera.target_x}\n erorr y: {Camera.CENTER_Y - Camera.target_y}"
    def start():
        Camera.cap = cv2.VideoCapture(0)
        from ultralytics import YOLO
        if not Camera.cap.isOpened():
            print("Error: Could not open webcam.")
        else:
            Camera.Ready = True
    
    def end():
        Camera.Ready = False
        Camera.cap.release()
        Camera.destroy_windows()
    def destroy_windows():
        cv2.destroyAllWindows()
    def mode_to_output(image):
        if Camera.mode == CameraMode.YOLO_CUP_DETECTOR:
            return yolo_cup_detector_read(image)
            
"""
Camera.start()
while True:
     Camera.update()
     if cv2.waitKey(1) & 0xFF == ord('q'):
        break
Camera.end()
"""
