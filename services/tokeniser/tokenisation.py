import spacy
from spacy.tokens import Doc
from minio import Minio

from psycopg2.extras import execute_values
import time
import datetime
import sys

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

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

# Decided I need to better tokenise so first will load all verses and then update the data for them later, I want tokens afterall in my database.

NLP_MAPPING = {
    "eng": "en",                # ENGLISH
    "Greek": "el",              # Greek
    "grc": "grc",               # ANCIENT GREEK
    "hbo": "he",                # HEBREW
    "heb": "he"                 # HEBREW
}

# Spacy packages need to be installed, so need to account for storage space for these:
# To Install a package run the following command:
#       python3 -m spacy download en_core_web_lg 

# Where "en" can be replaced by any other language code below => See also https://spacy.io/usage/models#section-languages 
# where "lg" can be replaced by ["sm" ,"md", "lg", "trf"] => See https://spacy.io/models/en

# Hebrew has no trained packages so no tokenisation
# Need to change map to consider this
# Add Validation to check for existence of key

# Will create tokens for one translation at a time, to preprocess it all, then carry on with the rest before moving onto others.

class Tokenisation:
    default_log_level = 1 # Here I can set the level of logging I want for my application

    LOG_MAPPING = {
        "TRACE": 0,
        "DEBUG": 1,
        "INFO": 2,
        "WARN": 3,
        "ERROR": 4,
        "FATAL": 5
    }

    SQL = {
        # --------------------------------- Fetch Types ---------------------------------
        "get_language": """
            SELECT
                ti.language_id
            FROM bible.translations t
                JOIN bible.translationinfo ti ON t.dbl_id = ti.dbl_id
            WHERE t.id = %s;
        """,
        "get_translation_books": """
            SELECT id FROM bible.booktofile WHERE translation_id = %s ORDER BY id;
        """,
        "get_book_chapters": """
            SELECT id, reconstructed_text, chapter_ref FROM bible.chapteroccurences WHERE book_map_id = %s ORDER BY id;
        """,
        "get_chapter_verses": """
            SELECT id FROM bible.verseoccurences WHERE chapter_id = %s ORDER BY id;
        """,
        # --------------------------------- NLP Lookup Types ---------------------------------
        "create_pos_lookup": """
            INSERT INTO lookup.nlp_pos_types (pos_tag) VALUES %s ON CONFLICT DO NOTHING;
        """,
        "create_dep_lookup": """
            INSERT INTO lookup.nlp_dep_types (dep) VALUES %s ON CONFLICT DO NOTHING;
        """,
        "create_tag_lookup": """
            INSERT INTO lookup.nlp_tag_types (tag) VALUES %s ON CONFLICT DO NOTHING;
        """,
        # --------------------------------- Node Types ---------------------------------
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
        # --------------------------------- Node Update Types ---------------------------------
        "update_node_offsets": """
            UPDATE bible.nodes 
            SET chapter_start_offset = %s, chapter_end_offset = %s
            WHERE id = %s;
        """,
        "update_chapter_occurence_text": """
            UPDATE bible.chapteroccurences 
            SET reconstructed_text = %s
            WHERE id = %s;
        """,
        # --------------------------------- Token Types ---------------------------------
        "create_token": """
            INSERT INTO bible.tokens (text, chapter_start_offset, chapter_end_offset, pos, tag, dep, lemma_id, trailing_space, is_alpha, is_punct, is_space, is_quote, is_left_punct, is_right_punct, like_num, language_id, translation_id, chapter_occurence_id, head_token_id)
            VALUES %s
            RETURNING id;
        """,
        "max_token_count": """
            SELECT COALESCE(MAX(id), 0) FROM bible.tokens;
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

        # Passes Minio client connection on to the MinioUSXUpload class
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_USERNAME,
            secret_key=MINIO_PASSWORD,
            secure=False
        )

        self.start_time = time.time()
        self.progress_message = None

        # Initialise logfile
        log_path = Path(__file__).parents[2] / "logs"
        self.log_file = log_path / f"_TOKENS-{self.translation_id}.log"

        try:
            os.makedirs(log_path)
        except Exception as e:
            print("Log File Path Already Exists!")
        print(f"See Log File at: {self.log_file}!")

        with open(self.log_file, 'w', encoding="utf-8") as f:
            f.write(f"Starting Tokenisation ...\n")

        self.cur.execute(self.SQL.get("get_language"), (self.translation_id,))
        self.language_id = self.cur.fetchone()[0]

        self.log_ingestion_activity(f"Linked to Language with ID: {self.language_id}", "INIT", "INFO")

        self.cur.execute(self.SQL.get("init_tokenisable_nodes"), (self.translation_id,))

        self.log_ingestion_activity(f"Initialised Tokenisable Nodes!", "INIT", "INFO")

        self.reconstruct_chapter_nodes()

        self.log_ingestion_activity(f"Finished Constructing Tokens: {self.language_id}", "INIT", "INFO")

        self.create_tokens()

        # Then run a part that will run in a lopp like semi-supervised learning for tokeniser 
        #     to figure out if it has done it correctly by just doing distinct query and looking for weird cases
        # self.reconstruct_tokens(self.fetch_chapter_tokens(1))

        self.conn.commit()
        self.conn.close()
    
    def reconstruct_chapter_nodes(self):
        # Get all Books for this Translation
        self.cur.execute(self.SQL.get("get_translation_books"), (self.translation_id,))
        all_books = self.cur.fetchall()

        for book_map_id in all_books:
            # Get all Chapters for this Book
            self.cur.execute(self.SQL.get("get_book_chapters"), (book_map_id,))
            all_chapters = self.cur.fetchall()

            for chapter_occurence_id,_,chapter_ref in all_chapters:
                # Get all tokenisable nodes for this chapter.
                self.cur.execute(self.SQL.get("get_chapter_tokenisable_nodes"), (chapter_occurence_id,))
                tokenisable_nodes = self.cur.fetchall()
                self.log_ingestion_activity(f"Nodes found to be tokenisable for [{chapter_ref}]: [{tokenisable_nodes}]", "NODE", "DEBUG")

                chapter_text = ""

                for node_id, text in tokenisable_nodes:
                    start = len(chapter_text)
                    chapter_text+=text  # Accumulate text for chapter occurence from nodes
                    end = len(chapter_text)

                    # Update start, end offsets for node
                    self.cur.execute(self.SQL.get("update_node_offsets"), (start, end, node_id))

                # When finished iterating through nodes
                #       update chapter_occurences with reconstructed chapter_text
                self.cur.execute(self.SQL.get("update_chapter_occurence_text"), (chapter_text, chapter_occurence_id))
                # print(chapter_text)
                self.log_ingestion_activity(f"Reconstructed Chapter [{chapter_ref}] Occurence [{chapter_occurence_id}]: \n[{chapter_text}\n]", "NODE", "TRACE")
    
    def create_tokens(self):
        # Init spacy pipeline used for training
        spacy_lang = "en"
        nlp = spacy.load(f"{spacy_lang}_core_web_sm")

        # Get all Books for this Translation
        self.cur.execute(self.SQL.get("get_translation_books"), (self.translation_id,))
        all_books = self.cur.fetchall()

        all_new_tokens = []
        token_count = 1

        total_books = len(all_books)
        
        self.cur.execute(self.SQL.get("max_token_count"))
        token_id_offset = self.cur.fetchone()[0]

        unique_pos = set()
        unique_tag = set()
        unique_dep = set()

        for i, book_map_id in enumerate(all_books):
            # Get all Chapters for this Book
            self.cur.execute(self.SQL.get("get_book_chapters"), (book_map_id,))
            all_chapters = self.cur.fetchall()

            # ✅ Proper loading bar (50 characters wide)
            progress = int((i / total_books) * 50)
            bar = '#' * progress + '-' * (50 - progress)
            percentage = int((i / total_books) * 100)

            self.progress_message = f"\r    Processing Books: |{bar}| {percentage}%"

            for chapter_occurence_id, chapter_text, chapter_ref in all_chapters:
                # Start NLP on reconstructed chapter text
                doc = nlp(chapter_text)

                token_mapping = {}

                temp_tokens = []

                self.log_ingestion_activity(f"Creating {len(doc)} Tokens for [{chapter_ref}]...", "TOKEN", "DEBUG")

                self.progress_message = f"\r    Processing Books: |{bar}| {percentage}% | {chapter_ref} / {len(all_chapters)}"

                for i, token in enumerate(doc):
                    pos = token.pos_
                    tag = token.tag_
                    dep = token.dep_

                    # Makes sure they exist in lookup tables
                    unique_pos.add((pos,))
                    unique_tag.add((tag,))
                    unique_dep.add((dep,))

                    # You may want a lemma lookup table; for now store lemma text directly
                    lemma = token.lemma_
                    lemma_id = lemma

                    this_token = [
                        token.text, 
                        token.idx,
                        token.idx + len(token.text),
                        pos,
                        tag,
                        dep,
                        lemma_id,
                        len(token.whitespace_) > 0,
                        token.is_alpha,
                        token.is_punct,
                        token.is_space,
                        token.is_quote,
                        token.is_left_punct,
                        token.is_right_punct,
                        token.like_num,
                        self.language_id,
                        self.translation_id,
                        chapter_occurence_id,
                        None # will be updated with head_token_id (i -> 18)
                    ]

                    self.log_ingestion_activity(f"Creating Temp Token [{i}] [{token.idx}]: {this_token}", "TOKEN", "TRACE")

                    token_db_id = token_count + token_id_offset # self.cur.fetchone()[0]
                    token_mapping[i] = [token_db_id, token.head.idx]

                    # Prepare for next node, and add for bulk insert
                    temp_tokens.append(this_token)
                    token_count += 1

                # print(token_mapping)
                self.log_ingestion_activity(f"Current Temp Tokens => {temp_tokens}", "TOKEN", "TRACE")

                for i, token in enumerate(temp_tokens):
                    temp_token = token_mapping.get(i)

                    if temp_token == None:
                        continue

                    head_db_id = token_mapping[i][0]
                    self.log_ingestion_activity(f"Updating Temp Token at [{i}] with head_db_id {head_db_id}", "TOKEN", "TRACE")

                    temp_tokens[i][18] = head_db_id
                    all_new_tokens.append(tuple(temp_tokens[i]))

                self.log_ingestion_activity(f"Finished Token Creation for [{chapter_ref}]", "TOKEN", "DEBUG")
                self.log_ingestion_activity(f"Current Tokens => {all_new_tokens}", "TOKEN", "TRACE")

        # Now bulk insert all of the nodes into the database (in batches / chunks)
        CHUNK = 20000  # ideal for execute_values

        unique_pos = list(unique_pos)
        unique_tag = list(unique_tag)
        unique_dep = list(unique_dep)

        # Bulk insert lookup values
        sql_query = self.SQL.get("create_pos_lookup")
        for i in range(0, len(unique_pos), CHUNK):
            execute_values(self.cur, sql_query, unique_pos[i:i+CHUNK])  

        sql_query = self.SQL.get("create_tag_lookup")
        for i in range(0, len(unique_tag), CHUNK):
            execute_values(self.cur, sql_query, unique_tag[i:i+CHUNK])  

        sql_query = self.SQL.get("create_dep_lookup")
        for i in range(0, len(unique_dep), CHUNK):
            execute_values(self.cur, sql_query, unique_dep[i:i+CHUNK])  

        # Bulk Insert Tokens
        sql_query = self.SQL.get("create_token")
        for i in range(0, len(all_new_tokens), CHUNK):
            execute_values(self.cur, sql_query, all_new_tokens[i:i+CHUNK])  

    def stream_file(self, object_name):
        # Get file
        response = None 
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name,
            )
            # Read the data as bytes, then decode as UTF-8
            data = response.read().decode("utf-8")
            return data
        finally:
            if response:
                response.close()
                response.release_conn()   

    def elapsed_ingestion_time(self):
        duration = time.time() - self.start_time
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)

        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
        return formatted_duration

    def log_ingestion_activity(self, log_message, source_class, log_level):
        # Always update CLI progress bar, just only conditionally log
        if self.progress_message != None and hasattr(sys.stdout, "write"):
            sys.stdout.write(f"\r{self.progress_message} | [Elapsed: {self.elapsed_ingestion_time()}] | ")
            sys.stdout.flush()

        if self.LOG_MAPPING[log_level] < self.default_log_level:
            return

        with open(self.log_file, 'a', encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} [{log_level}] [Elapsed: {self.elapsed_ingestion_time()}] [{source_class}] {log_message}\n")

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