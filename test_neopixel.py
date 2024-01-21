import board
import neopixel
import time
import json
import argparse
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import fcntl

# Configuration for the NeoPixel strip
PIN = board.D18  # The pin that the NeoPixel is connected to
ROWS = 8
COLUMNS = 16
NUM_PIXELS = ROWS * COLUMNS  # Number of pixels (7 rows x 16 columns)
BRIGHTNESS = 0.5  # Brightness level, range from 0.0 to 1.0

# Create the NeoPixel object
pixels = neopixel.NeoPixel(PIN, NUM_PIXELS, auto_write=False, brightness=0.01)

def set_pixel(row, col, color):
    """
    Calculate the LED index for the given row and column.

    Args:
    row (int): The row number (0-indexed).
    col (int): The column number (0-indexed).

    Returns:
    int: The index of the LED in the strip.
    """
    if col % 2 == 0:
        # For even columns, the index increases from top to bottom
        index = col * ROWS + row
    else:
        # For odd columns, the index increases from bottom to top
        index = col * ROWS + (ROWS - 1 - row)
    
    print(index)
    pixels[index] = color

def show():
    """Update the display with the data from the pixel buffer."""
    pixels.show()

def clear():
    """Clear the display."""
    pixels.fill((0, 0, 0))
    show()

def read_json_file(file_path):
    """
    Reads a JSON file and returns the data.

    Args:
    file_path (str): The path to the JSON file.

    Returns:
    dict: The data contained in the JSON file.
    """
    try:
        with open(file_path, 'r') as file:
            # Acquire an exclusive lock
            fcntl.flock(file, fcntl.LOCK_EX)

            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error reading the JSON file: {e}")
        return None

class Watcher:
    def __init__(self, directory_to_watch):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        # This function is called when a file is created
        if event.is_directory:
            return None

        # Reading and then deleting the file
        file_path = event.src_path
        print(f"File created: {file_path}")

        data = read_json_file(file_path)
        if data is not None:
            clear()
            print(data)
            for pixel in data['waveform_data']:
                print(pixel)
                set_pixel(pixel[0], pixel[1], (255, 255, 0))
            show()

        os.remove(file_path)
        print(f"File deleted: {file_path}")

def main():
    # Set the directory you want to monitor
    watch_directory = "/home/benderpi/bender_in_out/"
    w = Watcher(watch_directory)
    w.run()
    # data = read_json_file(args.file_path)
    
    # if data is not None:
    #     print(data)
    #     for pixel in data['waveform_data']:
    #         print(pixel)
    #         set_pixel(pixel[0], pixel[1], (255, 255, 0))
    #     show()

if __name__ == "__main__":
    main()