import cv2

def focus_check():
    """
    Shows a live feed from the default camera and continuously prints the Laplacian variance
    of each frame to estimate its focus.
    """
    # Define the camera to use. '0' is usually the built-in webcam on laptops.
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Cannot open camera")
        return

    counter = 0
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # If frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Calculate the Laplacian of the image and then the variance
        laplacian_var = cv2.Laplacian(frame, cv2.CV_64F).var()
        print(f"Laplacian variance: {laplacian_var}")

        if laplacian_var > 700:
            counter += 1
        else:
            counter = 0

        if counter >= 100:
            break

        # Display the resulting frame
        cv2.imshow('Live Feed', frame)
        cv2.waitKey(1)

        # # Break the loop when 'q' is pressed
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    return cap

    # When everything is done, release the capture and destroy all OpenCV windows
    # cap.release()
    # cv2.destroyAllWindows()

def take_a_picture():
    """
    Captures an image from the default camera and saves it as a PNG file.
    
    Args:
    - file_name (str): The name of the file to save the image to.
    """
    # cap = focus_check()
    # Define the camera to use. '0' is usually the built-in webcam on laptops.
    cap = cv2.VideoCapture(0)
    cv2.waitKey(1000)

    file_name = "/home/manuel/cool_picture.png"
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Cannot open camera")
        return

    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        return 

    # Save the frame as a PNG file
    cv2.imwrite(file_name, frame)

    # When everything done, release the capture and destroy all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

    return file_name

# take_a_picture()
