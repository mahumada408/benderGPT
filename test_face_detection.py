import argparse
import cvzone
from cvzone.FaceDetectionModule import FaceDetector
import cv2
import socket
import time

# Initialize the webcam
cap = cv2.VideoCapture(0)

class Server:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.setup_server()
        self.clients = []

    def setup_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Server started. Waiting for connection...")

    def handle_client(self, client_socket):
        try:
            while True:
                # Send current time to client
                message = f"Server Time: {time.ctime()}\n"
                for client_socket in self.clients:
                    client_socket.send(message.encode('utf-8'))
                time.sleep(0.01)  # Wait for 2 seconds before sending next message
        except ConnectionResetError:
            print("Client disconnected")
        finally:
            client_socket.close()

    def run(self):
        while len(self.clients) < 1:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            print(f"Connection established with {addr}")
        # self.handle_client(client_socket)

    def close_server(self):
        self.server_socket.close()
        print("Server shut down successfully.")
  
    def send_data(self, string_message):
        # string_message = f"{message_x}, {message_y}"
        disconnected_clients = []
        for client_socket in self.clients:
            try:
                client_socket.send(string_message.encode('utf-8'))
            except (ConnectionResetError, BrokenPipeError) as e:
                print("Client disconnected")
                disconnected_clients.append(client_socket)
        
        # Clean up disconnected clients
        for client_socket in disconnected_clients:
            self.clients.remove(client_socket)
            try:
                client_socket.close()
            except Exception as e:
                print(f"Error closing socket: {e}")

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--no-tracking', action='store_true', help='No face tracking')
    args = parser.parse_args()

    if not args.no_tracking:
        server = Server()
        server.run()

    width  = None
    height = None
    if cap.isOpened(): 
        # get vcap property 
        width  = cap.get(3)  # float `width`
        height = cap.get(4)  # float `height`
        print(f"{width}x{height}")

    # Initialize the FaceDetector object
    # minDetectionCon: Minimum detection confidence threshold
    # modelSelection: 0 for short-range detection (2 meters), 1 for long-range detection (5 meters)
    detector = FaceDetector(minDetectionCon=0.5, modelSelection=0)

    last_save_time = 0.0

    # Run the loop to continually get frames from the webcam
    while True:
        # Read the current frame from the webcam
        # success: Boolean, whether the frame was successfully grabbed
        # img: the captured frame
        success, img = cap.read()
        # if time.time() - last_save_time > 1:
        laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
        # print(f"Laplacian variance: {laplacian_var}")
        if laplacian_var > 700 and time.time() - last_save_time > 0.5:
            # Save the frame as a PNG file
            cv2.imwrite("/home/manuel/cool_picture.png", img)
            last_save_time = time.time()

        # Detect faces in the image
        # img: Updated image
        # bboxs: List of bounding boxes around detected faces
        img, bboxs = detector.findFaces(img, draw=False)

        # Check if any face is detected
        if bboxs:
            # Loop through each bounding box
            for bbox in bboxs:
                # bbox contains 'id', 'bbox', 'score', 'center'
                # only process bboxes with a score greater than 80.
                score = int(bbox['score'][0] * 100)
                if score < 80:
                    continue

                # ---- Get Data  ---- #
                center = bbox["center"]
                x, y, w, h = bbox['bbox']
                

                # ---- Draw Data  ---- #
                cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
                cvzone.putTextRect(img, f'{score}%', (x, y - 10))
                cvzone.cornerRect(img, (x, y, w, h))
                # print(center)
                camera_delta = (center[0] - (width/2))
                camera_delta_y = (center[1] - (height/2))

                if not args.no_tracking:
                    string_message = f"{width}, {height}, {center[0]}, {center[1]}"
                    # print(servo_angle)
                    server.send_data(string_message)


        # Display the image in a window named 'Image'
        # cv2.imshow("Image", img)
        # Wait for 1 millisecond, and keep the window open
        cv2.waitKey(1)

if __name__ == "__main__":
    main()