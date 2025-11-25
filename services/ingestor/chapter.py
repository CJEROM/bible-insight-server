from bs4 import BeautifulSoup

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from translation import Translation
    from book import Book

from paragraph import Paragraph
from verse import Verse
from translationnote import TranslationNote

class Chapter:
    def __init__(self, this_translation: "Translation", this_book: "Book", chapter_ref, chapter_text, db_conn):
        self.this_translation = this_translation
        self.this_book =        this_book

        self.language_id =      self.this_translation.get_language_id()
        self.translation_id =   self.this_translation.get_translation_id()

        self.book_map_id =      self.this_book.get_book_map_id()
        self.book_code =        self.this_book.get_book_code()

        self.chapter_ref =      chapter_ref
        self.chapter_xml =      BeautifulSoup(chapter_text, "xml")

        self.bible_structure =  self.this_translation.get_bible_structure_info()

        # Adds a database connection
        self.conn =             db_conn
        self.cur =              self.conn.cursor()
        
        self.createChapter()

        self.start_node = self.this_book.get_book_nodes().get_chapters()[self.chapter_ref]["sid"]
        self.end_node = self.this_book.get_book_nodes().get_chapters()[self.chapter_ref]["eid"]

        # Create a Chapter Occurence
        self.cur.execute("""
            INSERT INTO bible.chapteroccurences (chapter_ref, book_map_id, start_node, end_node) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (self.chapter_ref, self.book_map_id, self.start_node, self.end_node))
        self.chapter_occurence_id = self.cur.fetchone()[0]

        self.this_translation.log_ingestion_activity(f"Created Chapter Occurence [ID: {self.chapter_occurence_id}] [Start Node: {self.start_node}] [End Node: {self.start_node}]", f"[CHAPTER: {self.chapter_ref}]", "DEBUG")

        self.conn.commit()

        self.last_verse =       self.createVerseOccurences()
        self.createParagraphs()
        self.createTranslationNotes()

        self.conn.commit()

    def get_chapter_ref(self):
        return self.chapter_ref
    
    def get_start_node(self):
        return self.start_node
    
    def get_end_node(self):
        return self.end_node
    
    def get_chapter_occurence_id(self):
        return self.book_code

    # This is to validate the addition of non standard chapters outside the normal 1189 if there are any for a particular translation
    def createChapter(self):
        self.cur.execute("""
            SELECT chapter_ref FROM bible.chapters WHERE chapter_ref = %s
        """, (self.chapter_ref,))
        chapter_found = self.cur.fetchone()

        if chapter_found == None:
            book_code, chapter_num = self.chapter_ref.split(" ")
            self.cur.execute("""
                INSERT INTO bible.chapters (book_code, chapter_num, chapter_ref, standard) 
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (book_code, int(chapter_num), self.chapter_ref, False))
            # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.chapteroccurences",))
            print(f"     Non-Standard Chapter Created: {self.chapter_ref}")
            self.this_translation.log_ingestion_activity(f"Created Non-Standard Chapter: {self.chapter_ref}", f"[CHAPTER: {self.chapter_ref}]", "DEBUG")

    def createParagraphs(self):
        additions = 0
        # Have to be created here since not all paragraphs fit inside a chapter
        all_paragraphs = self.chapter_xml.find_all("para")
        para_node_ids = self.this_book.get_book_nodes().get_paras()

        self.this_translation.log_ingestion_activity(f"Creating [{len(para_node_ids)}] Paragraphs ...", f"[CHAPTER: {self.chapter_ref}]", "INFO")

        for i, (para) in enumerate(all_paragraphs):
            Paragraph(self.this_translation, self.this_book, self, para_node_ids[i], para, self.conn)
            additions += 1
        
        if additions > 0:
            # print(f"    [{additions}] Paragraphs added to database")
            self.this_translation.log_ingestion_activity(f"Created [{additions}] out of [{len(para_node_ids)}] Paragraphs!", f"[CHAPTER: {self.chapter_ref}]", "INFO")
            pass

    def createVerseOccurences(self):
        additions = 0
        all_verses = self.chapter_xml.find_all("verse")

        self.this_translation.log_ingestion_activity(f"Creating [{len(all_verses)}] Verse Occurences ...", f"[CHAPTER: {self.chapter_ref}]", "INFO")

        latest_ref = None

        for verse in all_verses:
            verse_ref = verse.get("sid")
            if verse_ref:
                Verse(self.this_translation, self.this_book, self, verse_ref, self.conn)
                additions += 1

            latest_ref = verse_ref

        if additions > 0:
            # print(f"    [{additions}] Verse Occurences added to database")
            pass
        return latest_ref # how many verses have been created for this translation

    def standardise_dash(self, ref):
        new_ref = ref
        dash_formats = ["–", "—", "−", "–"] # Different dashes used
        for dash in dash_formats:
            if dash in ref:
                new_ref = ref.replace(dash, "-")

        return new_ref

    def createTranslationNotes(self):
        all_note_node_ids = self.this_book.get_book_nodes().get_notes()[self.chapter_ref]
        self.this_translation.log_ingestion_activity(f"Creating [{len(all_note_node_ids)}] Translation Notes ...", f"[CHAPTER: {self.chapter_ref}]", "INFO")

        # Go through chapter and grab all cross references and footnotes, and write to database
        for i, this_note in enumerate(self.chapter_xml.find_all("note")):
            TranslationNote(self.this_translation, self.this_book, self, this_note, all_note_node_ids[i], self.conn)
