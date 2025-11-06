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
import sys

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

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL")
LABEL_STUDIO_API_TOKEN = os.getenv("LABEL_STUDIO_API_TOKEN")

TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+|[^\w\s]")

class Labeller:
    def __init__(self, nlp_words_filepath, translation_id=None):
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

        self.label_studio_client = None
        self.translation_project = None

        # Should consider how else to do this
        project_label_config = """
        <View>
            <Text name="text" value="$text"/>
            <View style="box-shadow: 2px 2px 5px #999;
                        padding: 20px; margin-top: 2em;
                        border-radius: 5px;">
                <Header value="Choose if entity related"/>
                <Choices name="entity" toName="text"
                        choice="single" showInLine="true">
                <Choice value="Entity Related"/>
                <Choice value="N/A"/>
                </Choices>
            </View>
        </View>
        """

        if self.translation_id == None:
            self.cur.execute("""SELECT id, iso, name FROM bible.languages;""")
            languages = self.cur.fetchall()

            for language_id, iso, name in languages:
                start_time = time.time()
                self.label_studio_client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_TOKEN)

                self.translation_project = self.label_studio_client.projects.create(
                    title=f"{name} Word List Labels",
                    description=f"For Labelling word list of language [{language_id}]",
                    label_config=project_label_config
                )
                
                exports = self.export_word_list(iso)
                duration = round(time.time() - start_time, 2)
                print(f"✅ Migrated [{exports}] Words to DB in {duration} seconds for the [{name}:{language_id}] language!\n")
        else:
            start_time = time.time()
            exports = self.export_word_list()
            duration = round(time.time() - start_time, 2)
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

    def get_book_files(self, language_iso=None):
        if self.translation_id == None:
            # Just grab all book files at ones for language, can label other languages too, so perhaps best to pick by language?
            self.cur.execute("""
                SELECT 
                    btf.book_code,
                    f.etag,
                    f.file_path,
                    f.bucket,
                    tl.translation_id
                FROM bible.translationlabellingprojects tl 
                    JOIN bible.booktofile btf ON tl.translation_id = btf.translation_id
                    JOIN bible.files f ON btf.file_id = f.id
                    JOIN bible.translations t ON tl.translation_id = t.id
                    JOIN bible.translationinfo ti ON t.dbl_id = ti.dbl_id
                    JOIN bible.languages l ON l.id = ti.language_id
                WHERE l.iso = %s;
            """, (language_iso,))
        else:
            self.cur.execute("""
                SELECT 
                    btf.book_code,
                    f.etag,
                    f.file_path,
                    f.bucket,
                    btf.translation_id
                FROM bible.booktofile btf 
                    JOIN bible.files f ON btf.file_id = f.id
                WHERE btf.translation_id = %s;
            """, (self.translation_id,))

        db_books = self.cur.fetchall()
        return db_books

    def get_word_list(self, language_iso):
        db_books = self.get_book_files(language_iso)
        total_books = len(db_books)  # ✅ Needed for proper percentage
        all_tokens = set()
        
        for i, (code, etag, object_name, bucket, translation_id) in enumerate(db_books, start=1):
            book_file_content = self.stream_file(object_name, bucket)
            book_xml = BeautifulSoup(book_file_content, "xml")
            # Go though paragraph by paragraph
            book_text = self.get_para_text(book_xml)

            # ✅ Extract tokens from this book and merge into set
            all_tokens.update(self.get_tokens_without_punctuation(book_text))

            # ✅ Proper loading bar (50 characters wide)
            progress = int((i / total_books) * 50)
            bar = '#' * progress + '-' * (50 - progress)
            percentage = int((i / total_books) * 100)
            sys.stdout.write(f"\rProcessing books: |{bar}| {percentage}%")
            sys.stdout.flush()

        # results = self.get_word_frequencies(self.get_tokens_without_punctuation(language_text))
        return all_tokens

    def export_word_list(self, language_iso=None):
        word_list = self.get_word_list(language_iso)
        nlp_words = self.load_nlp_words(language_iso)
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

                if is_nlp: # if is nlp identified already, then pre label that inside the project so that we don't have to do it again
                    self.label_studio_client.tasks.create(
                        data={
                            "text": word
                        },
                        predictions=[{
                            "result": [
                                {
                                    "from_name": "entity",    # The name of the <Choices> tag
                                    "to_name": "text",        # The name of the <Text> tag
                                    "type": "choices",
                                    "value": {
                                        "choices": ["Entity Related"]   # Pre-selected choice
                                    }
                                }
                            ]
                        }],
                        project=self.translation_project.id,
                    )
                else:
                    self.label_studio_client.tasks.create(
                        data={
                            "text": word
                        },
                        project=self.translation_project.id,
                    )
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
                result = self.cur.fetchone()
                if result:
                    result = result[0]
                else:
                    continue

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
        # Turn into set instead
        return set(TOKEN_PATTERN.findall(text)) # return only unique mentions
    
    def get_tokens_without_punctuation(self, text):
        return [t for t in self.get_tokens(text) if re.match(r"[A-Za-z0-9]", t)]
        # Keeps only words & numbers, removes punctuation

    def get_word_frequencies(self, tokens):
        return Counter(tokens)  # returns a dict-like object with counts

    def load_nlp_words(self, language_iso):
        # These are words that beforehand I have already identified as of interest to my labelling set up
        file_name = f"{language_iso}-nlp-words.txt" if language_iso != None else "nlp-words.txt"
        file_path = Path(self.nlp_words_filepath) / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        else:
            print(f"    {file_path} Not Found => no pre-labelling will occur\n")
            return set()

if __name__ == "__main__":
    # Can try querying all finished projects in labellingproject or translationlabellingprojects tables 
    #       as candidates for working on
    nlp_path = Path(__file__).parents[2] / "archive"
    # Labeller(nlp_file, 1)
    Labeller(nlp_path)