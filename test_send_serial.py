#!/usr/bin/env python3
import serial
import time

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    ser.reset_input_buffer()

    while True:
        for i in range(8):
            for j in range(16):
                data = f"{i}, {j}\n"
                ser.write(data.encode('utf-8'))
                time.sleep(0.1)