from bs4 import BeautifulSoup
import os
import re
import time

from dbmanager import DBManager
from bible.book import Book
from bible.chapter import Chapter

class Translation:
    def __init__(self, translation_path, dbl_id, agreement_id, db: DBManager):
        self.db = db

        # Make passed on variables part of class
        self.translation_path = translation_path
        self.dbl_id = dbl_id
        self.agreement_id = agreement_id
        self.metadata_xml = None

        self.new_translation = False

        # Database References
        self.language_id = None
        self.translation_id = None
        self.revision = None
        self.medium = None

        self.translation_string = ""
        
        self.start_time = time.time()

        self.readMetadata()

        self.db.commit()

    def readFileContents(self, file_path):
        if not os.path.exists(file_path):
            print(file_path + " : Doesn't exist. Writing as blank.")
            return None
        else:
            with open(file_path) as f:
                return f.read()

    def createNewFile(self, type, file_path):
        file_content = ""
        if type != "audio/mpeg":
            file_content = self.readFileContents(self.translation_path + "/" + file_path)

        if file_content == None:
            return None
        
        file_name = file_path.split("/")[-1]

        # Creates link to The Digital Bible Library Link this translation can be downloaded from, 
        #       does not account for revision id tho
        # https://app.library.bible/content/105a06b6146d11e7/download?agreementId=251311 (Example Link)
        source_url = "https://app.library.bible/content/" + self.dbl_id + "/download?agreementId=" + self.agreement_id
        source_id = self.db.execute("SELECT id FROM Sources WHERE url=?", (source_url,)).fetchone()

        if source_id == None:
            self.db.execute("""
                INSERT INTO Sources (url) 
                VALUES (?)
            """, (source_url, ))
            source_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Sources",)).fetchone()[0]
        else:
            source_id = source_id[0]

        self.db.execute("""
            INSERT INTO Files (type, file_name, file_content, translation_id, revision, source_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (type, file_name, file_content, self.translation_id, self.revision, source_id))
        new_file_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Files",)).fetchone()[0]

        if type == "styles":
            self.createStylesAndProperties(file_content, new_file_id)
        elif type == "versification":
            # Get Excluded Verses
            self.createVersification(file_content, new_file_id)

        return new_file_id

    def readMetadata(self):
        # Read metadata file and parse with beautiful soup
        metadata_string = self.readFileContents(self.translation_path + "/metadata.xml")
        self.metadata_xml = BeautifulSoup(metadata_string, "xml")

        # Grab translation revision version
        self.revision = int(self.metadata_xml.find("DBLMetadata").get("revision"))

        # Check for language, if not existing, add to database
        try:
            self.checkLanguage()
        except Exception as e:
            print("At Language Check:", e)

        # Check for translation, if not existing, add to database (with associated files)
        self.checkTranslation()
        if self.translation_id == None:
            self.new_translation = True
            self.createNewTranslation()

            print(f"Started Importing [{self.translation_string}]")

            # Add Metadata file to database
            self.createNewFile("metadata", "metadata.xml")
            # Add License file to database
            self.createNewFile("license", "license.xml")

        if self.new_translation == True:
            # Add Translation Files to database
            if self.medium == "text":
                self.createBibleBooks()
            elif self.medium == "audio":
                self.createBibleChapters()

            self.new_translation = False
            
            duration = round(time.time() - self.start_time, 2)
            print(f"Completed Import of [{self.translation_string}] in {duration} seconds!")
        else: 
            print(f"[{self.translation_string}] already exists in DB with ID: {self.translation_id}")
        
    def checkLanguage(self):
        language_xml = self.metadata_xml.find("language")
        iso = language_xml.find("iso").text

        # Using previously created database connection
        
        self.language_id = self.db.execute("SELECT id FROM Languages WHERE iso=?", (iso,)).fetchone()
        if self.language_id != None:
            self.language_id = self.language_id[0]
        else:
            self.createNewLanguage()
        
    def createNewLanguage(self):
        language_xml = self.metadata_xml.find("language")
        iso = language_xml.find("iso").text
        name = language_xml.find("name").text
        nameLocal = language_xml.find("nameLocal").text
        scriptDirection = language_xml.find("scriptDirection").text

        # Using previously created database connection
        self.db.execute("""
            INSERT INTO Languages (iso, name, nameLocal, scriptDirection) 
            VALUES (?, ?, ?, ?)
        """, (iso, name, nameLocal, scriptDirection))
        self.language_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Languages",)).fetchone()
        if self.language_id != None:
            self.language_id = self.language_id[0]

    def checkTranslation(self):
        # Using previously created database connection
        
        self.translation_id = self.db.execute("SELECT id, abbreviationLocal, name FROM Translations WHERE dbl_id=? AND agreement_id=?", (self.dbl_id,self.agreement_id)).fetchone()

        if self.translation_id != None:
            self.translation_string = f"{self.translation_id[1]}: {self.translation_id[2]}"
            self.translation_id = self.translation_id[0]

    def createNewTranslation(self):
        identification_xml = self.metadata_xml.find("identification")
        description = identification_xml.find("description").text
        publication_xml = self.metadata_xml.find("publication", default="true")
        name = publication_xml.find("name").text
        nameLocal = publication_xml.find("nameLocal").text
        abbreviationLocal = publication_xml.find("abbreviationLocal").text

        self.medium = self.metadata_xml.find("type").find("medium").text

        # dbl_link = "https://app.library.bible/content/" + self.dbl_id + "/download?agreementId=" + self.agreement_id

        self.db.execute("""
            INSERT INTO Translations (dbl_id, agreement_id, medium, name, nameLocal, description, abbreviationLocal, revision, language_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.dbl_id, self.agreement_id, self.medium, name, nameLocal, description, abbreviationLocal, self.revision, self.language_id))
        
        self.translation_string = f"{abbreviationLocal}: {name}"

        self.translation_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=?""", ("Translations",)).fetchone()[0]

        # Here we can create new translation relationship entries
        translation_relationships = self.metadata_xml.find("relationships")
        for relation in translation_relationships.find_all("relation"):
            # Example: <relation id="9879dbb7cfe39e4d" revision="4" type="text" relationType="source"/>
            relation_dbl_id = relation.get("id")
            relation_revision = relation.get("revision")
            relation_type = relation.get("relationType")
            self.db.execute("""
                INSERT INTO TranslationRelationships (from_translation, from_revision, to_translation, to_revision, type) 
                VALUES (?, ?, ?, ?, ?)
            """, (self.translation_id, self.revision, relation_dbl_id, relation_revision, relation_type))

    def createBibleBooks(self):
        publication_xml = self.metadata_xml.find("publication", default="true")
        
        contents = [content for content in publication_xml.find_all("content")]
        resources = self.metadata_xml.find("manifest")
        book_info = self.metadata_xml.find("names")

        # Using previously created database connection

        # Added the extra files as well
        substrings = ["ldml", "styles", "versification"]
        for substring in substrings:
            for resource in resources.find_all("resource"):
                uri = resource['uri']
                if substring in uri:
                    self.createNewFile(substring, uri)

        # Book files
        for book in contents:
            role = book["role"]
            
            curBookId = self.db.execute("""SELECT id FROM Books WHERE code = ? """, (role,)).fetchone()
            # Check if book is part of ones we want to track
            if (curBookId != None):
                curBookId = curBookId[0]
                curBookInfo = book_info.find("name", id=book["name"])
                file_type = resources.find("resource", uri=book["src"]).get("mimeType")
                curBookFileContents = self.readFileContents(self.translation_path + "/" + book["src"])

                # Add files to database
                file_id = self.createNewFile(file_type, book["src"]) # Add file to database

                short_name = curBookInfo.find("short").text
                long_name = curBookInfo.find("long").text

                # Create Book Classes
                Book(self.language_id, self.translation_id, self.revision, curBookId, file_id, curBookFileContents, self.medium, self.db, short_name, long_name)

    def createBibleChapters(self):
        publication_xml = self.metadata_xml.find("publication", id="p1")

        resources = self.metadata_xml.find("manifest")
        book_info = self.metadata_xml.find("names")
            
        # Book files
        for book in publication_xml.find_all("division"):
            # Get first chapter so can find book ref for finding relavant book in database
            book_ref = book.find("content")["role"].split(" ")[0]
            
            curBookId = self.db.execute("""SELECT id FROM Books WHERE code = ? """, (book_ref,)).fetchone()

            # Check if book is part of ones we want to track
            if (curBookId != None):
                curBookId = curBookId[0]
                curBookInfo = book_info.find("name", id=book["name"])

                for chapter in book.find_all("content"):
                    chapter_ref = chapter["role"]
                    #
                    
                    file_type = resources.find("resource", uri=chapter["src"]).get("mimeType")

                    # Add Chapter audio files to database
                    file_id = self.createNewFile(file_type, self.translation_path + "/" + chapter["src"]) # Add file to database

                    short_name = curBookInfo.find("short").text
                    long_name = curBookInfo.find("long").text

                    # Create Chapter Classes
                    Chapter(self.language_id, self.translation_id, self.revision, curBookId, file_id, self.medium, chapter_ref, self.db, None, short_name, long_name)
                
                # Create Book Classes
                Book(self.language_id, self.translation_id, self.revision, curBookId, file_id, None, self.medium, self.db)
        
    def createStylesAndProperties(self, styles_string, styles_file_id):
        # We only set styles and properties once, since it is duplicated across all translations, just usx formatting.
        styles = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=?""", ("Styles",)).fetchone()
        if styles != None:
            return
        
        styles_xml = BeautifulSoup(styles_string, "xml")
        properties = styles_xml.find_all("property")

        previous_style_parent = None
        style_id = None

        for property in properties:
            style_parent = property.find_parent("style")
            
            property_name = property.get("name")
            property_unit = property.get("unit")
            property_value = property.text

            if style_parent == None:
                # General Properties (without a parent style in stylesheet)
                if property_unit != None:
                    self.db.execute("""
                        INSERT INTO Properties (name, value, unit) 
                        VALUES (?, ?, ?)
                    """, (property_name, property_value, property_unit))
                else:
                    self.db.execute("""
                        INSERT INTO Properties (name, value) 
                        VALUES (?, ?)
                    """, (property_name, property_value))

                continue

            if previous_style_parent != style_parent:
                # Create new style
                style = style_parent.get("id")
                style_name = style_parent.find("name").text
                style_description = style_parent.find("description").text
                style_versetext = style_parent.get("versetext")
                style_publishable = style_parent.get("publishable")

                self.db.execute("""
                    INSERT INTO Styles (style, name, description, versetext, publishable, style_file_id) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (style, style_name, style_description, style_versetext, style_publishable, styles_file_id))

                style_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Styles",)).fetchone()[0]

                previous_style_parent = style_parent

            if property_unit != None:
                self.db.execute("""
                    INSERT INTO Properties (name, value, unit, style_id) 
                    VALUES (?, ?, ?, ?)
                """, (property_name, property_value, property_unit, style_id))
            else:
                self.db.execute("""
                    INSERT INTO Properties (name, value, style_id) 
                    VALUES (?, ?, ?)
                """, (property_name, property_value, style_id))

    def createVersification(self, file_string, file_id):
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

        self.createVerses(file_sections[0])
        self.createExcludedVerses(file_sections[2])
    
    def createExcludedVerses(self, section_text):
        # Create list of excluded verses
        for line in section_text.splitlines():
            if line.startswith("#! -"):
                verse_ref = line[4:].strip()
                book_code = verse_ref[0:3]

                valid_book = self.db.execute("""
                    SELECT id FROM Books WHERE code=?
                """, (book_code,)).fetchone()

                if valid_book == None:
                    continue

                self.db.execute("""
                    INSERT INTO ExcludedVerses (verse_ref, translation_id) 
                    VALUES (?, ?)
                """, (verse_ref, self.translation_id))
    
    def createVerses(self, section_text):
        # Create all Verses Tables instances - different from VerseOccurences, just chceck they all exist
        for line in section_text.splitlines():
            sections = line.split(" ")
            book_code = sections[0]

            book_id = self.db.execute("""
                SELECT id FROM Books WHERE code=?
            """, (book_code,)).fetchone()

            if book_id == None:
                continue

            for chapter in range(1,len(sections)):
                chapter_num, verse_count = sections[chapter].split(":")
                for verse in range(1, (int(verse_count)+1)):
                    chapter_ref = book_code + " " + chapter_num
                    verse_ref = chapter_ref + ":" + str(verse)

                    verse_id = self.db.execute("""
                        SELECT id FROM Verses WHERE verse_ref=?
                    """, (verse_ref,)).fetchone()

                    if verse_id == None:
                        self.db.execute("""
                            INSERT INTO Verses (chapter_ref, verse_ref) 
                            VALUES (?, ?)
                        """, (chapter_ref, verse_ref))
