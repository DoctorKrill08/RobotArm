import cv2
import numpy as np

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
    grayscale_image =cv2.blur(grayscale_image,(5,5))

    t_lower = 20
    t_upper = 50

    cv2.imshow('Webcam Feed', image)
    cv2.imshow('Grayscale', grayscale_image)

    #Draw lines of best fit with lines of set size

    sobel_x = cv2.Sobel(grayscale_image, cv2.CV_64F, 1, 0, ksize=3)

    # 2. Convert back to absolute 8-bit for visualization
    abs_sobel_x = np.absolute(sobel_x)
    sobel_8bit = np.uint8(abs_sobel_x)

    # 3. Apply thresholding to mimic Canny's final selection step
    # This filters out weak "differences"
    _, vertical_edges = cv2.threshold(sobel_8bit, t_lower, t_upper, cv2.THRESH_BINARY)

    cv2.imshow('Vertical Edges Only', vertical_edges)

    kernel = np.ones((5, 5), np.uint8)

    # Thicken white pixels
    thickened = cv2.dilate(vertical_edges, kernel, iterations=1)
    cv2.imshow('Thick vertical edges', thickened)

    #Filter out small blobs
    thickened = cv2.imread('blobs.jpg', 0)


    # Find components and their stats
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(vertical_edges)

    # Create an empty result mask
    min_area = 50  # Set your threshold here
    result = np.zeros_like(vertical_edges)

    # Start from 1 to skip the background (label 0)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            result[labels == i] = 255
    cv2.imshow('Filterd vertical', result)


    # 5. Press 'q' on the keyboard to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 6. Release the capture and close windows
cap.release()
cv2.destroyAllWindows()