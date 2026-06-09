from ultralytics import YOLO

model = YOLO("yolov8n.yaml")

train_results = model.train(
    data="config.yaml",  # Path to dataset configuration file
    epochs=1,  # Number of training epochs
)

# Evaluate the model's performance on the validation set
metrics = model.val()

# Perform object detection on an image
results = model("C:/Users/Admin/Robotics/RobotArm/CameraStuff/cup_dataset/test_images/image.jpg")  # Predict on an image
results[0].show()  # Display results

# Export the model to ONNX format for deployment
path = model.export(format="onnx")  # Returns the path to the exported model