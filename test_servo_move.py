from adafruit_servokit import ServoKit
import threading
import time
import socket
import numpy as np
from pid_controller import PID

kit = ServoKit(channels=16)
kit.servo[0].angle = 90
kit.servo[1].angle = 90
kit.servo[2].angle = 90

pid = PID(kp=0.1, ki=0.2, kd=0.0, setpoint=320)

face_x = 320
last_pid_angle = 90
server_connected = False
last_server_connected = False

def periodic_handler():
    """Function to be called periodically."""
    # low pass
    global last_pid_angle
    
    # print(f"{face_x}, {pid_angle}")
    # global last_server_connected
    # pid_angle = last_pid_angle

    # print(f"last_server_connected: {last_server_connected}")
    # print(f"server_connected: {server_connected}")
    # if last_server_connected and not server_connected:
    #     print("no server")
    #     pid.clear()
    #     # last_server_connected = False
    #     print(f"no server angle {pid_angle}")
    # else:
    #     print("pid")
    pid_angle = 90 - np.clip(pid.update(face_x, 0.01), -90, 90)
    alpha = 0.1
    pid_angle = alpha * pid_angle + (1 - alpha) * last_pid_angle
    kit.servo[0].angle = pid_angle
    last_pid_angle = pid_angle

def start_periodic_handler(interval):
    """Starts the periodic handler with the specified interval."""
    threading.Timer(interval, start_periodic_handler, args=[interval]).start()
    periodic_handler()

def map(x, xlow, xhigh, ylow, yhigh):
    """Map an array of values x from range [xlow, xhigh] to [ylow, yhigh] using NumPy."""
    y = ylow + (x - xlow) * (yhigh - ylow) / (xhigh - xlow)
    return y

class Client:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port

    def start(self):
        print("looking for server")
        global server_connected
        server_connected = False
        start_periodic_handler(0.01)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                server_connected = True
                sock.settimeout(5)
                sock.connect((self.host, self.port))
                print("Connected to server.")
                global last_server_connected
                last_server_connected = True
                servo_1_angle = 90
                servo_2_angle = 90
                while True:
                    data = sock.recv(1024)  # Buffer size of 1024 bytes
                    if not data:
                        print("Connection closed by server.")
                        self.start()
                        break
                    # print("Received:", data.decode('utf-8'))
                    global face_x
                    width = float(data.decode('utf-8').split(",")[0])
                    height = float(data.decode('utf-8').split(",")[1])
                    face_x = float(data.decode('utf-8').split(",")[2])
                    face_y = float(data.decode('utf-8').split(",")[3])

                    servo_1_angle = map(face_x, 0, width, 0, 180)
                    servo_2_angle = map(face_y, 0, height, 0, 180)
                    kit.servo[1].angle = servo_1_angle
                    kit.servo[2].angle = servo_2_angle

        except socket.error as e:
            time.sleep(1)
            self.start()

if __name__ == "__main__":
    client = Client()
    client.start()
