import os
import time
import zipfile
from glob import glob
from pyunpack import Archive
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import PySimpleGUI as sg
import threading


class ArchiveExtractor(FileSystemEventHandler):
    # ... (same as your original script)

    def on_created(self, event):
        self.process(event)

    def check_existing_files(self, folder_to_monitor, window):
        for root, _, files in os.walk(folder_to_monitor):
            for file in files:
                file_path = os.path.join(root, file)
                if zipfile.is_zipfile(file_path) or file_path.lower().endswith(('.rar')):
                    self.extract_archive(file_path, window)

    def extract_archive(self, file_path, window=None):
        # ... (same as your original script)
        if window:
            window.write_event_value("extracted", file_path)


def run_finished_download_handler(folder_to_monitor, window):
    event_handler = ArchiveExtractor()
    event_handler.check_existing_files(folder_to_monitor, window)

    observer = Observer()
    observer.schedule(event_handler, folder_to_monitor, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    # Define the layout for the GUI
    layout = [
        [sg.Text("Select folder to monitor:")],
        [sg.Input(), sg.FolderBrowse()],
        [sg.Button("Start"), sg.Button("Exit")],
        [sg.Output(size=(80, 20), key="output")]
    ]

    # Create the window using the layout
    window = sg.Window("FinishedDownloadHandler", layout, finalize=True)

    # Event loop to process user input
    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "Start":
            folder_to_monitor = values[0]
            if folder_to_monitor:
                # Run the FinishedDownloadHandler in a separate thread
                handler_thread = threading.Thread(
                    target=run_finished_download_handler, args=(folder_to_monitor, window))
                handler_thread.start()

        if event == "extracted":
            file_path = values["extracted"]
            print(f"Extracted: {file_path}")

    # Close the window
    window.close()
