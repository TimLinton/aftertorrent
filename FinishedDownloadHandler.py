import os
import time
import zipfile
from glob import glob
from pyunpack import Archive
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import PySimpleGUI as sg
import threading
import json
import os
from tkinter import Tk, Label, Text, Scrollbar, VERTICAL


def read_download_rules():
    rules_path = os.path.expanduser(
        "~/.config/qBittorrent/rss/download_rules.json")
    with open(rules_path, 'r') as f:
        rules = json.load(f)
    return rules


def simplify_rules(rules):
    simplified_rules = []
    for rule_name, rule_data in rules.items():
        simplified_rule = {
            'name': rule_name,
            'assignedCategory': rule_data['assignedCategory'],
            'savePath': rule_data['savePath']
        }
        simplified_rules.append(simplified_rule)
    return simplified_rules


def display_rules_in_textbox(rules, textbox):
    for rule in rules:
        rule_text = f"Name: {rule['name']}\nAssigned Category: {rule['assignedCategory']}\nSave Path: {rule['savePath']}\n\n"
        textbox.insert('end', rule_text)


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

    def on_created(self, event):
        self.process(event)

    def check_existing_files(self, folder_to_monitor, window=None):
        for root, _, files in os.walk(folder_to_monitor):
            for file in files:
                file_path = os.path.join(root, file)
                if zipfile.is_zipfile(file_path) or file_path.lower().endswith(('.rar')):
                    self.extract_archive(file_path)

    def extract_archive(self, file_path, window=None):
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
    rss_list = sg.Multiline('', size=(50, 20), key="rss_list")
    output_log = sg.Output(size=(80, 20), key="output")

    layout = [
        [sg.Text("Select folder to monitor:")],
        [sg.Input(), sg.FolderBrowse()],
        [sg.Button("Start"), sg.Button("Exit")],
        [
            sg.Column([[rss_list]], element_justification="left"),
            sg.Column([[output_log]], element_justification="right")
        ]
    ]

    # Create the window using the layout
    window = sg.Window("FinishedDownloadHandler", layout, finalize=True)

    # Display rules in the textbox
    rules = read_download_rules()
    simplified_rules = simplify_rules(rules)
    for rule in simplified_rules:
        rule_text = f"Name: {rule['name']}\nAssigned Category: {rule['assignedCategory']}\nSave Path: {rule['savePath']}\n\n"
        window['rss_list'].print(rule_text)

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
