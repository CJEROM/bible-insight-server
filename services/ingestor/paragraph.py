import psycopg2
from bs4 import BeautifulSoup

class Paragraph:
    def __init__(self, translation_id, book_map_id, para_xml, db_conn):
        self.translation_id = translation_id
        self.book_map_id = book_map_id
        self.para_xml = para_xml

        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.paragraph_id = None
        self.style_id, self.versetext = self.getParagraphStyle()

        self.createParagraph()
        self.createStrongs()
        self.linkVerses()

        self.conn.commit()

    def getParagraphStyle(self):
        para_style = self.para_xml.get("style")

        style_id = None
        versetext = "false"

        self.cur.execute("""
            SELECT id, versetext FROM bible.styles WHERE style=%s
        """, (para_style,))
        style = self.cur.fetchone()
        
        if style != None:
            style_id = style[0]
            versetext = style[1]

        return style_id, versetext
    
    def linkVerses(self):
        all_verses = self.para_xml.find_all("verse")

        # Add all verses mappings (due to unique constraint wont add duplicates)
        for verse in all_verses:
            verse_ref = verse.get("sid") if verse.get("sid") != None else verse.get("eid")
            self.cur.execute("""
                INSERT OR IGNORE INTO VersesToParagraphs (verse_ref, paragraph_id) 
                VALUES (?, ?)
            """, (verse_ref, self.paragraph_id))

    def getParaText(self):
        verse_text_content = ""

        if self.versetext:
            # Creates a copy instead of reference, so when we remove note tags, it doesn't remove them from original xml
            temp_para_xml = BeautifulSoup(str(self.para_xml), "xml")
            # Remove <note> tags completely
            for tag in temp_para_xml.find_all("note"):
                tag.extract()

            verse_text_content = temp_para_xml.get_text().strip()
            
        return verse_text_content
        
    def createParagraph(self):
        chapter_ref = self.para_xml.find_next_sibling("chapter").get("eid")

        self.cur.execute("""
            SELECT id FROM bible.chapters WHERE chapter_ref=%s
        """, (chapter_ref,))

        chapter_id = self.cur.fetchone()

        if chapter_id:
            chapter_id = chapter_id[0]

        self.cur.execute("""
            INSERT INTO Paragraphs (book_file_id, chapter_id, style_id, parent_para, xml, versetext) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (self.book_file_id, chapter_id, self.style_id, None, str(self.para_xml), self.getParaText()))
        self.cur.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Paragraphs",))
        self.paragraph_id = self.cur.fetchone()[0]

    def getVerseForStrongs(self, strong_xml):
        verse_ref = None
        verse_id = None

        verse_tag = strong_xml.find_next("verse")
        
        if verse_tag != None:
            verse_ref = verse_tag.get("eid") if verse_tag.get("eid") else verse_tag.get("sid")

        if verse_tag != None:
            self.cur.execute("""
                SELECT id FROM Verses WHERE verse_ref=%s
            """, (verse_ref,))
            verse_id = self.cur.fetchone()

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
            self.cur.execute("""
                SELECT id FROM bible.strongs WHERE code=%s
            """, (strong_code,))
            strong_id = self.cur.fetchone()

            if strong_id == None:
                # check what language the code belongs to 
                language_id = None
                if strong_code[0:1] == "G": # Greek
                    self.cur.execute("""
                        SELECT id FROM bible.languages WHERE name=%s
                    """, ("Greek",))
                    language_id = self.cur.fetchone()
                elif strong_code[0:1] == "H": # Hebrew
                    self.cur.execute("""
                        SELECT id FROM bible.languages WHERE name=%s
                    """, ("Hebrew",))
                    language_id = self.cur.fetchone()

                if language_id != None:
                    language_id = language_id[0]

                self.cur.execute("""
                    INSERT OR IGNORE INTO bible.strongs (code, language_id) 
                    VALUES (%s, %s)
                """, (strong_code, language_id))

            # Create strongs occurence linked to strongs
            self.cur.execute("""
                INSERT OR IGNORE INTO bible.strongsoccurence (content, -, paragraph_id, verse_id, strong_code) 
                VALUES (%s, %s, %s, %s, %s)
            """, (strong_occurence.get_text(), self.book_file_id, self.paragraph_id, self.getVerseForStrongs(strong_occurence), strong_code))