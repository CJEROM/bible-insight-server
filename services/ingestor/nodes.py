from bs4 import BeautifulSoup, Tag, NavigableString
import psycopg2
import sys
import time

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
            INSERT INTO bible.nodes (node_type, style, number, sid, eid) 
            VALUES ('chapter', %s, %s, %s, %s)
            RETURNING id;
        """,
        "para": """
            INSERT INTO bible.nodes (node_type, style, vid) 
            VALUES ('para', %s, %s)
            RETURNING id;
        """,
        "verse": """
            INSERT INTO bible.nodes (node_type, style, number, sid, eid) 
            VALUES ('verse', %s, %s, %s, %s)
            RETURNING id;
        """,
        "note": """
            INSERT INTO bible.nodes (node_type, style, caller) 
            VALUES ('note', %s, %s)
            RETURNING id;
        """,
        "char": """
            INSERT INTO bible.nodes (node_type, style, closed, strong) 
            VALUES ('char', %s, %s, %s)
            RETURNING id;
        """,
        "ref": """
            INSERT INTO bible.nodes (node_type, loc) 
            VALUES ('ref', %s)
            RETURNING id;
        """,
        "text": """
            INSERT INTO bible.nodes (node_type, node_text) 
            VALUES ('text', %s)
            RETURNING id;
        """,
        "update_node": """
            UPDATE bible.nodes
            SET parent_node_id = %s,
                index_in_parent = %s,
                book_map_id = %s,
                canonical_path = %s
            WHERE id = %s;
        """,
    }

    def __init__(self, book_map_id, db_conn, book_xml):
        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        # Initialise variables 
        self.book_soup = BeautifulSoup(book_xml, "xml")
        self.book_map_id = book_map_id

        self.walk_parsed_xml()
            
        self.conn.commit()
    
    def execute_and_get_id(self, query, params):
        self.cur.execute(query, params)
        return self.cur.fetchone()[0]
    
    def walk_parsed_xml(self):
        nodes_to_create = len(list(self.book_soup.descendants))

        start_time = time.time()

        # Used to keep track of what chapter, paragraph and verse we are in, and their node_id
        chapter_node_id = None
        paragraph_node_id = None
        verse_node_id = None

        for i, node in enumerate(self.book_soup.descendants):
            node_id = None # Initialise node_id for the note we are going to create in DB

            if isinstance(node, Tag):
                query = self.SQL.get(node.name)
                match node.name:
                    case "xml":
                        version = node.get("version")
                        encoding = node.get("encoding")

                        node_id = self.execute_and_get_id(query, (version, encoding))
                    case "usx":
                        version = node.get("version")

                        node_id = self.execute_and_get_id(query, (version,))
                    case "book":
                        style = node.get("style")
                        code = node.get("code")

                        node_id = self.execute_and_get_id(query, (style, code))
                    case "chapter":
                        style = node.get("style")
                        number = node.get("number")
                        sid = node.get("sid")
                        eid = node.get("eid")

                        node_id = self.execute_and_get_id(query, (style, number, sid, eid))

                        # Update what chapter we are in
                        if sid != None:
                            chapter_node_id = node_id
                        elif eid != None:
                            chapter_node_id = None
                    case "para":
                        style = node.get("style")
                        vid = node.get("vid")
                        node_id = self.execute_and_get_id(query, (style, vid))

                        # Update what para we are in
                        paragraph_node_id = node_id
                    case "verse":
                        style = node.get("style")
                        number = node.get("number")
                        sid = node.get("sid")
                        eid = node.get("eid")

                        node_id = self.execute_and_get_id(query, (style, number, sid, eid))

                        # Update what verse we are in
                        if sid != None:
                            verse_node_id = node_id
                        elif eid != None:
                            verse_node_id = None
                    case "note":
                        style = node.get("style")
                        caller = node.get("caller")

                        node_id = self.execute_and_get_id(query, (style, caller))
                    case "char":
                        style = node.get("style")
                        closed = node.get("closed")
                        strong = node.get("strong")

                        node_id = self.execute_and_get_id(query, (style, closed, strong))
                    case "ref":
                        loc = node.get("loc")

                        node_id = self.execute_and_get_id(query, (loc,))

            if isinstance(node, NavigableString):  
                node_text = str(node)
                node_id = self.execute_and_get_id(self.SQL.get("text"), (node_text,))

                # Logic to differentiate whether this is versetext or not

                # if it is insert into bible.text_nodes table to show its relevant

                # Then throw in tokens pipeline, linked to node, but extend to verse for example to hold. or paragraph as well

            # Do something with node_id's?
            parent_node_id = None
            index_in_parent = None
            canonical_path = None
            self.cur.execute(self.SQL.get("update_node"), (parent_node_id, index_in_parent, self.book_map_id, canonical_path, node_id))

            # Loading bar with elapsed time
            duration = time.time() - start_time
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)

            formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

            progress = int((i / nodes_to_create) * 50)
            bar = '#' * progress + '-' * (50 - progress)
            percentage = int((i / nodes_to_create) * 100)
            sys.stdout.write(f"\rProcessing books: |{bar}| {percentage}% | Elapsed: {formatted_duration} | ")
            sys.stdout.flush()

if __name__ == "__main__":
    test_book_xml = None
    # test_book_path = Path(__file__).parents[2] / "downloads" / "1CH - WMBBE.usx"
    # test_book_path = Path(__file__).parents[2] / "downloads" / "PSA - WMBBE.usx"
    test_book_path = Path(__file__).parents[2] / "downloads" / "3JN - FBV.usx"
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