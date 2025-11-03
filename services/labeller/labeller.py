import spacy
import re
import json
from minio import Minio
import psycopg2
from label_studio_sdk import LabelStudio
from pathlib import Path
from bs4 import BeautifulSoup
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

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

class Labeller:
    def __init__(self, translation_id):
        self.nlp = spacy.load("en_core_web_sm")
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

        self.get_book_files()

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

        results = self.cur.fetchall()
        
        for code, etag, object_name, bucket in results:
            print(self.stream_file(object_name, bucket))
            break

if __name__ == "__main__":
    # Can try querying all finished projects in labellingproject or translationlabellingprojects tables 
    #       as candidates for working on
    Labeller(1)