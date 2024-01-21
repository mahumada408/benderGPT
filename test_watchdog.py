import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

        with open(file_path, 'r') as file:
            print(file.read())

        os.remove(file_path)
        print(f"File deleted: {file_path}")

if __name__ == '__main__':
    # Set the directory you want to monitor
    watch_directory = "/home/benderpi/bender_in_out/"
    w = Watcher(watch_directory)
    w.run()
