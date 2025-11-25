from bs4 import BeautifulSoup, Tag, NavigableString
import psycopg2
from psycopg2.extras import execute_values

from pathlib import Path
import os
from dotenv import load_dotenv

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from translation import Translation
    from book import Book

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
        "new_node": """
            INSERT INTO bible.nodes (node_text, node_type, code, sid, eid, vid, style, number, caller, closed, version, strong, loc, parent_node_id, index_in_parent, book_map_id, canonical_path) 
            VALUES %s;
        """,
        "node_count": """
            SELECT COUNT(*) FROM bible.nodes;
        """
    }

    def __init__(self, this_translation: "Translation", this_book: "Book", db_conn, book_xml):
        self.this_translation = this_translation
        self.this_book = this_book

        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        # Initialise variables 
        self.book_soup = BeautifulSoup(book_xml, "xml")
        self.book_map_id = self.this_book.get_book_map_id()

        self.created_nodes = {
            "chapter": {},
            "verse": {},
            "para": {},
            "note": {}
        }
        
        self.walk_parsed_xml()
            
        self.conn.commit()
    
    def walk_parsed_xml(self):
        node_id_map = {}    # maps bs4 node → SQL node_id
        child_index = {}    # parent → next child index
        path_map = {}       # bs4 node → canonical path

        all_new_nodes = []

        self.cur.execute(self.SQL.get("node_count"))
        node_id_offset = self.cur.fetchone()[0]

        node_id_counter = 1

        node_chapter_ref = self.this_book.get_book_code() + " 1"

        for node in self.book_soup.descendants:
            # Initialise node_id for the note we are going to create in DB
            node_id = node_id_counter + node_id_offset # since i will be 0, want to start at 1 instead + offset from database to say this new node is
            node_type = None
            
            this_node = [None] * 17 # create mutable list of length 17

            if isinstance(node, Tag):
                node_type =     node.name

                this_node[1] =  node_type # node_type, 1
                this_node[2] =  node.get("code") # code, 2
                sid =           node.get("sid")
                this_node[3] =  sid # sid, 3
                eid =           node.get("eid")
                this_node[4] =  eid # eid, 4
                this_node[5] =  node.get("vid") # vid, 5
                this_node[6] =  node.get("style") # style, 6 
                this_node[7] =  node.get("number") # number, 7
                this_node[8] =  node.get("caller") # caller, 8
                this_node[9] =  node.get("closed") # closed, 9
                this_node[10] = node.get("version") # version, 10
                strong =        node.get("strong")
                this_node[11] = strong # strong, 11
                this_node[12] = node.get("loc") # loc, 12

                # Consider creating init for all strongs numbers instead
                if strong != None:
                    self.createStrongs(strong)

            if isinstance(node, NavigableString):  
                node_type = "text"

                this_node[0] = str(node) # node_text, 0
                this_node[1] = node_type # node_type, 1

            # ------ Skip empty nodes
            if all(x is None for x in this_node):
                continue

            # ------ Parent & child index tracking
            node_id_map[id(node)] = node_id # add to node_map

            # With mapped id, find parent and get associated node_id
            parent_obj = node.parent
            parent_node_id = None
            index_in_parent = None

            # if has a parent (only xml and usx will not)
            if parent_obj:
                # get node_id map for parsed xml
                parent_node_id = node_id_map.get(id(parent_obj))

                # also increment and set count for child index under that parent
                if id(parent_obj) not in child_index:
                    child_index[id(parent_obj)] = 0
                index_in_parent = child_index[id(parent_obj)]
                child_index[id(parent_obj)] += 1
            else:
                index_in_parent = None

            # ------ Build Canonical Path
            parent_path = path_map.get(id(parent_obj), "") # if not exists, gives empty string

            new_path = f"/{node_type}:{index_in_parent}" 
            canonical_path = parent_path + new_path
            path_map[id(node)] = canonical_path

            # Update the rest of the node parts that required more processing
            this_node[13] = parent_node_id # parent_node_id, 13
            this_node[14] = index_in_parent # index_in_parent, 14
            this_node[15] = self.book_map_id # book_map_id, 15
            this_node[16] = canonical_path # canonical_path, 16 

            # Prepare for next node, and add for bulk insert
            all_new_nodes.append(tuple(this_node))
            node_id_counter += 1

            self.this_translation.log_ingestion_activity(f"Created New Node: {this_node}", f"[NODE:{node_type}]", "INFO")

            # Add to dictionary to show start and end nodes for chapters or verse
            if node_type in ["chapter", "verse"]:
                if sid != None:
                    self.created_nodes[node_type][sid] = {}
                    self.created_nodes[node_type][sid]["sid"] = node_id
                    if node_type == "chapter":
                        node_chapter_ref = sid
                elif eid != None:
                    self.created_nodes[node_type][eid]["eid"] = node_id
            # Add to dictionary to show node_id for para or note
            elif node_type in ["para", "note"]:
                print(node_type, self.created_nodes[node_type])
                # Check if need to inialise for chapter
                if self.created_nodes[node_type] == {}:
                    self.created_nodes[node_type][node_chapter_ref] = []
                elif self.created_nodes[node_type].get(node_chapter_ref) == None:
                    self.created_nodes[node_type][node_chapter_ref] = []

                self.created_nodes[node_type][node_chapter_ref].append(node_id)

        # Now bulk insert all of the nodes into the database (in batches / chunks)
        CHUNK = 20000  # ideal for execute_values

        sql_query = self.SQL.get("new_node")
        for i in range(0, len(all_new_nodes), CHUNK):
            execute_values(self.cur, sql_query, all_new_nodes[i:i+CHUNK])

    def get_chapters(self):
        return self.created_nodes["chapter"]
    
    def get_paras(self):
        return self.created_nodes["para"]
    
    def get_verses(self):
        return self.created_nodes["verse"]
    
    def get_notes(self):
        return self.created_nodes["note"]
    
    # May remove if I choose to initialise it in a different way e.g. init script
    def createStrongs(self, strong_code):
        # Write any new unique strongs that haven't been added to database yet
        self.cur.execute("""
            SELECT id FROM bible.strongs WHERE code=%s
        """, (strong_code,))
        strong_id = self.cur.fetchone()

        if strong_id == None:
            # check what language the code belongs to 
            language_id = None
            if strong_code[0:1] == "G": # Greek
                self.cur.execute("""
                    SELECT id FROM bible.languages WHERE name LIKE 'Greek%'
                """)
                language_id = self.cur.fetchone()[0]
            elif strong_code[0:1] == "H": # Hebrew
                self.cur.execute("""
                    SELECT id FROM bible.languages WHERE name LIKE 'Hebrew%'
                """)
                language_id = self.cur.fetchone()[0]

            self.cur.execute("""
                INSERT INTO bible.strongs (code, language_id) 
                VALUES (%s, %s)
            """, (strong_code, language_id))

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

    new_nodes = Nodes(None, conn, test_book_xml)
    print(new_nodes.get_chapters()["3JN"])