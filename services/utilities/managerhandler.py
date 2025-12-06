from logmanager import LogManager

class ManagerHandler:
    def __init__(self):
        self.logs = {}
        pass

    def create_log(self, file_name):
        self.logs[file_name] = LogManager(log_file_name=file_name)

    def return_log(self, file_name):
        requested_log = self.logs.get(file_name)

        if requested_log == None:
            print("No Log with that ID found")
            return
        else:
            return requested_log

if __name__ == "__main__":
    pass