import os
import time
import zipfile
from glob import glob
from pyunpack import Archive
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ArchiveExtractor(FileSystemEventHandler):
    def extract_archive(self, file_path):
        try:
            Archive(file_path).extractall(os.path.dirname(file_path))
            print(f"Extracted: {file_path}")
        except Exception as e:
            print(f"Error extracting {file_path}: {e}")

    def process(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if zipfile.is_zipfile(file_path) or file_path.lower().endswith(('.rar')):
            self.extract_archive(file_path)

    def on_created(self, event):
        self.process(event)

    def check_existing_files(self, folder_to_monitor):
        for root, _, files in os.walk(folder_to_monitor):
            for file in files:
                file_path = os.path.join(root, file)
                if zipfile.is_zipfile(file_path) or file_path.lower().endswith(('.rar')):
                    self.extract_archive(file_path)


if __name__ == "__main__":
    # Replace this with the path to the folder you want to monitor
    folder_to_monitor = '/home/goodchoice/Desktop/Testfolder/'

    event_handler = ArchiveExtractor()
    event_handler.check_existing_files(folder_to_monitor)

    observer = Observer()
    observer.schedule(event_handler, folder_to_monitor, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
