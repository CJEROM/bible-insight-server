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

        self.conn.commit()
        self.conn.close()
    
    def getBooks(self):
        self.cur.execute(self.SQL.get("get_book_map_ids", self.translation_id))
        book_ids = self.cur.fetchall()
        return book_ids

if __name__ == "__main__":
    pass