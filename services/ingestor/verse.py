from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from translation import Translation
    from book import Book
    from chapter import Chapter

class Verse:
    def __init__(self, this_translation: "Translation", this_book: "Book", this_chapter: "Chapter", verse_ref, db_conn, is_special_case=False):
        self.this_translation = this_translation
        self.this_book = this_book
        self.this_chapter = this_chapter

        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.translation_id =       self.this_translation.get_translation_id()
        self.book_map_id =          self.this_book.get_book_map_id()
        self.chapter_occurence_id = self.this_chapter.chapter_occurence_id
        self.verse_ref =            verse_ref
        self.is_special_case =      is_special_case

        self.createVerse()

        self.conn.commit()

        if self.is_special_case == False:
            self.createVerseOccurence()

        self.conn.commit()

    def get_verse_ref(self):
        return self.verse_ref
    
    def get_start_node(self):
        return self.start_node
    
    def get_end_node(self):
        return self.end_node
    
    def get_verse_occurence_id(self):
        return self.verse_occurence_id
    
    def get_start_node_id(self):
        return self.start_node
    
    def get_end_node_id(self):
        return self.end_note
    
    def createVerse(self):
        # Check whether non-standard verse has been added or not
        self.cur.execute("""
            SELECT id FROM bible.verses WHERE verse_ref = %s;
        """, (self.verse_ref,))
        verse_found = self.cur.fetchone()

        if verse_found == None:
            verse_splits = self.verse_ref.split("-")
            chapter_ref, verse_num = verse_splits[0].split(":")
            verse_suffix = self.verse_ref.split(":")[1]

            # Check whether verse_ref is non standard e.g. GEN 1:1-2
            if len(verse_splits) > 1:
                # Create new non standard verse first (to preseve foreign key constraint in db as well before verse occurence created)
                self.cur.execute("""
                    INSERT INTO bible.verses (chapter_ref, verse_ref, standard, verse) 
                    VALUES (%s, %s, %s, %s)
                """, (chapter_ref, self.verse_ref, False, verse_suffix))

                self.this_translation.log_ingestion_activity(f"Created New Verse", f"VERSE: {self.verse_ref}", "DEBUG")

                start_verse = int(verse_num)
                end_verse = int(verse_splits[1]) + 1 # because range is non inclusive
                for verse in range(start_verse, end_verse):
                    new_verse_ref = f"{chapter_ref}:{verse}"
                    self.cur.execute("""
                        INSERT INTO bible.verse_correction (non_standard_verse_ref, verse_ref) 
                        VALUES (%s, %s)
                    """, (self.verse_ref, new_verse_ref))
                    self.this_translation.log_ingestion_activity(f"Created Verse Correction [{new_verse_ref}]", f"VERSE: {self.verse_ref}", "DEBUG")
            
            # Taking account of secondary non standard verse
            if self.verse_ref[-1].isalpha(): # e.g. EXO 28:29a
                self.cur.execute("""
                    INSERT INTO bible.verses (chapter_ref, verse_ref, standard, verse) 
                    VALUES (%s, %s, %s, %s)
                """, (chapter_ref, self.verse_ref, False, verse_suffix))
                self.this_translation.log_ingestion_activity(f"Created New Verse", f"VERSE: {self.verse_ref}", "DEBUG")
                
                new_verse_ref = self.verse_ref[:-1]
                self.cur.execute("""
                    INSERT INTO bible.verse_correction (non_standard_verse_ref, verse_ref) 
                    VALUES (%s, %s)
                """, (self.verse_ref, new_verse_ref))
                self.this_translation.log_ingestion_activity(f"Created Verse Correction [{new_verse_ref}]", f"VERSE: {self.verse_ref}", "DEBUG")

    def createVerseOccurence(self):
        all_vesre_nodes = self.this_book.get_book_nodes().get_verses()[self.verse_ref]
        self.start_node = all_vesre_nodes["sid"]
        self.end_node = all_vesre_nodes["eid"]

        self.cur.execute("""
            INSERT INTO bible.verseoccurences (chapter_id, book_map_id, translation_id, verse_ref, start_node, end_node) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (self.chapter_occurence_id, self.book_map_id, self.translation_id, self.verse_ref, self.start_node, self.end_node))
        self.verse_occurence_id = self.cur.fetchone()[0]

        self.this_translation.log_ingestion_activity(f"Created New Verse Occurence [ID: {self.verse_occurence_id}] [Start Node: {self.start_node}] [End Node: {self.end_node}]", f"VERSE: {self.verse_ref}", "TRACE")