from bs4 import BeautifulSoup

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ingestor.usx.book import Book
    from manager.logmanager import LogManager

from ingestor.usx.paragraph import Paragraph
from ingestor.usx.verse import Verse
from ingestor.usx.translationnote import TranslationNote

class Chapter:
    def __init__(self, this_book: "Book", chapter_ref, chapter_text, log: "LogManager"):
        self.this_book          = this_book
        self.metadata           = this_book.metadata
        self.read               = this_book.read
        self.write              = this_book.write

        self.log                = log
        self.manager            = self.log.get_manager_handler()
        self.db                 = self.manager.get_db()

        self.language_id        = self.metadata.language_id
        self.translation_id     = self.metadata.translation_id

        self.book_map_id        = self.this_book.book_map_id
        self.book_code          = self.this_book.book_code

        self.chapter_ref        = chapter_ref
        self.chapter_xml        = BeautifulSoup(chapter_text, "xml")
        
        self.createChapter()

        all_chapter_nodes   = self.this_book.book_nodes.get_chapters().get(self.chapter_ref)
        
        if all_chapter_nodes == None:
            self.log.log_to_file(f"Chapter {chapter_ref} invalid, skipping...", f"CHAPTER: {self.chapter_ref}", "DEBUG")
            return
        
        self.start_node     = all_chapter_nodes["sid"]
        self.end_node       = all_chapter_nodes["eid"]

        # Create a Chapter Occurence
        self.chapter_occurence_id = self.write.persist_chapter_occurence(
            chapter_ref     = self.chapter_ref,
            book_map_id     = self.book_map_id,
            translation_id  = self.translation_id,
            start_node      = self.start_node,
            end_node        = self.end_node
        )

        self.log.log_to_file(f"Created Chapter Occurence [ID: {self.chapter_occurence_id}] [Start Node: {self.start_node}] [End Node: {self.end_node}]", f"CHAPTER: {self.chapter_ref}", "DEBUG")

        self.db.commit()

        self.last_verse     = self.createVerseOccurences()

        self.createParagraphs()
        self.createTranslationNotes()

        self.db.commit()

    # This is to validate the addition of non standard chapters outside the normal 1189 if there are any for a particular translation
    def createChapter(self):
        chapter_found = self.read.find_chapter(self.chapter_ref)

        if chapter_found == None:
            book_code, chapter_num = self.chapter_ref.split(" ")

            self.write.persist_chapter(
                book_code       = book_code,
                chapter_num     = int(chapter_num),
                chapter_ref     = self.chapter_ref,
                is_standard     = False
            )

            # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.chapteroccurences",))
            print(f"     Non-Standard Chapter Created: {self.chapter_ref}")
            self.log.log_to_file(f"Created Non-Standard Chapter: {self.chapter_ref}", f"CHAPTER: {self.chapter_ref}", "DEBUG")

    def createParagraphs(self):
        additions       = 0
        # Have to be created here since not all paragraphs fit inside a chapter
        all_paragraphs  = self.chapter_xml.find_all("para")
        para_node_ids   = self.this_book.book_nodes.get_paras().get(self.chapter_ref)

        if all_paragraphs == None or para_node_ids == None:
            self.log.log_to_file(f"No Paragraphs for this Chapter!", f"CHAPTER: {self.chapter_ref}", "DEBUG")
            return

        self.log.log_to_file(f"Creating [{len(para_node_ids)}] Paragraphs ...", f"CHAPTER: {self.chapter_ref}", "INFO")
        self.log.log_to_file(f"Creating With Paragraph Node Ids => {para_node_ids}", f"CHAPTER: {self.chapter_ref}", "TRACE")

        for i, (para) in enumerate(all_paragraphs):
            Paragraph(self, para_node_ids[i], para, self.log)
            additions += 1
        
        if additions > 0:
            # print(f"    [{additions}] Paragraphs added to database")
            self.log.log_to_file(f"Created [{additions}] out of [{len(para_node_ids)}] Paragraphs!", f"CHAPTER: {self.chapter_ref}", "DEBUG")
            pass

    def createVerseOccurences(self):
        additions   = 0
        all_verses  = self.chapter_xml.find_all("verse")

        # Translation Notes aren't guaranteed to be created, so don't create them if they don't exist
        if len(all_verses) == None:
            self.log.log_to_file(f"No Verse Occurences for this Chapter!", f"CHAPTER: {self.chapter_ref}", "DEBUG")
            return

        self.log.log_to_file(f"Creating [{len(all_verses)}] Verse Occurences ...", f"CHAPTER: {self.chapter_ref}", "INFO")

        latest_ref  = None

        for verse in all_verses:
            verse_ref = verse.get("sid")
            if verse_ref:
                Verse(self, verse_ref, self.log)
                additions += 1

            latest_ref = verse_ref

        if additions > 0:
            # print(f"    [{additions}] Verse Occurences added to database")
            pass
        return latest_ref # how many verses have been created for this translation

    def standardise_dash(self, ref: str):
        new_ref         = ref
        dash_formats    = ["–", "—", "−", "–"] # Different dashes used

        for dash in dash_formats:
            if dash in ref:
                new_ref = ref.replace(dash, "-")

        return new_ref

    def createTranslationNotes(self):
        all_note_node_ids = self.this_book.book_nodes.get_notes().get(self.chapter_ref)

        # Translation Notes aren't guaranteed to be created, so don't create them if they don't exist
        if all_note_node_ids == None:
            self.log.log_to_file(f"No Translation Notes for this Chapter!", f"CHAPTER: {self.chapter_ref}", "DEBUG")
            return
        
        self.log.log_to_file(f"Creating [{len(all_note_node_ids)}] Translation Notes ...", f"CHAPTER: {self.chapter_ref}", "INFO")
        self.log.log_to_file(f"Creating Translation Notes Node Ids => {all_note_node_ids}", f"CHAPTER: {self.chapter_ref}", "TRACE")

        # Go through chapter and grab all cross references and footnotes, and write to database
        for i, this_note in enumerate(self.chapter_xml.find_all("note")):
            TranslationNote(self, this_note, all_note_node_ids[i], self.log)
