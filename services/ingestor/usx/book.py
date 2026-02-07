from bs4 import BeautifulSoup
import re

from ingestor.usx.chapter import Chapter
from ingestor.usx.nodes import Nodes
from ingestor.usx.files.base_file import BaseFile

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ingestor.usx.files.metadata import Metadata
    from manager.logmanager import LogManager

# Changing since will only be relevant for text anyway
class Book(BaseFile):
    def __init__(self, metadata: "Metadata", book_code, book_map_id, file_id, file_path, log: "LogManager"):
        self.this_file_path     = file_path
        self.log                = log
        self.manager            = self.log.get_manager_handler()
        self.db                 = self.manager.get_db()

        self.metadata           = metadata
        self.read               = metadata.read
        self.write              = metadata.write

        book_string             = self.read_file()

        self.language_id        = self.metadata.language_id
        self.translation_id     = self.metadata.translation_id
        self.book_map_id        = book_map_id
        self.file_id            = file_id
        self.usx                = BeautifulSoup(book_string, "xml")

        self.book_code          = book_code

        self.log.log_to_file(f"Created with [book_map_id:{self.book_map_id}]", f"BOOK: {self.book_code}", "INFO")

        self.book_nodes         = Nodes(self, self.log) # Allows for creating all associated nodes for this book first, before going down the rest of this pipeline
        
        self.createTextChapters()

        self.db.commit()
    
    def get_book_map_id(self):
        return self.book_map_id
    
    def get_book_code(self):
        return self.book_code
    
    def get_book_nodes(self):
        return self.book_nodes

    # Purpose is to split xml up into chapters, for token processing
    def createTextChapters(self):
        additions       = 0
        # Grab all chapter_refs for this particular book from database
        all_chapters    = self.read.get_all_chapters(self.book_code)

        self.log.log_to_file(f"Creating {len(all_chapters)} Chapters", f"BOOK: {self.book_code}", "DEBUG")

        for chapter in all_chapters:
            chapter_ref     = chapter[0]
            start_tag       = self.usx.find("chapter", sid=chapter_ref)
            end_tag         = self.usx.find("chapter", eid=chapter_ref)

            search_string   = f"{start_tag}.*{end_tag}"
            chapter_found   = re.search(search_string, str(self.usx), re.DOTALL)

            # In case of WLC for example, Malachi 4 doesn't exist, so skip over chapter
            #       if it doesn't exist for this book.
            # Should also account for upper range increased due to non standard chapters (skip over them)
            if chapter_found == None:
                self.log.log_to_file(f"Chapter {chapter_ref} invalid, skipping...", f"BOOK: {self.book_code}", "DEBUG")
                continue

            self.log.log_to_file(f"Creating {chapter_ref} as Chapter Found in book: {chapter_found.group(0)}", f"BOOK: {self.book_code}", "TRACE")

            # Have to add encapsulating tags, since otherwise only first chapter tag, 
            #       will be included when parsed as xml, ignoring the rest of the text
            chapter_text    = """<usx version="3.0">\n"""
            chapter_text    += chapter_found.group(0)
            chapter_text    += "\n</usx>"

            # Create Chapter Classes
            Chapter(self, chapter_ref, chapter_text, self.log)
            
            additions       += 1

            self.log.log_to_file(chapter_ref, f"BOOK: {self.book_code}", "TRACE")
        
        if additions > 0:
            # print(f"    [{additions}] Chapters added for {self.book_code}")
            self.log.log_to_file(f"Created {additions} Chapter Occurences!", f"BOOK: {self.book_code}", "INFO")
            pass # Ignore this printing for now to just test what translations are robust enough to work in here and which aren't
   