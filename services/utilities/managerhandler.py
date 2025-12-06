from dbmanager import DBManager
from envmanager import EnvManager
from logmanager import LogManager
from objectmanager import ObjectManager

class ManagerHandler:
    def __init__(self):
        self.logs = {}
        
        self.env = EnvManager()
        self.db = DBManager()
        self.obj = ObjectManager()

    def get_env(self):
        return self.env
    
    def get_db(self):
        return self.db
    
    def get_obj(self):
        return self.obj

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