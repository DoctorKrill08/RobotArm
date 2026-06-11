from ultralytics import YOLO
import cv2

MINIMUM_CONFIDENCE = 0.25

# Load a pretrained YOLO26n model
model = YOLO("yolo26n.pt")

# Train the model on the COCO8 dataset for 100 epochs
train_results = model.train(
    data= r"C:\Users\Admin\Robotics\RobotArm\CameraStuff\cup_detector\config.yaml",  # Path to dataset configuration file
    epochs=15,  # Number of training epochs
    imgsz=400,  # Image size for training
    device="cpu",  # Device to run on (e.g., 'cpu', 0, [0,1,2,3])
)

# Evaluate the model's performance on the validation set
metrics = model.val() 
results = model.predict("C:/Users/Admin/Robotics/RobotArm/CameraStuff/cup_detector/cup_dataset/test_images/cup0.jpg",conf = MINIMUM_CONFIDENCE)  # Predict on an image

for box in results[0].boxes:
    print("-------BOX--------", box.xyxy)
    print(box.conf)

path = model.export(format="onnx")  # Returns the path to the exported model

# Render the bounding boxes onto the image array
annotated_frame = results[0].plot()
annotated_frame = cv2.resize(annotated_frame, (400, 400))

# Display using OpenCV
cv2.imshow("YOLO Detection Results", annotated_frame)
cv2.waitKey(0)  # Press any key to close the window
cv2.destroyAllWindows()