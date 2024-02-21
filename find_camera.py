import cv2

cap = cv2.VideoCapture(-1)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Could not open camera")
    exit()

# Get the camera index
camera_index = cap.get(cv2.CAP_PROP_POS_FRAMES)

# Print the camera index
print("Camera index:", camera_index)

# Release the cam