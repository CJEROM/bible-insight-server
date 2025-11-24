from bs4 import BeautifulSoup
from pathlib import Path
import re
import datetime

import psycopg2

from translation import Translation
from chapter import Chapter
from nodes import Nodes

# Changing since will only be relevant for text anyway
class Book:
    def __init__(self, this_translation: Translation, book_code, book_map_id, file_id, book_string, db_conn):
        self.this_translation = this_translation

        self.language_id =      self.this_translation.get_language_id()
        self.translation_id =   self.this_translation.get_translation_id()
        self.book_map_id =      book_map_id
        self.file_id =          file_id
        self.book_xml =         BeautifulSoup(book_string, "xml")

        # Adds a database connection
        self.conn =             db_conn
        self.cur =              self.conn.cursor()

        self.book_code =        book_code

        self.this_translation.log_ingestion_activity(f"Created with book_map_id:{self.book_map_id}", book_code, "INFO")

        self.book_nodes =       Nodes(book_map_id, db_conn, book_string) # Allows for creating all associated nodes for this book first, before going down the rest of this pipeline
        
        self.createTextChapters()

        self.conn.commit()

    def get_book_xml(self):
        return self.book_xml
    
    def get_book_map_id(self):
        return self.book_map_id
    
    def get_book_code(self):
        return self.book_code
    
    def get_book_nodes(self):
        return self.book_nodes

    # Purpose is to split xml up into chapters, for token processing
    def createTextChapters(self):
        additions = 0
        # Grab all chapter_refs for this particular book from database
        self.cur.execute("""
            SELECT chapter_ref FROM bible.chapters WHERE book_code=%s
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
            # Should also account for upper range increased due to non standard chapters (skip over them)
            if chapter_found == None:
                continue

            # Have to add encapsulating tags, since otherwise only first chapter tag, 
            #       will be included when parsed as xml, ignoring the rest of the text
            chapter_text = """<usx version="3.0">\n"""
            chapter_text += chapter_found.group(0)
            chapter_text += "\n</usx>"

            # Create Chapter Classes
            Chapter(self.this_translation, self, chapter_ref, chapter_text, self.conn)
            additions += 1

            self.this_translation.log_ingestion_activity(chapter_ref, "BOOK", "INFO")
        
        if additions > 0:
            # print(f"    [{additions}] Chapters added for {self.book_code[0]}")
            pass # Ignore this printing for now to just test what translations are robust enough to work in here and which aren't
   