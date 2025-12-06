from pathlib import Path
import os
import sys
import time
import datetime

from managerhandler import ManagerHandler

class LogManager():
    default_log_level = 2 # Here I can set the level of logging I want for my application

    LOG_MAPPING = {
        "TRACE": 0,
        "DEBUG": 1,
        "INFO": 2,
        "WARN": 3,
        "ERROR": 4,
        "FATAL": 5
    }

    def __init__(self, manager: ManagerHandler, default_log_path=None, default_log_folder=None, log_file_name=None, log_file_extension=".log"):
        self.main_manager = manager

        self.log_path = None
        if default_log_path != None:
            self.set_default_log_path(default_log_path)
        elif default_log_folder != None:
            self.set_default_log_folder(default_log_folder)
        else:
            self.set_default_log_folder("logs")

        self.log_file_extension = log_file_extension
        self.log_file_name = log_file_name
        
        self.log_file = self.log_path / f"{self.log_file_name}.{self.log_file_extension}"

        self.clear_log_file() # Creates Log File Ready for writing

        self.start_time = time.time()
        self.progress_message = None

        total_books = len(contents)

        # ✅ Proper loading bar (50 characters wide)
        progress = int((i / total_books) * 50)
        bar = '#' * progress + '-' * (50 - progress)
        percentage = int((i / total_books) * 100)
        
        self.progress_message = f"    Processing Books: |{bar}| {percentage}% | {found_book}"
        self.progress_message = f"\r   |{bar}| {percentage}%"

    # For choosing either setting the full log_path or just the root folder that we want to store it in
    def set_default_log_path(self, default_log_path):
        try:
            os.makedirs(default_log_path)
        except Exception as e:
            print("Log File Path Already Exists! Skipping Creation ...")
        self.log_path = default_log_path
        self.update_log_file()

    def set_default_log_folder(self, log_folder):
        default_log_path = Path(__file__).parents[2] / log_folder
        try:
            os.makedirs(default_log_path)
        except Exception as e:
            print("Log File Path Already Exists! Skipping Creation ...")
        self.log_path = default_log_path
        self.update_log_file()
    
    def update_log_file(self):
        self.log_file = self.log_path / f"{self.log_file_name}.{self.log_file_extension}"
    
    def set_default_log_extension(self, extension):
        self.log_file_extension = extension
        self.update_log_file()

    def set_log_file_name(self, new_log_file_name):
        self.log_file_name = new_log_file_name
        self.update_log_file()

    def delete_log_file(self):
        pass

    def clear_log_file(self):
        with open(self.log_file, 'w', encoding="utf-8") as f:
            f.write("")

    def create_log_file(self):
        pass

    def set_logging_level(self):
        pass

    def update_progress_bar(self):
        pass

    def complete_progress_bar(self):
        pass

    def log_to_console(self):
        pass
    
    def elapsed_time(self, is_accurate=False):
        if is_accurate == False:
            duration = time.time() - self.start_time
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)

            formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
            return formatted_duration
        else:
            duration = time.time() - self.start_time
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            milliseconds = int((duration % 1) * 1000)  # or *100 for .mm format

            formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
            return formatted_duration

    def log_to_file(self, log_message, source_class, log_level):
        # Always update CLI progress bar, just only conditionally log
        if self.progress_message != None and hasattr(sys.stdout, "write"):
            sys.stdout.write(f"\r{self.progress_message} | [Elapsed: {self.elapsed_time()}] | ")
            sys.stdout.flush()

        if self.LOG_MAPPING[log_level] < self.default_log_level:
            return

        with open(self.log_file, 'a', encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} [{log_level}] [Elapsed: {self.elapsed_time()}] [{source_class}] {log_message}\n")

if __name__ == "__main__":
    pass