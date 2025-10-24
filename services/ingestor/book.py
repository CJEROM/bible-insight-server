from bs4 import BeautifulSoup
import pathlib
import re

import psycopg2
from ingestor.paragraph import Paragraph
from ingestor.chapter import Chapter

class Book:
    def __init__(self, language_id, translation_id, revision, book_id, file_id, book_string, medium, short_name, long_name):
        self.language_id = language_id
        self.translation_id = translation_id
        self.revision = revision
        self.book_id = book_id
        self.file_id = file_id
        self.book_xml = BeautifulSoup(book_string, "xml")
        self.medium = medium

        self.short_name = short_name
        self.long_name = long_name

        # Adds a database connection
        self.conn = psycopg2.connect(
            host="REDACTED_IP",
            port=5444,
            dbname="postgres",
            user="postgres",
            password="REDACTED_PASSWORD"
        )
        self.cur = self.conn.cursor()

        self.style_file_id = None

        self.checkMedium()

        self.conn.commit()

    def checkMedium(self):
        if self.medium == "text":
            self.createParagraphs()
            self.createTextChapters()
        else:
            return
    
    def createParagraphs(self):
        # Have to be created here since not all paragraphs fit inside a chapter
        all_paragraphs = self.book_xml.find_all("para")

        for para in all_paragraphs:
            Paragraph(self.translation_id, self.file_id, para, self.db)

    # Purpose is to split xml up into chapters, for token processing
    def createTextChapters(self):
        # Grab all chapter_refs for this particular book
        all_chapters = self.db.execute("""
            SELECT chapter_ref FROM Chapters WHERE book_id=?
        """, (self.book_id,)).fetchall()

        for chapter in all_chapters:
            chapter_ref = chapter[0]
            start_tag = self.book_xml.find("chapter", sid=chapter_ref)
            end_tag = self.book_xml.find("chapter", eid=chapter_ref)

            search_string = f"{start_tag}.*{end_tag}"
            chapter_found = re.search(search_string, str(self.book_xml), re.DOTALL)

            # In case of WLC for example, Malachi 4 doesn't exist, so skip over chapter
            #       if it doesn't exist for this book.
            if chapter_found == None:
                continue

            # Have to add encapsulating tags, since otherwise only first chapter tag, 
            #       will be included when parsed as xml, ignoring the rest of the text
            chapter_text = """<usx version="3.0">\n"""
            chapter_text += chapter_found.group(0)
            chapter_text += "\n</usx>"

            # log_path = f"/Users/cepherom/git/bibleSearchTool/logs/{chapter_ref.split(' ')[0]}/"
            # log_file = f"{log_path}{chapter_ref}.xml"
            # pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)
        
            # # For logging purposes to monitor Chapter contents.
            # with open(log_file, 'w') as f:
            #     f.write(chapter_text)
            #     f.write("\n\n")

            # Create Chapter Classes
            Chapter(self.language_id, self.translation_id, self.revision, self.book_id, self.file_id, self.medium, chapter_ref, self.db, chapter_text)
   