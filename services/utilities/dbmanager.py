from envmanager import EnvManager
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

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

        self.init_database()

    def init_database(self):
        # cur.execute("SELECT version();")
        is_init = self.fetch_clean_one("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """, ("languages",))
        
        if is_init:
            print("Database Already Initialised!")
            return 

        db_server_script_path = Path(__file__).parents[2] / "services" / "database" / "server"

        # Load and execute SQL file
        schema_path = db_server_script_path / "schemas" / "v1_schema.sql"
        with open(schema_path, "r") as file:
            sql_script = file.read()
            self.execute(sql_script)

        migrations = [
            "001_init_translations.sql",
            "001_init_bible.sql",
            "001_init_lookup.sql"
        ]

        for init_script in migrations:
            init_script_path = db_server_script_path / "migrations" / init_script
            # Load and execute SQL file
            with open(init_script_path, "r", encoding="utf-8") as file:
                sql_script = file.read()
                self.execute(sql_script)

        self.commit()

        print("Database Init Success")

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
    
    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_cursor(self):
        return self.cur

    def get_connection(self):
        return self.conn