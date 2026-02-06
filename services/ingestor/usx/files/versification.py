from ingestor.usx.files.base_file import BaseFile
import re

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class Versification(BaseFile):
    def __init__(self, translation_id: int, main_manager: "ManagerHandler", log: "LogManager", source_id: int | None, file_path: Path = None):
        super.__init__(main_manager, log, source_id, file_path)
        self.translation_id = translation_id
        self.bible_structure_info = None

        self.createVersification()
        self.createVerses(self.bible_structure_info)

    def get_bible_structure_info(self):
        structure = self.bible_structure_info
        # Go through bible versification
        chapter_dict = {}
        for line in structure.splitlines():
            parts = line.split()
            book = parts[0]
            chapters = parts[1:]
            
            for ch in chapters:
                chapter_num, verse_count = ch.split(':')
                chapter_dict[f"{book} {chapter_num}"] = int(verse_count)

        return chapter_dict

    def createVersification(self, file_string):
        # file_xml = BeautifulSoup(file_string, "xml")
        # We can split file string by "#", remove blank ones, then grapb the relevant section
        #       by finding next index after sections we want, then read that line by line for each section

        file_sections_headers = [
            "# Verse number is the maximum verse number for that chapter.",
            "# Mappings from this versification to standard versification",
            "# Excluded verses",
            "# Verse segment information"
        ]
        
        # Build regexes that capture everything between headers (non-greedy, across lines)
        find_bible_info = re.escape(file_sections_headers[0]) + r"(.*?)" + re.escape(file_sections_headers[1])
        find_versification_map = re.escape(file_sections_headers[1]) + r"(.*?)" + re.escape(file_sections_headers[2])
        find_excluded_verses = re.escape(file_sections_headers[2]) + r"(.*?)" + re.escape(file_sections_headers[3])

        # Run searches
        matches = [
            re.search(find_bible_info, file_string, re.DOTALL),
            re.search(find_versification_map, file_string, re.DOTALL),
            re.search(find_excluded_verses, file_string, re.DOTALL)
        ]

        # Extract just the captured groups (excluding headers)
        file_sections = [m.group(1).strip() if m else "" for m in matches]

        self.bible_structure_info = file_sections[0]
        self.createExcludedVerses(file_sections[2])
    
    def createExcludedVerses(self, section_text:str):
        additions = 0
        # Create list of excluded verses
        for line in section_text.splitlines():
            if line.startswith("#! -"):
                verse_ref = line[4:].strip()
                book_code = verse_ref[0:3]

                valid_book = self.read.find_book(book_code=book_code)

                if valid_book == None:
                    continue

                self.write.persist_excluded_verse(
                    verse_ref=verse_ref,
                    translation_id=self.translation_id
                )
                additions+=1
                
                self.log.log_to_file(f"Created Excluded Verse: {verse_ref}", "TRANSLATION", "INFO")

        if additions > 0:
            print(f"    [{additions}] Excluded Verses added to database")

        self.log.log_to_file(f"Created {additions} excluded verses", "TRANSLATION", "INFO")
    
    def createVerses(self, section_text):
        verse_additions = 0
        chapter_additions = 0

        self.log.log_to_file(f"Initializing Verses...", "TRANSLATION", "INFO")
        # Create all Verses Tables instances - different from VerseOccurences, just chceck they all exist
        for line in section_text.splitlines():
            sections = line.split(" ")
            book_code = sections[0]

            book_id = self.read.find_book(book_code=book_code)

            if book_id == None:
                continue

            for chapter in range(1,len(sections)):
                chapter_num, verse_count = sections[chapter].split(":")
                chapter_ref = book_code + " " + chapter_num

                found_chapter = self.read.find_chapter(chapter_ref=chapter_ref)

                # Validates any non standard chapters that might apear outside ones initialised originally
                if found_chapter == None:
                    try:
                        # Basically, all normal Chapters already imported (on DB init), so if one missing its non standard
                        self.write.persist_chapter(
                            book_code=book_code,
                            chapter_num=chapter_num,
                            chapter_ref=chapter_ref,
                            is_standard=False
                        )
                        print(f"     Non-Standard Chapter Created: {chapter_ref}")
                        self.log.log_to_file(f"Created Non-Standard Chapter: {chapter_ref}", "TRANSLATION", "INFO")
                        chapter_additions+=1
                    except Exception as e:
                        print(f"❌ Skipped Chapter Creation of [{chapter_ref}] because of {e}")
                        self.log.log_to_file(f"Skipped Chapter Creation of [{chapter_ref}] because of {e}", "TRANSLATION", "ERROR")
                        # In the case it can't seem to create a new chapter then skip the chapter (won't take it as important)

                for verse in range(1, (int(verse_count)+1)):
                    verse_ref = chapter_ref + ":" + str(verse)

                    verse_id = self.read.find_verse(
                        verse_ref=verse_ref
                    )

                    if verse_id == None:
                        self.write.persist_verse(
                            chapter_ref=chapter_ref,
                            verse_ref=verse_ref,
                            verse=str(verse)
                        )
                        verse_additions += 1
                        self.log.log_to_file(f"Created Verse: {verse_ref}", "TRANSLATION", "TRACE")
        
        if verse_additions > 0:
            print(f"    [{verse_additions}] Verses Initialized into database")
            
        self.log.log_to_file(f"Initialised {verse_additions} Verses!", "TRANSLATION", "INFO")
        self.log.log_to_file(f"Initialised {chapter_additions} Chapters (Non Standard)!", "TRANSLATION", "INFO")