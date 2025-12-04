

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
            SELECT n.id, n.node_text
            FROM bible.nodes
            WHERE is_tokenisable = TRUE
                AND book_map_id = %s
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

    def __init__(self, scope, occurence_id):
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
        self.scope = scope
        self.occurence_id = occurence_id

        self.nodes = [] # Represents all (tokenisable) nodes used to reconstruct context
        self.text = ""

        self.reconstruct_occurence()

    def get_nodes(self):
        return self.nodes
    
    def get_reconstructed_text(self):
        return self.text
    
    def reconstruct_occurence(self):
        query = ""
        match self.scope:
            case "book":
                query = self.SQL.get("get_book_tokenisable_nodes")
            case "chapter":
                query = self.SQL.get("get_chapter_tokenisable_nodes")
            case "verse":
                query = self.SQL.get("get_verse_tokenisable_nodes")

        self.cur.execute(query, (self.occurence_id,))
        tokenisable_nodes_results = self.cur.fetchall()
        for id, node_text in tokenisable_nodes_results:
            self.nodes.append(id)
            self.text += node_text
    
    # Perhaps function to help build on nodes, to display strongs if available?

if __name__ == "__main__":
    chapter = Assembler("chapter", 1)
    print(chapter.get_nodes())
    print(chapter.get_reconstructed_text())