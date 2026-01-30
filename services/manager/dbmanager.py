import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from contextlib import contextmanager
from manager.queryboundary import QueryBoundary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.envmanager import EnvManager

class DBManager:
    def __init__(self, role: str, this_manager: "ManagerHandler" = None):
        self.this_manager = this_manager
        self.env = None
        if this_manager == None:
            self.env = EnvManager()
        else:
            self.env = self.this_manager.get_env()

        self.role = role
        config = self.env.get_postgres_config(role)
        self.conn = psycopg2.connect(**config)

        # Adds a database connection
        # self.conn = psycopg2.connect(
        #     host=config["host"],
        #     port=config["port"],
        #     dbname=config["database"],
        #     user=config["username"],
        #     password=config["password"]
        # )

        self.query_boundary = QueryBoundary(self)

        self.CHUNK = 20000  # ideal for execute_values

        self.init_database()

    def get_query_boundary(self):
        return self.query_boundary

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

        schema_folder   = "schemas"
        seed_folder     = "seed"

        migrations = [
            db_server_script_path / schema_folder / "core"      / "schemas.sql",
            db_server_script_path / schema_folder / "core"      / "extensions.sql",
            db_server_script_path / schema_folder / "reference" / "licences.sql",
            db_server_script_path / schema_folder / "reference" / "sources.sql",
            db_server_script_path / schema_folder / "reference" / "files.sql",
            db_server_script_path / schema_folder / "reference" / "languages.sql",
            db_server_script_path / schema_folder / "reference" / "translations.sql",
            db_server_script_path / schema_folder / "reference" / "licence_mapping.sql",
            db_server_script_path / schema_folder / "bible"     / "books.sql",
            db_server_script_path / schema_folder / "reference" / "lexemes (legacy).sql",
            db_server_script_path / schema_folder / "reference" / "lexemes.sql",
            db_server_script_path / schema_folder / "usx"       / "nodes.sql",
            db_server_script_path / schema_folder / "bible"     / "chapters.sql",
            db_server_script_path / schema_folder / "bible"     / "verses.sql",
            db_server_script_path / schema_folder / "usx"       / "styles.sql",
            db_server_script_path / schema_folder / "usx"       / "paragraphs.sql",
            db_server_script_path / schema_folder / "usx"       / "footnotes.sql",
            db_server_script_path / schema_folder / "usx"       / "cross_references.sql",
            db_server_script_path / schema_folder / "user"      / "users.sql",
            db_server_script_path / schema_folder / "user"      / "user_data.sql",
            db_server_script_path / schema_folder / "metadata"  / "label_studio.sql",
            db_server_script_path / schema_folder / "metadata"  / "spacy_lookup.sql",
            db_server_script_path / schema_folder / "reference" / "tokens.sql",
            db_server_script_path / schema_folder / "entities"  / "entities.sql",
            db_server_script_path / schema_folder / "entities"  / "quotes.sql",
            db_server_script_path / schema_folder / "reference" / "morphology.sql",
            db_server_script_path / schema_folder / "metadata"  / "ingestion.sql",
            db_server_script_path / schema_folder / "metadata" / "feature_mapping.sql",
            # db_server_script_path / "metadata"  / "chronology.sql",   # Not in Use
            # db_server_script_path / "metadata"  / "harmony.sql",      # Not in Use
            # db_server_script_path / "entities"  / "geo (legacy).sql", # Not Complete (For Bible.Info data)
            # --------------------------- SEED DATA ---------------------------
            db_server_script_path / seed_folder / "language_data.sql",
            db_server_script_path / seed_folder / "translation_data.sql",
            db_server_script_path / seed_folder / "bible_books.sql",
            db_server_script_path / seed_folder / "bible_chapters.sql",
            db_server_script_path / seed_folder / "lookup_data.sql",
            db_server_script_path / seed_folder / "user_data.sql",
            db_server_script_path / seed_folder / "ref_lookup_data.sql",
            db_server_script_path / seed_folder / "licensing_data.sql"
        ]

        for init_script_path in migrations:
            # Load and execute SQL file
            with open(init_script_path, "r", encoding="utf-8") as file:
                sql_script = file.read()
                self.execute(sql_script)
                print(f"Executed: {init_script_path.parent.name}.{init_script_path.name}")

        self.conn.commit()

        print("Database Init Success")

    def execute(self, query, params=None):
        # Adds transaction control / handling + Error handling and rollback
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def fetch_clean_one(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return result[0] if result else None
    
    def fetch_one(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
    
    def fetch_all(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    
    def fetch_all_single(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return [row[0] for row in cur.fetchall()]
    
    def set_chunks(self, new_chunk):
        self.CHUNK = new_chunk
    
    def bulk_insert(self, query, items):
        try:
            with self.conn.cursor() as cur:
                for i in range(0, len(items), self.CHUNK):
                    execute_values(cur, query, items[i:i+self.CHUNK])
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    # def get_connection(self):
    #     return self.conn

    # Allows rolling back a sequence of operations if needed, instead of just the one that failed
    #   prevent half imports and incomplete data in db
    @contextmanager
    def transaction(self):
        try:
            yield self
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

class DBManagerFactory:
    def __init__(self, this_manager: "ManagerHandler" = None):
        self.this_manager = this_manager

    def default(self):
        return DBManager(None, self.this_manager)

    def reader(self):
        return DBManager("reader", self.this_manager)

    def writer(self):
        return DBManager("writer", self.this_manager)

    def usx_ingestor(self):
        return DBManager("usx_ingestor", self.this_manager)

    def admin(self):
        return DBManager("admin", self.this_manager)