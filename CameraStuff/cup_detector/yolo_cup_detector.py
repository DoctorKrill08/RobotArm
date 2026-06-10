from ultralytics import YOLO
import cv2

CUP_ID = 41
MINIMUM_CONFIDENCE = 0.25

# Load a pretrained YOLO26n model
model = YOLO("runs/detect/train/weights/best.pt")
results = model.predict("C:/Users/Admin/Robotics/RobotArm/CameraStuff/cup_detector/cup_dataset/test_images/cup0.jpg",conf = MINIMUM_CONFIDENCE)  # Predict on an image

# Render the bounding boxes onto the image array
annotated_frame = results[0].plot()
annotated_frame = cv2.resize(annotated_frame, (400, 400))

# Display using OpenCV
cv2.imshow("YOLO Detection Results", annotated_frame)
cv2.waitKey(0)  # Press any key to close the window
cv2.destroyAllWindows()