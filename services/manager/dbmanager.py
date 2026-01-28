import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.envmanager import EnvManager

class DBManager:
    def __init__(self, this_manager: "ManagerHandler" = None):
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

        self.CHUNK = 20000  # ideal for execute_values

        self.init_database()

    def init_database(self):
        # cur.execute("SELECT version();")
        is_init = self.fetch_clean_one("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'bible';
        """)
        
        if is_init:
            # print("Database Already Initialised!")
            return 

        db_server_script_path = Path(__file__).parents[2] / "services" / "database" / "server"

        # Load and execute SQL file
        # schema_file_path = db_server_script_path / "schemas" / "v1_schema.sql"
        # with open(schema_file_path, "r") as file:
        #     sql_script = file.read()
        #     self.execute(sql_script)

        migrations = [
            db_server_script_path / "core"      / "schemas.sql",
            db_server_script_path / "core"      / "extensions.sql",
            db_server_script_path / "reference" / "licences.sql",
            db_server_script_path / "reference" / "sources.sql",
            db_server_script_path / "reference" / "files.sql",
            db_server_script_path / "reference" / "languages.sql",
            db_server_script_path / "metadata"  / "translations.sql",
            db_server_script_path / "reference" / "licence_mapping.sql",
            db_server_script_path / "bible"     / "books.sql",
            db_server_script_path / "usx"       / "nodes.sql",
            db_server_script_path / "bible"     / "chapters.sql",
            db_server_script_path / "bible"     / "verses.sql",
            db_server_script_path / "usx"       / "styles.sql",
            db_server_script_path / "usx"       / "paragraphs.sql",
            db_server_script_path / "usx"       / "footnotes.sql",
            db_server_script_path / "usx"       / "cross_references.sql",
            db_server_script_path / "user"      / "users.sql",
            db_server_script_path / "user"      / "user_data.sql",
            db_server_script_path / "metadata"  / "label_studio.sql",
            db_server_script_path / "metadata"  / "spacy_lookup.sql",
            db_server_script_path / "metadata"  / "tokens.sql",
            db_server_script_path / "reference" / "lexemes (legacy).sql",
            db_server_script_path / "reference" / "lexemes.sql",
            db_server_script_path / "entities"  / "entities.sql",
            db_server_script_path / "entities"  / "quotes.sql",
            db_server_script_path / "reference" / "morphology.sql",
            db_server_script_path / "reference" / "ingestion.sql",
            db_server_script_path / "reference" / "feature_mapping.sql",
            # db_server_script_path / "metadata"  / "chronology.sql",   # Not in Use
            # db_server_script_path / "metadata"  / "harmony.sql",      # Not in Use
            # db_server_script_path / "entities"  / "geo (legacy).sql", # Not Complete (For Bible.Info data)
            # --------------------------- SEED DATA ---------------------------
            db_server_script_path / "seed" / "language_data.sql",
            db_server_script_path / "seed" / "translation_data.sql",
            db_server_script_path / "seed" / "bible_books.sql",
            db_server_script_path / "seed" / "bible_chapters.sql",
            db_server_script_path / "seed" / "lookup_data.sql",
            db_server_script_path / "seed" / "user_data.sql",
            db_server_script_path / "seed" / "ref_lookup_data.sql",
            db_server_script_path / "seed" / "licensing_data.sql"
        ]

        for init_script_path in migrations:
            # Load and execute SQL file
            with open(init_script_path, "r", encoding="utf-8") as file:
                sql_script = file.read()
                self.execute(sql_script)
                print(f"Executed: {init_script_path.st}")

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
    
    def fetch_all_single(self, query, params=None):
        self.cur.execute(query, params)
        return [row[0] for row in self.cur.fetchall()]
    
    def set_chunks(self, new_chunk):
        self.CHUNK = new_chunk
    
    def bulk_insert(self, query, items):
        for i in range(0, len(items), self.CHUNK):
            execute_values(self.cur, query, items[i:i+self.CHUNK])
    
    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_cursor(self):
        return self.cur

    def get_connection(self):
        return self.conn