from envmanager import EnvManager
import psycopg2
from psycopg2.extras import execute_values

class DBManager:
    def __init__(self):
        self.env = EnvManager()

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