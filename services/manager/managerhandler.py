from manager.dbmanager import DBManagerFactory
from manager.envmanager import EnvManager
from manager.logmanager import LogManager
from manager.objectmanager import ObjectManager
from manager.labelmanager import LabelManager

class ManagerHandler:
    def __init__(self):
        self.logs = {}
        
        self.env = EnvManager(self)
        self.db = DBManagerFactory(self).default()
        self.obj = ObjectManager(self)
        self.label = None # LabelManager(self)

    def get_env(self):
        return self.env
    
    def get_db(self):
        return self.db
    
    def get_obj(self):
        return self.obj
    
    def get_label(self):
        return self.label

    def create_log(self, file_name):
        log_manager = LogManager(manager=self, log_file_name=file_name)
        self.logs[file_name] = log_manager
        return log_manager
    
    def create_log_in_folder(self, folders:list, file_name=None):
        log_manager = LogManager(manager=self, log_file_name=file_name, default_log_folder=folders)
        self.logs[log_manager.get_file_name()] = log_manager
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