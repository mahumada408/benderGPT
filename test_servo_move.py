from adafruit_servokit import ServoKit
import time
import socket

kit = ServoKit(channels=16)
kit.servo[0].angle = 90

class Client:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            print("Connected to server.")
            while True:
                data = sock.recv(1024)  # Buffer size of 1024 bytes
                if not data:
                    print("Connection closed by server.")
                    break
                print("Received:", data.decode('utf-8'))
                camera_delta = float(data.decode('utf-8').split(",")[0])
                camera_delta_y = float(data.decode('utf-8').split(",")[1])
                control_gain = 0.2
                kit.servo[1].angle = 90 + (camera_delta * control_gain)
                kit.servo[2].angle = 90 + (camera_delta_y * control_gain)

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
    