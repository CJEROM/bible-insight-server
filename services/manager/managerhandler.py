from manager.dbmanager import DBManager
from manager.envmanager import EnvManager
from manager.logmanager import LogManager
from manager.objectmanager import ObjectManager

class ManagerHandler:
    def __init__(self):
        self.logs = {}
        
        self.env = EnvManager(self)
        self.db = DBManager(self)
        self.obj = ObjectManager(self)

    def get_env(self):
        return self.env
    
    def get_db(self):
        return self.db
    
    def get_obj(self):
        return self.obj

    def create_log(self, file_name):
        log_manager = LogManager(manager=self, log_file_name=file_name)
        self.logs[file_name] = log_manager
        return log_manager
    
    def create_log_in_folder(self, file_name, folders:list):
        log_manager = LogManager(manager=self, log_file_name=file_name, default_log_folder=folders)
        self.logs[file_name] = log_manager
        return log_manager

    def return_log(self, file_name):
        requested_log = self.logs.get(file_name)

        if requested_log == None:
            print("No Log with that ID found")
            return
        else:
            return requested_log

if __name__ == "__main__":
    pass