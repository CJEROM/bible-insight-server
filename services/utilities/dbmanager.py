from envmanager import EnvManager
import psycopg2
from psycopg2.extras import execute_values

from managerhandler import ManagerHandler

class DBManager:
    def __init__(self, this_manager: ManagerHandler = None):
        self.this_manager = this_manager
        self.env = None
        if this_manager == None:
            self.env = EnvManager()
        else:
            self.env = self.this_manager.get_env()

        config = self.env.get_postgres_config()

        # Adds a database connection
        self.conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            dbname=config["database"],
            user=config["username"],
            password=config["password"]
        )

        self.cur = self.conn.cursor()

        self.conn.commit()
        self.conn.close()