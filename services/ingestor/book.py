from bs4 import BeautifulSoup
from pathlib import Path
import re

import psycopg2

from chapter import Chapter

# Changing since will only be relevant for text anyway
class Book:
    def __init__(self, language_id, translation_id, book_map_id, file_id, book_string, db_conn, bible_structure_info):
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
        self.book_code = self.cur.fetchone()[0]

        self.book_structure = self.getBookStructure(bible_structure_info)
        # print(self.book_structure)
        
        self.createTextChapters()

        self.conn.commit()

    def getBookStructure(self, bible_structure_info: str):
        # Go through bible versification
        for line in bible_structure_info.splitlines():
            # if it start with the book_code we are going through
            if line.startswith(self.book_code):
                # Step 1: Remove book abbreviation (first word)
                parts = line.split()
                book = parts[0]         # "1SA"
                chapters = parts[1:]    # ["1:28", "2:36", ..., "31:13"]

                # Step 2: Convert "x:y" into dictionary x -> y where x => "1SA 1" and y => 28
                chapter_dict = {book + " " + ch.split(':')[0]: int(ch.split(':')[1]) for ch in chapters}
                return chapter_dict
            
        return dict() # In case it didn't find it at all return an empty dict

    # Purpose is to split xml up into chapters, for token processing
    def createTextChapters(self):
        additions = 0
        # Grab all chapter_refs for this particular book
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
            if chapter_found == None:
                continue

            # Have to add encapsulating tags, since otherwise only first chapter tag, 
            #       will be included when parsed as xml, ignoring the rest of the text
            chapter_text = """<usx version="3.0">\n"""
            chapter_text += chapter_found.group(0)
            chapter_text += "\n</usx>"

            # Create Chapter Classes
            Chapter(self.language_id, self.translation_id, self.book_map_id, chapter_ref, chapter_text, self.conn, self.book_structure.get(chapter_ref))
            additions += 1

            log_file = Path(__file__).parents[2] / "downloads" / f"translation-{self.translation_id}-log.txt"
            with open(log_file, 'a', encoding="utf-8") as f:
                f.write(f"{chapter_ref}\n")
        
        if additions > 0:
            # print(f"    [{additions}] Chapters added for {self.book_code[0]}")
            pass # Ignore this printing for now to just test what translations are robust enough to work in here and which aren't
   