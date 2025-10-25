from bs4 import BeautifulSoup
import pathlib
import re

import psycopg2
from ingestor.paragraph import Paragraph
from ingestor.chapter import Chapter

# Changing since will only be relevant for text anyway
class Book:
    def __init__(self, language_id, translation_id, book_map_id, file_id, book_string, db_conn):
        self.language_id = language_id
        self.translation_id = translation_id
        self.book_map_id = book_map_id
        self.file_id = file_id
        self.book_xml = BeautifulSoup(book_string, "xml")

        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.cur.execute("""
            SELECT book_code FROM bible.booktofile WHERE id = %s;
        """, (self.book_map_id,))
        self.book_code = self.cur.fetchone()

        self.createParagraphs()
        self.createTextChapters()

        self.conn.commit()
    
    def createParagraphs(self):
        additions = 0
        # Have to be created here since not all paragraphs fit inside a chapter
        all_paragraphs = self.book_xml.find_all("para")

        for para in all_paragraphs:
            Paragraph(self.translation_id, self.file_id, para, self.conn)
            additions += 1
        
        if additions > 0:
            print(f"[{additions}] Paragraphs added to database")

    # Purpose is to split xml up into chapters, for token processing
    def createTextChapters(self):
        additions = 0
        # Grab all chapter_refs for this particular book
        self.cur.execute("""
            SELECT chapter_ref FROM bible.chapters WHERE book_id=?
        """, (self.book_code,))
        all_chapters = self.cur.fetchall()

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

            # Create Chapter Classes
            Chapter(self.language_id, self.translation_id, self.book_id, self.file_id, self.medium, chapter_ref, self.db, chapter_text)
            additions += 1
        
        if additions > 0:
            print(f"[{additions}] Chapters added for {self.book_code}")
   