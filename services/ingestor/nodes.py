from bs4 import BeautifulSoup
import psycopg2

from pathlib import Path
import os
from dotenv import load_dotenv

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
        break

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Will be created from books class
class Nodes:
    SQL = {
        "xml": """
            INSERT INTO bible.nodes (node_type, version, encoding) 
            VALUES ('xml', %s, %s)
            RETURNING id;
        """,
        "usx": """
            INSERT INTO bible.nodes (node_type, version) 
            VALUES ('usx', %s)
            RETURNING id;
        """,
        "book": """
            INSERT INTO bible.nodes (node_type, style, code) 
            VALUES ('book', %s, %s)
            RETURNING id;
        """,
        "chapter": """
            INSERT INTO bible.nodes (node_type, style, encoding) 
            VALUES ('chapter', %s, %s)
            RETURNING id;
        """,
        "para": """
            INSERT INTO bible.nodes (node_type, style, encoding) 
            VALUES ('para', %s, %s)
            RETURNING id;
        """,
        "verse": """
            INSERT INTO bible.nodes (node_type, style, encoding) 
            VALUES ('verse', %s, %s)
            RETURNING id;
        """,
        "note": """
            INSERT INTO bible.nodes (node_type, style, encoding) 
            VALUES ('note', %s, %s)
            RETURNING id;
        """,
        "char": """
            INSERT INTO bible.nodes (node_type, style, encoding) 
            VALUES ('char', %s, %s)
            RETURNING id;
        """,
        "ref": """
            INSERT INTO bible.nodes (node_type, style, encoding) 
            VALUES ('ref', %s, %s)
            RETURNING id;
        """,
        "text": """
            INSERT INTO bible.nodes (node_type, encoding) 
            VALUES ('text', %s, %s)
            RETURNING id;
        """,
    }
    def __init__(self, book_map_id, db_conn, book_xml):
        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        # Initialise variables 
        self.book_soup = BeautifulSoup(book_xml, "xml")
        self.book_map_id = book_map_id

        for node in self.book_soup.descendants:
            self.cur.execute(self.SQL["xml"], (None,None))

        pass

    def walk_parsed_xml(self):
        pass

if __name__ == "__main__":
    test_book_xml = None
    test_book_path = Path(__file__).parents[2] / "downloads" / "1CH.usx"
    with open(test_book_path, "r", encoding="utf-8") as f:
        test_book_xml = f.read()

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD
    )

    Nodes(None, conn, test_book_xml)