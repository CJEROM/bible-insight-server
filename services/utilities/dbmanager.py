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

    def execute(self, query, params=None):
        self.cur.execute(query, params)
        self.conn.commit()

    def fetch_clean_one(self, query, params=None):
        self.cur.execute(query, params)
        result = self.cur.fetchone()

        if result != None:
            return result[0]
        
        return result
    
    def fetch_one(self, query, params=None):
        self.cur.execute(query, params)
        return self.cur.fetchone()
    
    def fetch_all(self, query, params=None):
        self.cur.execute(query, params)
        return self.cur.fetchall()
    
    def db_commit(self):
        self.conn.commit()

    def db_close(self):
        self.conn.close()

    def get_cursor(self):
        self.cur

    def get_connection(self):
        self.conn