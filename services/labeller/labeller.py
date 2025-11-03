import spacy
import re
import json
from minio import Minio
import psycopg2
from label_studio_sdk import LabelStudio
from pathlib import Path
from bs4 import BeautifulSoup
import os
from collections import Counter
import time

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

TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\w\s]")

class Labeller:
    def __init__(self, translation_id, nlp_words_filepath):
        self.nlp = spacy.load("en_core_web_sm")
        self.translation_id = translation_id
        self.nlp_words_filepath = nlp_words_filepath

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
        exports = self.export_word_list()
        duration = round(time.time() - self.start_time, 2)
        print(f"✅ Migrated [{exports}] Words to DB in {duration} seconds for translation [{self.translation_id}]!\n")

        self.conn.commit()
        self.cur.close()
        self.conn.close()

    # Make use and amend below function, to feed in files for processing (e.g. Book Classes)
    def stream_file(self, object_name, bucket):
        # Get file
        response = None 
        try:
            response = self.client.get_object(
                bucket_name=bucket,
                object_name=object_name,
            )
            # Read the data as bytes, then decode as UTF-8
            data = response.read().decode("utf-8")
            return data
        finally:
            if response:
                response.close()
                response.release_conn()

    def get_book_files(self):
        self.cur.execute("""
            SELECT 
                btf.book_code,
                f.etag,
                f.file_path,
                f.bucket
            FROM bible.booktofile btf 
                JOIN bible.files f ON btf.file_id = f.id
            WHERE btf.translation_id = %s;
        """, (self.translation_id,))

        db_books = self.cur.fetchall()
        return db_books

    def get_word_list(self):
        db_books = self.get_book_files()
        translation_text = ""
        
        for code, etag, object_name, bucket in db_books:
            book_file_content = self.stream_file(object_name, bucket)
            book_xml = BeautifulSoup(book_file_content, "xml")
            # Go though paragraph by paragraph
            book_text = self.get_para_text(book_xml)
            translation_text += book_text + "\n"

        results = self.get_word_frequencies(self.get_tokens_without_puntuation(translation_text))
        # results = self.get_tokens_without_puntuation(translation_text)
        return results.keys()

    def export_word_list(self):
        word_list = self.get_word_list()
        nlp_words = self.load_nlp_words()
        words_added = []
        for word in word_list:
            try:
                is_nlp = word in nlp_words

                self.cur.execute("""
                    INSERT INTO bible.word_list (text, nlp) 
                    VALUES (%s, %s)
                    RETURNING id;
                """, (word, is_nlp))
                words_added.append(self.cur.fetchone())
            except Exception as e:
                pass

        return len(words_added)

    def get_para_text(self, book_xml):
        temp_book_xml = BeautifulSoup(str(book_xml), "xml")
        
        # Gets Rid of the book tag that would be included and add Translation name to word list
        book_tag = temp_book_xml.find("book")
        book_tag.decompose()

        book_paras = temp_book_xml.find_all("para")

        # Check for para tags
        for para in book_paras:
            # print(para)
            para_style = para.get("style")

            if para_style != None:
                self.cur.execute("""
                    SELECT versetext FROM bible.styles WHERE style = %s AND source_file_id = (SELECT style_file FROM bible.translations WHERE id = %s);
                """, (para_style, self.translation_id))
                result = self.cur.fetchone()[0]

                # If not part of actual scripture text then remove
                is_versetext = True if result else False
                if is_versetext == False:
                    para.decompose()

                # Remove <note> tags completely
                all_notes = para.find_all("note")
                if len(all_notes) > 0:
                    for note in para.find_all("note"):
                        note.decompose()

        final_text = temp_book_xml.get_text().strip()
        return final_text

    def get_tokens(self, text):
        return TOKEN_PATTERN.findall(text)
    
    def get_tokens_without_puntuation(self, text):
        return [t for t in self.get_tokens(text) if re.match(r"[A-Za-z0-9]", t)]
        # Keeps only words & numbers, removes punctuation

    def get_word_frequencies(self, tokens):
        return Counter(tokens)  # returns a dict-like object with counts

    def load_nlp_words(self):
        # These are words that beforehand I have already identified as of interest to my labelling set up
        with open(self.nlp_words_filepath, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())

if __name__ == "__main__":
    # Can try querying all finished projects in labellingproject or translationlabellingprojects tables 
    #       as candidates for working on
    Labeller(1, "C:\Users\CephJ\Documents\git\bible-insight-server\archive\nlp_words.txt")