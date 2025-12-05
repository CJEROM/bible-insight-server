

# Responsible for helping me test token queries and trying to reassemble fragments in a way I might request it from the server

# This object works as a deribative of Tokenisation as tokenisation identifies nodes that are tokenisable, 
#       using that information, we can make use of this object either, to recontruct these up to a certain context (not chapter)
#       and then serve that to the user as a result, as well as information on where it sits.

# The idea is to anchor references to any information by either, verse, chapter, book, translation (the ones that make sense to users)

import psycopg2
import os
from pathlib import Path
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

class Assembler:
    SQL = {
        # Reconstruct from OCCURENCE -> ID
        "get_chapter_tokenisable_nodes": """
            WITH chapter_bounds AS (
                SELECT start_node, end_node
                FROM bible.chapteroccurences
                WHERE id = %s
            )
            SELECT n.id, n.node_text
            FROM chapter_bounds cb
            JOIN bible.nodes n 
                ON n.id BETWEEN cb.start_node AND cb.end_node
                AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_tokenisable_nodes": """
            WITH verse_bounds AS (
                SELECT start_node, end_node
                FROM bible.verseoccurences
                WHERE id = %s
            )
            SELECT n.id, n.node_text
            FROM verse_bounds vb
            JOIN bible.nodes n 
                ON n.id BETWEEN vb.start_node AND vb.end_node
                AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_book_tokenisable_nodes": """
            SELECT id, node_text
            FROM bible.nodes
            WHERE is_tokenisable = TRUE
                AND book_map_id = %s
            ORDER BY id;
        """,
        # Reconstruct from NODE -> ID
        "get_book_for_node_id": """
            SELECT n.id, n.node_text
            FROM bible.nodes n
            WHERE n.book_map_id = (
                SELECT book_map_id
                FROM book.nodes
                WHERE id = %s
            )
            AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_chapter_for_node_id": """
            WITH chapter_found AS (
                SELECT id, start_node, end_node
                FROM bible.chapteroccurences
                WHERE start_node <= %s AND end_node >= %s
                LIMIT 1
            )
            SELECT n.id, n.node_text
            FROM bible.nodes n 
            JOIN chapter_found cf
                ON n.id BETWEEN cf.start_node AND cf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_for_node_id": """
            WITH verse_found AS (
                SELECT id, start_node, end_node
                FROM bible.verseoccurences
                WHERE start_node <= %s AND end_node >= %s
                LIMIT 1
            )
            SELECT n.id, n.node_text
            FROM bible.nodes n 
            JOIN verse_found vf
                ON n.id BETWEEN vf.start_node AND vf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        # Reconstruct from NODE -> CANONICAL PATH
        "get_book_for_node_path": """
            SELECT n.id, n.node_text
            FROM bible.nodes n
            WHERE n.book_map_id = (
                SELECT book_map_id
                FROM book.nodes
                WHERE canonical_path = %s AND translation_id = %s
            )
            AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_chapter_for_node_path": """
            WITH node_found AS (
                SELECT id AS node_id
                FROM bible.nodes 
                WHERE canonical_path = %s AND translation_id = %s
            ),
            chapter_found AS (
                SELECT id, start_node, end_node
                FROM bible.chapteroccurences cf
                JOIN node_found nf
                  ON nf.node_id BETWEEN cf.start_node AND cf.end_node
                LIMIT 1
            )
            SELECT n.id, n.node_text
            FROM bible.nodes n 
            JOIN chapter_found cf
                ON n.id BETWEEN cf.start_node AND cf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_for_node_path": """
            WITH node_found AS (
                SELECT id AS node_id
                FROM bible.nodes 
                WHERE canonical_path = %s AND translation_id = %s
            ),
            verse_found AS (
                SELECT id, start_node, end_node
                FROM bible.verseoccurences vf
                JOIN node_found nf
                  ON nf.node_id BETWEEN vf.start_node AND vf.end_node
                LIMIT 1
            )
            SELECT n.id, n.node_text
            FROM bible.nodes n 
            JOIN verse_found vf
                ON n.id BETWEEN vf.start_node AND vf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        # Reconstruct from REF
        "get_book_from_ref": """
            SELECT id, node_text
            FROM bible.nodes
            WHERE book_map_id = (
                SELECT id 
                FROM book.booktofile
                WHERE book_code = %s AND translation_id = %s
            )
            AND is_tokenisable = TRUE
            ORDER BY id;
        """,
        "get_chapter_from_ref": """
            WITH chapter_bounds AS (
                SELECT start_node, end_node
                FROM bible.chapteroccurences
                WHERE chapter_ref = %s AND translation_id = %s
            )
            SELECT n.id, n.node_text
            FROM chapter_bounds cb
            JOIN bible.nodes n 
                ON n.id BETWEEN cb.start_node AND cb.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_from_ref": """
            WITH verse_bounds AS (
                SELECT start_node, end_node
                FROM bible.verseoccurences
                WHERE verse_ref = %s AND translation_id = %s
            )
            SELECT n.id, n.node_text
            FROM verse_bounds vb
            JOIN bible.nodes n 
                ON n.id BETWEEN vb.start_node AND vb.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        # NOT IN USE YET
        "get_ref_all_verseoccurences": """
            SELECT * 
            FROM bible.verseoccurences
            WHERE verse_ref = %s
        """,
        "get_ref_all_chapteroccurences": """
            SELECT * 
            FROM bible.chapteroccurences
            WHERE chapter_ref = %s
        """
    }

    def __init__(self, ):
        # Adds a database connection
        self.conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD
        )
        self.cur = self.conn.cursor()

        # What context are we reconstructing: book OR chapter (already exists) OR verse       [heading? (future feature)]

        self.nodes = [] # Represents all (tokenisable) nodes used to reconstruct context
        self.text = ""

        self.reconstruct_occurence()

    def get_nodes(self):
        return self.nodes
    
    def get_reconstructed_text(self):
        return self.text
    
    def reconstruct_occurence(self, scope, occurence_id):
        query = ""
        match scope:
            case "book":
                query = self.SQL.get("get_book_tokenisable_nodes")
            case "chapter":
                query = self.SQL.get("get_chapter_tokenisable_nodes")
            case "verse":
                query = self.SQL.get("get_verse_tokenisable_nodes")

        self.cur.execute(query, (occurence_id,))
        tokenisable_nodes_results = self.cur.fetchall()
        for id, node_text in tokenisable_nodes_results:
            self.nodes.append(id)
            self.text += node_text

    def reconstruct_from_node_id(self, scope, node_id):
        query = ""
        match scope:
            case "book":
                query = self.SQL.get("get_book_for_node_id")
                self.cur.execute(query, (node_id,))
            case "chapter":
                query = self.SQL.get("get_chapter_for_node_id")
                self.cur.execute(query, (node_id,node_id))
            case "verse":
                query = self.SQL.get("get_verse_for_node_id")
                self.cur.execute(query, (node_id,node_id))
        
        tokenisable_nodes_results = self.cur.fetchall()
        for id, node_text in tokenisable_nodes_results:
            self.nodes.append(id)
            self.text += node_text

    def reconstruct_from_node_path(self, translation_id, canonical_path):
        query = ""
        match self.scope:
            case "book":
                query = self.SQL.get("get_book_for_node_path")
            case "chapter":
                query = self.SQL.get("get_chapter_for_node_path")
            case "verse":
                query = self.SQL.get("get_verse_for_node_path")

        self.cur.execute(query, (canonical_path,translation_id))
        tokenisable_nodes_results = self.cur.fetchall()
        for id, node_text in tokenisable_nodes_results:
            self.nodes.append(id)
            self.text += node_text

    def reconstruct_from_ref(self, translation_id, ref):
        # Find if GEN, GEN 1, GEN 1:1 => Based on that change query
        scope = None
        if len(ref.split(" ")) == 1: # No space so book
            scope = "book"
        elif len(ref.split(":")) == 1: # no verse so chapter
            scope = "chapter"
        else:
            scope = "verse"

        query = ""
        match scope:
            case "book":
                query = self.SQL.get("get_book_from_ref")
            case "chapter":
                query = self.SQL.get("get_chapter_from_ref")
            case "verse":
                query = self.SQL.get("get_verse_from_ref")

        self.cur.execute(query, (ref, translation_id))
        tokenisable_nodes_results = self.cur.fetchall()
        for id, node_text in tokenisable_nodes_results:
            self.nodes.append(id)
            self.text += node_text
    
    # Perhaps function to help build on nodes, to display strongs if available?

if __name__ == "__main__":
    chapter = Assembler("book", 1)
    print(chapter.get_nodes())
    print(chapter.get_reconstructed_text())