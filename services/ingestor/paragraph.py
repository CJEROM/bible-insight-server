import psycopg2
from bs4 import BeautifulSoup
    
class Paragraph:
    def __init__(self, translation_id, book_file_id, para_xml):
        self.translation_id = translation_id
        self.book_file_id = book_file_id
        self.para_xml = para_xml

        # Adds a database connection
        self.conn = psycopg2.connect(
            host="REDACTED_IP",
            port=5444,
            dbname="postgres",
            user="postgres",
            password="REDACTED_PASSWORD"
        )
        self.cur = self.conn.cursor()

        self.paragraph_id = None
        self.style_id, self.versetext = self.getParagraphStyle()

        self.createParagraph()
        self.createStrongs()
        self.linkVerses()

        self.conn.commit()

    def getParagraphStyle(self):
        para_style = self.para_xml.get("style")

        style_file_id = self.db.execute("""
            SELECT id FROM Files WHERE translation_id=? AND type=?
        """, (self.translation_id, "styles")).fetchone()

        style_id = None
        versetext = "false"

        if style_file_id != None:
            style = self.db.execute("""
                SELECT id, versetext FROM Styles WHERE style_file_id=? AND style=?
            """, (style_file_id[0], para_style)).fetchone()
            
            if style != None:
                style_id =  style[0]
                versetext = style[1]

        return style_id, versetext
    
    def linkVerses(self):
        all_verses = self.para_xml.find_all("verse")

        # Add all verses mappings (due to unique constraint wont add duplicates)
        for verse in all_verses:
            verse_ref = verse.get("sid") if verse.get("sid") != None else verse.get("eid")
            self.db.execute("""
                INSERT OR IGNORE INTO VersesToParagraphs (verse_ref, paragraph_id) 
                VALUES (?, ?)
            """, (verse_ref, self.paragraph_id))

    def getParaText(self):
        verse_text_content = ""

        if self.versetext == "true":
            # Creates a copy instead of reference, so when we remove note tags, it doesn't remove them from original xml
            temp_para_xml = BeautifulSoup(str(self.para_xml), "xml")
            # Remove <note> tags completely
            for tag in temp_para_xml.find_all("note"):
                tag.extract()

            verse_text_content = temp_para_xml.get_text().strip()
            
        return verse_text_content
        
    def createParagraph(self):
        chapter_ref = self.para_xml.find_next_sibling("chapter").get("eid")

        chapter_id = self.db.execute("""
            SELECT id FROM Chapters WHERE chapter_ref=?
        """, (chapter_ref,)).fetchone()

        if chapter_id:
            chapter_id = chapter_id[0]

        self.db.execute("""
            INSERT OR IGNORE INTO Paragraphs (book_file_id, chapter_id, style_id, parent_para, xml, versetext) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.book_file_id, chapter_id, self.style_id, None, str(self.para_xml), self.getParaText()))
        self.paragraph_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Paragraphs",)).fetchone()[0]

    def getVerseForStrongs(self, strong_xml):
        verse_ref = None
        verse_id = None

        verse_tag = strong_xml.find_next("verse")
        
        if verse_tag != None:
            verse_ref = verse_tag.get("eid") if verse_tag.get("eid") else verse_tag.get("sid")

        if verse_tag != None:
            verse_id = self.db.execute("""
                SELECT id FROM Verses WHERE verse_ref=?
            """, (verse_ref,)).fetchone()

        if verse_id != None:
            return verse_id[0]
        
        return verse_id

    def createStrongs(self):
        # Get all strongs inside this paragraph
        all_strongs_occurences = self.para_xml.find_all("char", style="w")

        for strong_occurence in all_strongs_occurences:
            # Get strongs number / code
            strong_code = strong_occurence.get("strong")

            # Write any new unique strongs that haven't been added to database yet
            strong_id = self.db.execute("""
                SELECT id FROM Strongs WHERE code=?
            """, (strong_code,)).fetchone()

            if strong_id == None:
                # check what language the code belongs to 
                language_id = None
                if strong_code[0:1] == "G": # Greek
                    language_id = self.db.execute("""
                        SELECT id FROM Languages WHERE name=?
                    """, ("Greek",)).fetchone()
                elif strong_code[0:1] == "H": # Hebrew
                    language_id = self.db.execute("""
                        SELECT id FROM Languages WHERE name=?
                    """, ("Hebrew",)).fetchone()

                if language_id != None:
                    language_id = language_id[0]

                self.db.execute("""
                    INSERT OR IGNORE INTO Strongs (code, language_id) 
                    VALUES (?, ?)
                """, (strong_code, language_id))

            # Create strongs occurence linked to strongs
            self.db.execute("""
                INSERT OR IGNORE INTO StrongsOccurence (content, book_file_id, paragraph_id, verse_id, strong_code) 
                VALUES (?, ?, ?, ?, ?)
            """, (strong_occurence.get_text(), self.book_file_id, self.paragraph_id, self.getVerseForStrongs(strong_occurence), strong_code))