import spacy
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

# Decided I need to better tokenise so first will load all verses and then update the data for them later, I want tokens afterall in my database.

NLP_MAPPING = {
    "eng": "en",                # ENGLISH
    "Greek": "el",              # Greek
    "grc": "grc",               # ANCIENT GREEK
    "hbo": "he",                # HEBREW
    "heb": "he"                 # HEBREW
}

# Will create tokens for one translation at a time, to preprocess it all, then carry on with the rest before moving onto others.

class Tokenisation:
    SQL = {
        "get_book_map_ids": """
            SELECT 
                btf.id
            FROM bible.booktofile btf 
            WHERE btf.translation_id = %s;
        """,
        "init_tokenisable_nodes": """
            WITH RECURSIVE text_nodes AS (
                SELECT
                    n.id          AS text_node_id,
                    n.parent_node_id
                FROM bible.nodes n
                WHERE n.node_type = 'text'
                AND n.canonical_path LIKE '%para%text%'
                AND n.canonical_path NOT LIKE '%note%'
                AND n.book_map_id IN (
                    SELECT id
                    FROM bible.booktofile
                    WHERE translation_id = ?
                )
            ),
            --SELECT * FROM text_nodes;
            ancestor_chain AS (
                -- seed: start at the text node's parent
                SELECT
                    t.text_node_id,
                    t.parent_node_id      AS ancestor_id,
                    1                     AS depth
                FROM text_nodes t

                UNION ALL

                -- step: move one level up each time
                SELECT
                    ac.text_node_id,
                    n.parent_node_id      AS ancestor_id,
                    ac.depth + 1          AS depth
                FROM ancestor_chain ac
                JOIN bible.nodes n
                ON n.id = ac.ancestor_id
                WHERE ac.ancestor_id IS NOT NULL
            ),
            para_for_text AS (
                SELECT DISTINCT ON (ac.text_node_id)
                    ac.text_node_id,
                    ac.ancestor_id AS para_node_id,
                    ac.depth
                FROM ancestor_chain ac
                JOIN bible.nodes p
                ON p.id = ac.ancestor_id
                WHERE p.node_type = 'para'
                ORDER BY ac.text_node_id, ac.depth  -- keep nearest para
            )
            UPDATE bible.nodes n
            SET is_tokenisable = TRUE
            FROM para_for_text pt
            JOIN bible.paragraphs bp
            ON bp.node_id = pt.para_node_id
            WHERE n.id = pt.text_node_id
            AND bp.is_versetext = TRUE
            AND n.is_tokenisable IS DISTINCT FROM TRUE;
        """,
        "get_tokenisable": """
            SELECT
                n.id AS text_node_id
            FROM bible.nodes n
            WHERE n.is_tokenisable = 'true'
            AND n.book_map_id IN (
                    SELECT id FROM bible.booktofile
                    WHERE translation_id = %s   -- <-- your target translation
            )
        """
    }

    def __init__(self, translation_id):
        self.translation_id = translation_id

        # Adds a database connection
        self.conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD
        )
        self.cur = self.conn.cursor()

        self.nlp = spacy.blank("en")
        # self.nlp = spacy.load(
        #     "en_core_web_sm", 
        #     disable=[
        #         "tok2vec",              # word verctors / embeddings for downstream components
        #         "tagger",               # part-of-speach tagger
        #         "parser",               # dependency parser
        #         "attribute_ruler",      # replacement rules after tagger / parser
        #         "lemmatizer",           # computes lemmas (dictionary form of the word)
        #         "ner"                   # named entity recognition
        #     ]
        # )
        
        print(self.get_tokenisable_nodes())

        # Then run a part that will run in a lopp like semi-supervised learning for tokeniser 
        #     to figure out if it has done it correctly by just doing distinct query and looking for weird cases

        # 

        self.conn.commit()
        self.conn.close()
    
    def get_books(self):
        self.cur.execute(self.SQL.get("get_book_map_ids", self.translation_id))
        book_ids = self.cur.fetchall()
        return book_ids

    def get_tokenisable_nodes(self):
        # First figure out whether the text_nodes are tokenisable (should put a query together for it)
        # Then update them as such in the database
        self.cur.execute(self.SQL.get("init_tokenisable_nodes"), (self.translation_id,))

        # Then get all tokenisable nodes
        self.cur.execute(self.SQL.get("get_tokenisable_nodes"), (self.translation_id,))
        tokenisable_nodes = self.cur.fetchall()
        return tokenisable_nodes

if __name__ == "__main__":
    Tokenisation(1)
    pass