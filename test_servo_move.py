from adafruit_servokit import ServoKit
import time
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

data = client_socket.recv(1024)  # Buffer size
boolean_value, float_value = data.decode().split(",")
boolean_value = boolean_value == 'True'
float_value = float(float_value)

client_socket.close()

SLEEP_TIME = 0.01

kit = ServoKit(channels=16)

# kit.servo[0].angle = 90

while True:
#     # for i in range(75, 130):
#     #     print(i)
#     #     kit.servo[1].angle = i
#     #     time.sleep(SLEEP_TIME)
    
#     # for i in range(130, 75, -1):
#     #     print(i)
#     #     kit.servo[1].angle = i
#     #     time.sleep(SLEEP_TIME)

#     # for i in range(90, 180):
#     #     print(i)
#     #     kit.servo[2].angle = i
#     #     time.sleep(SLEEP_TIME)
    
#     # for i in range(180, 60, -1):
#     #     print(i)
#     #     kit.servo[2].angle = i
#     #     time.sleep(SLEEP_TIME)

    for i in range(0, 180):
        print(i)
        # if i >=90 and i <=180:
        kit.servo[0].angle = i
        time.sleep(SLEEP_TIME)
        # if i >=75 and i <=130:
        #     kit.servo[1].angle = i
        #     time.sleep(SLEEP_TIME)
    
    for i in range(180, 0, -1):
        print(i)
        # if i >=90 and i <=180:
        kit.servo[0].angle = i
        time.sleep(SLEEP_TIME)
        # if i >=75 and i <=130:
        #     kit.servo[1].angle = i
        #     time.sleep(SLEEP_TIME)
    