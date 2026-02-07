from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ingestor.usx.chapter import Chapter
    from manager.logmanager import LogManager

class Verse:
    def __init__(self, this_chapter: "Chapter", verse_ref: str, log: "LogManager", is_special_case=False):
        self.this_chapter           = this_chapter
        self.this_book              = self.this_chapter.get_this_book()
        self.metadata               = self.this_book.metadata

        self.log                    = log
        self.manager                = self.log.get_manager_handler()
        self.db                     = self.manager.get_db()

        self.translation_id         = self.metadata.translation_id
        self.book_map_id            = self.this_book.book_map_id
        self.chapter_occurence_id   = self.this_chapter.chapter_occurence_id
        self.verse_ref              = verse_ref
        self.is_special_case        = is_special_case

        self.read                   = self.metadata.read
        self.write                  = self.metadata.write

        self.createVerse()

        self.db.commit()

        if self.is_special_case == False:
            self.createVerseOccurence()

        self.db.commit()
    
    def createVerse(self):
        # Check whether non-standard verse has been added or not
        verse_found = self.db.fetch_one("""
            SELECT id FROM bible.verses WHERE verse_ref = %s;
        """, (self.verse_ref,))

        if verse_found == None:
            verse_splits            = self.verse_ref.split("-")
            chapter_ref, verse_num  = verse_splits[0].split(":")
            verse_suffix            = self.verse_ref.split(":")[1]

            # Check whether verse_ref is non standard e.g. GEN 1:1-2
            if len(verse_splits) > 1:
                # Create new non standard verse first (to preseve foreign key constraint in db as well before verse occurence created)
                self.write.persist_verse(
                    chapter_ref     = chapter_ref,
                    verse_ref       = self.verse_ref,
                    verse           = verse_suffix,
                    is_standard     = False
                )

                self.log.log_to_file(f"Created New Verse", f"VERSE: {self.verse_ref}", "DEBUG")

                start_verse = int(verse_num)
                end_verse = int(verse_splits[1]) + 1 # because range is non inclusive

                for verse in range(start_verse, end_verse):
                    new_verse_ref = f"{chapter_ref}:{verse}"

                    self.write.persist_verse_correction(
                        non_standard_verse_ref  = self.verse_ref,
                        verse_ref               = new_verse_ref
                    )
                    self.log.log_to_file(f"Created Verse Correction [{new_verse_ref}]", f"VERSE: {self.verse_ref}", "DEBUG")
            
            # Taking account of secondary non standard verse
            if self.verse_ref[-1].isalpha(): # e.g. EXO 28:29a

                self.write.persist_verse(
                    chapter_ref     = chapter_ref,
                    verse_ref       = self.verse_ref,
                    verse           = verse_suffix,
                    is_standard     = False
                )
                self.log.log_to_file(f"Created New Verse", f"VERSE: {self.verse_ref}", "DEBUG")
                
                new_verse_ref = self.verse_ref[:-1]

                self.write.persist_verse_correction(
                    non_standard_verse_ref  = self.verse_ref,
                    verse_ref               = new_verse_ref
                )
                self.log.log_to_file(f"Created Verse Correction [{new_verse_ref}]", f"VERSE: {self.verse_ref}", "DEBUG")

    def createVerseOccurence(self):
        all_vesre_nodes     = self.this_book.book_nodes.get_verses()[self.verse_ref]
        self.start_node     = all_vesre_nodes["sid"]
        self.end_node       = all_vesre_nodes["eid"]

        self.verse_occurence_id = self.write.persist_verse_occurence(
            chapter_id      = self.chapter_occurence_id,
            book_map_id     = self.book_map_id,
            translation_id  = self.translation_id,
            verse_ref       = self.verse_ref,
            start_node      = self.start_node,
            end_node        = self.end_node
        )

        self.log.log_to_file(f"Created New Verse Occurence [ID: {self.verse_occurence_id}] [Start Node: {self.start_node}] [End Node: {self.end_node}]", f"VERSE: {self.verse_ref}", "TRACE")