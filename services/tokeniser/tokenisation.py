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
        "init_tokenisable_nodes": """
            WITH RECURSIVE text_nodes AS (
                SELECT
                    n.id          AS text_node_id,
                    n.parent_node_id
                FROM bible.nodes n
                WHERE n.node_type = 'text'
                AND n.canonical_path LIKE '%%para%%text%%'
                AND n.canonical_path NOT LIKE '%%note%%'
                AND n.book_map_id IN (
                    SELECT id
                    FROM bible.booktofile
                    WHERE translation_id = %s
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
        "get_tokenisable_nodes": """
            SELECT
                n.id AS text_node_id,
                n.node_text
            FROM bible.nodes n
            WHERE n.is_tokenisable = 'true'
            AND n.book_map_id IN (
                    SELECT id FROM bible.booktofile
                    WHERE translation_id = %s   -- <-- your target translation
            )
            ORDER BY n.id ASC
        """,
        "create_tokens": """
            INSERT INTO bible.tokens (text, node_id, start_offset, end_offset, trailing_space, is_alpha, is_punct, is_space, like_num, language_id, translation_id)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """,
        "get_language": """
            SELECT
                ti.language_id
            FROM bible.translations t
                JOIN bible.translationinfo ti ON t.dbl_id = ti.dbl_id
            WHERE t.id = %s;
        """,
        "get_chapter_tokens": """
            WITH chapter_bounds AS (
                SELECT start_node, end_node
                FROM bible.chapteroccurences
                WHERE id = %s
            )
            SELECT t.*
            FROM chapter_bounds cb
            JOIN bible.nodes n 
                ON n.id BETWEEN cb.start_node AND cb.end_node
                AND n.is_tokenisable = TRUE
            JOIN bible.tokens t 
                ON t.node_id = n.id
            ORDER BY n.id, t.start_offset;
        """,
        "get_verse_tokens": """
            WITH verse_bounds AS (
                SELECT start_node, end_node
                FROM bible.verseoccurences
                WHERE id = %s
            )
            SELECT t.*
            FROM verse_bounds vb
            JOIN bible.nodes n 
                ON n.id BETWEEN vb.start_node AND vb.end_node
                AND n.is_tokenisable = TRUE
            JOIN bible.tokens t 
                ON t.node_id = n.id
            ORDER BY n.id, t.start_offset;
        """,
        "get_translation_books": """
            SELECT id FROM bible.booktofile WHERE translation_id = %s
        """,
        "get_book_chapters": """
            SELECT id FROM bible.chapteroccurences WHERE book_map_id = %s
        """,
        "get_chapter_verses": """
            SELECT id FROM bible.verseoccurences WHERE chapter_id = %s
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

        self.cur.execute(self.SQL.get("get_language"), (self.translation_id,))
        self.language_id = self.cur.fetchone()[0]
        
        self.create_tokens()

        # Then run a part that will run in a lopp like semi-supervised learning for tokeniser 
        #     to figure out if it has done it correctly by just doing distinct query and looking for weird cases
        self.reconstruct_tokens(self.fetch_chapter_tokens(1))

        self.conn.commit()
        self.conn.close()
    
    def get_tokenisable_nodes(self):
        # First figure out whether the text_nodes are tokenisable (should put a query together for it)
        # Then update them as such in the database
        self.cur.execute(self.SQL.get("init_tokenisable_nodes"), (self.translation_id,))

        # Then get all tokenisable nodes
        self.cur.execute(self.SQL.get("get_tokenisable_nodes"), (self.translation_id,))
        tokenisable_nodes = self.cur.fetchall()
        return tokenisable_nodes
    
    def create_tokens(self):
        self.cur.execute(self.SQL.get("get_tokenisable_nodes"), (self.translation_id,))
        tokenisable_nodes = self.cur.fetchall()

        if len(tokenisable_nodes) > 0:
            return

        nlp = spacy.blank("en")
        for node_id, text in self.get_tokenisable_nodes():
            node_doc = nlp(text)

            for token in node_doc:
                self.cur.execute(
                    self.SQL.get("create_tokens"), 
                    (
                        token.text, 
                        node_id,
                        token.idx,
                        token.idx + len(token.text),
                        len(token.whitespace_) > 0,
                        token.is_alpha,
                        token.is_punct,
                        token.is_space,
                        token.like_num,
                        self.language_id,
                        self.translation_id
                    ))

    def fetch_verse_tokens(self, verse_occurence_id):
        # Responsible for reconstructing verses from tokens, to allow for easier nlp
        # 1. Get all verse occurences for the translation
        # 2. For each verse occurence, get all tokens that belong to it
        # 3. Reconstruct the verse text from the tokens
        self.cur.execute(self.SQL.get("get_verse_tokens"), (verse_occurence_id,))
        verse_tokens = self.cur.fetchall()
        return verse_tokens

    def fetch_chapter_tokens(self, chapter_occurence_id):
        # Responsible for reconstructing chapters from verses, to allow for easier nlp
        # 1. Get all chapter occurences for the translation
        # 2. For each chapter occurence, get all tokens that belong to it
        # 3. Reconstruct the chapter text from the tokens
        # 4. Apply nlp to the chapter text to get better tokenisation
        # 5. Update the tokens in the database with the new tokenisation
        self.cur.execute(self.SQL.get("get_chapter_tokens"), (chapter_occurence_id,))
        chapter_tokens = self.cur.fetchall()
        return chapter_tokens

    def reconstruct_tokens(self, tokens):
        joined_text = ""
        for token in tokens:
            token_id = token[0]
            token_text = token[1]
            token_node_id = token[2]
            start_offset = token[3]
            end_offset = token[4]
            trailing_space = token[10]

            joined_text+=token_text
            if trailing_space:
                joined_text+=" "
        print(joined_text)

    def update_tokens(self):
        # Module responsible for updating tokens with nlp information e.g pos, tag, dep, head_token_id, lemma
        pass

if __name__ == "__main__":
    # conn = psycopg2.connect(
    #     host=POSTGRES_HOST,
    #     port=POSTGRES_PORT,
    #     dbname=POSTGRES_DB,
    #     user=POSTGRES_USERNAME,
    #     password=POSTGRES_PASSWORD
    # )
    # cur = conn.cursor()

    # cur.execute("""
    #     SELECT id FROM bible.translations;            
    # """)
    # all_translations = cur.fetchall()

    # for translation in all_translations:
    #     Tokenisation(translation)
    
    Tokenisation(1)
    pass