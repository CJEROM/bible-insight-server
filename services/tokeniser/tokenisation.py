import spacy

from psycopg2.extras import execute_values
import time
import datetime
import sys
from pathlib import Path
import os

from manager.managerhandler import ManagerHandler

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

    def __init__(self, translation_id, manager:ManagerHandler = None):
        self.translation_id = translation_id

        self.manager = manager
        if manager == None:
            self.manager = ManagerHandler()
            self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        self.db = self.manager.get_db()
        self.obj = self.manager.get_obj()
        self.log = self.manager.create_log(f"_TOKENS-{self.translation_id}")
        self.log.set_logging_level(1)

        self.log.log_to_file(f"Starting Tokenisation ...\n", "TOKENISATION", "INFO")

        self.language_id = self.db.fetch_clean_one(self.SQL.get("get_language"), (self.translation_id,))

        self.log.log_to_file(f"Linked to Language with ID: {self.language_id}", "INIT", "INFO")

        self.reconstruct_chapter_nodes()

        self.log.log_to_file(f"Finished Constructing Tokens: {self.language_id}", "INIT", "INFO")

        self.create_tokens()

        # print(self.loadLanguageLDML())

        # Then run a part that will run in a lopp like semi-supervised learning for tokeniser 
        #     to figure out if it has done it correctly by just doing distinct query and looking for weird cases
        # self.reconstruct_tokens(self.fetch_chapter_tokens(1))

        self.db.commit()
        self.db.close()
    
    def reconstruct_chapter_nodes(self):
        # Get all Books for this Translation
        all_books = self.db.fetch_all(self.SQL.get("get_translation_books"), (self.translation_id,))

        for book_map_id in all_books:
            # Get all Chapters for this Book
            all_chapters = self.db.fetch_all(self.SQL.get("get_book_chapters"), (book_map_id,))

            for chapter_occurence_id,_,chapter_ref in all_chapters:
                # Get all tokenisable nodes for this chapter.
                tokenisable_nodes = self.db.fetch_all(self.SQL.get("get_chapter_tokenisable_nodes"), (chapter_occurence_id,))
                self.log.log_to_file(f"Nodes found to be tokenisable for [{chapter_ref}]: [{tokenisable_nodes}]", "NODE", "DEBUG")

                chapter_text = ""

                for node_id, text in tokenisable_nodes:
                    start = len(chapter_text)
                    chapter_text+=text  # Accumulate text for chapter occurence from nodes
                    end = len(chapter_text)

                    # Update start, end offsets for node
                    self.db.execute(self.SQL.get("update_node_offsets"), (start, end, node_id))

                # When finished iterating through nodes
                #       update chapter_occurences with reconstructed chapter_text
                self.db.execute(self.SQL.get("update_chapter_occurence_text"), (chapter_text, chapter_occurence_id))
                # print(chapter_text)
                self.log.log_to_file(f"Reconstructed Chapter [{chapter_ref}] Occurence [{chapter_occurence_id}]: \n[{chapter_text}\n]", "NODE", "TRACE")
    
    def create_tokens(self):
        # Init spacy pipeline used for training
        spacy_lang = "en"
        nlp = spacy.load(f"{spacy_lang}_core_web_sm")

        # Get all Books for this Translation
        all_books = self.db.fetch_all(self.SQL.get("get_translation_books"), (self.translation_id,))

        all_new_tokens = []
        token_count = 1

        self.log.set_progress_total(len(all_books))
        
        token_id_offset = self.db.fetch_clean_one(self.SQL.get("max_token_count"))

        unique_pos = set()
        unique_tag = set()
        unique_dep = set()

        for book_i, book_map_id in enumerate(all_books):
            # Get all Chapters for this Book
            all_chapters = self.db.fetch_all(self.SQL.get("get_book_chapters"), (book_map_id,))

            self.log.set_progress(new_message=" ", progress=book_i)

            for chapter_occurence_id, chapter_text, chapter_ref in all_chapters:
                # Start NLP on reconstructed chapter text
                doc = nlp(chapter_text)

                token_mapping = {}

                temp_tokens = []

                self.log.log_to_file(f"Creating {len(doc)} Tokens for [{chapter_ref}]...", "TOKEN", "DEBUG")

                self.log.set_progress(new_message=f"{chapter_ref} / {len(all_chapters)}", progress=book_i)

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

                    self.log.log_to_file(f"Creating Temp Token [{i}] [{token.idx}]: {this_token}", "TOKEN", "TRACE")

                    token_db_id = token_count + token_id_offset # self.cur.fetchone()[0]
                    token_mapping[i] = [token_db_id, token.head.idx]

                    # Prepare for next node, and add for bulk insert
                    temp_tokens.append(this_token)
                    token_count += 1

                # print(token_mapping)
                self.log.log_to_file(f"Current Temp Tokens => {temp_tokens}", "TOKEN", "TRACE")

                for i, token in enumerate(temp_tokens):
                    temp_token = token_mapping.get(i)

                    if temp_token == None:
                        continue

                    head_db_id = token_mapping[i][0]
                    self.log.log_to_file(f"Updating Temp Token at [{i}] with head_db_id {head_db_id}", "TOKEN", "TRACE")

                    temp_tokens[i][18] = head_db_id
                    all_new_tokens.append(tuple(temp_tokens[i]))

                self.log.log_to_file(f"Finished Token Creation for [{chapter_ref}]", "TOKEN", "DEBUG")
                self.log.log_to_file(f"Current Tokens => {all_new_tokens}", "TOKEN", "TRACE")

        # Now bulk insert all of the nodes into the database (in batches / chunks)
        self.db.set_chunks(20000)  # ideal for execute_values

        unique_pos = list(unique_pos)
        unique_tag = list(unique_tag)
        unique_dep = list(unique_dep)

        # Bulk insert lookup values
        self.db.bulk_insert(self.SQL.get("create_pos_lookup"), unique_pos)
        self.db.bulk_insert(self.SQL.get("create_tag_lookup"), unique_tag)
        self.db.bulk_insert(self.SQL.get("create_dep_lookup"), unique_dep)

        # Bulk Insert Tokens
        self.db.bulk_insert(self.SQL.get("create_token"), all_new_tokens)

if __name__ == "__main__":
    is_test = True

    manager = ManagerHandler()
    manager.get_obj().set_default_bucket("bible-dbl-raw")

    if is_test:
        # Tokenisation(1, manager) # Basic    English
        Tokenisation(7, manager) # Strongs  English
    else:
        db = manager.get_db()

        all_translations = db.fetch_all("""
            SELECT id FROM bible.translations;            
        """)

        for translation in all_translations:
            Tokenisation(translation[0], manager)