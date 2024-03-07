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

while True:
    angle = 90 + 90 * np.sin(time.time())
    print(angle)
    kit.servo[0].angle = angle

pid = PID(kp=0.1, ki=0.1, kd=0.01, setpoint=320)

face_x = 320
last_pid_angle = 90

def periodic_handler():
    """Function to be called periodically."""
    pid_angle = 90 - np.clip(pid.update(face_x, 0.01), -90, 90)
    # low pass
    global last_pid_angle
    alpha = 0.5
    pid_angle = alpha * pid_angle + (1 - alpha) * last_pid_angle
    print(f"{face_x}, {pid_angle}")
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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            print("Connected to server.")
            servo_1_angle = 90
            servo_2_angle = 90
            start_periodic_handler(0.01)
            while True:
                kit.servo[1].angle = servo_1_angle
                kit.servo[2].angle = servo_2_angle
                data = sock.recv(1024)  # Buffer size of 1024 bytes
                if not data:
                    print("Connection closed by server.")
                    break
                # print("Received:", data.decode('utf-8'))
                global face_x
                width = float(data.decode('utf-8').split(",")[0])
                height = float(data.decode('utf-8').split(",")[1])
                face_x = float(data.decode('utf-8').split(",")[2])
                face_y = float(data.decode('utf-8').split(",")[3])

                # control_gain = 0.8

                # servo_1_angle = 90 + (camera_delta * control_gain)
                # servo_2_angle = 90 + (camera_delta_y * control_gain)
                # servo_1_angle = np.clip(servo_1_angle, 0, 180)
                # servo_2_angle = np.clip(servo_2_angle, 0, 180)

                servo_1_angle = map(face_x, 0, width, 0, 180)
                servo_2_angle = map(face_y, 0, height, 0, 180)
                kit.servo[1].angle = servo_1_angle
                kit.servo[2].angle = servo_2_angle
                # print(f"{servo_1_angle}, {servo_2_angle}")

                head_delta = (servo_1_angle - 90)

                control_gain_base = 0.1
                servo_0_angle = 90 + (head_delta * control_gain_base)
                servo_0_angle = np.clip(servo_0_angle, 0, 180)
                # print(servo_0_angle)
                # pid_angle = np.clip(pid.update(face_x, 0.01), 0, 180)
                # print(pid_angle)
                # kit.servo[0].angle = pid_angle

if __name__ == "__main__":
    client = Client()
    client.start()

# SLEEP_TIME = 0.01



# # 

# while True:
# #     # for i in range(75, 130):
# #     #     print(i)
# #     #     kit.servo[1].angle = i
# #     #     time.sleep(SLEEP_TIME)
    
# #     # for i in range(130, 75, -1):
# #     #     print(i)
# #     #     kit.servo[1].angle = i
# #     #     time.sleep(SLEEP_TIME)

# #     # for i in range(90, 180):
# #     #     print(i)
# #     #     kit.servo[2].angle = i
# #     #     time.sleep(SLEEP_TIME)
    
# #     # for i in range(180, 60, -1):
# #     #     print(i)
# #     #     kit.servo[2].angle = i
# #     #     time.sleep(SLEEP_TIME)

#     for i in range(0, 180):
#         print(i)
#         # if i >=90 and i <=180:
#         kit.servo[0].angle = i
#         time.sleep(SLEEP_TIME)
#         # if i >=75 and i <=130:
#         #     kit.servo[1].angle = i
#         #     time.sleep(SLEEP_TIME)
    
#     for i in range(180, 0, -1):
#         print(i)
#         # if i >=90 and i <=180:
#         kit.servo[0].angle = i
#         time.sleep(SLEEP_TIME)
#         # if i >=75 and i <=130:
#         #     kit.servo[1].angle = i
#         #     time.sleep(SLEEP_TIME)
    