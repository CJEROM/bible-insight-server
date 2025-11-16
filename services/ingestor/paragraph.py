import psycopg2
from bs4 import BeautifulSoup

class Paragraph:
    def __init__(self, translation_id, paragraph_node_id, para_xml, db_conn):
        self.translation_id = translation_id
        self.paragraph_node_id = paragraph_node_id
        self.para_xml = para_xml

        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.paragraph_id = None
        self.style_id, self.versetext = self.getParagraphStyle()

        self.createParagraph()
        self.createStrongs()

        self.conn.commit()

    def getParagraphStyle(self):
        para_style = self.para_xml.get("style")

        style_id = None
        versetext = False

        self.cur.execute("""
            SELECT id, versetext FROM bible.styles WHERE style=%s
        """, (para_style,))
        style = self.cur.fetchone()
        
        if style != None:
            style_id = style[0]
            versetext = style[1]

        return style_id, versetext

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
        self.cur.execute("""
            INSERT INTO bible.paragraphs (node_id, style_id, parent_para, is_versetext) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (self.paragraph_node_id, self.style_id, None, str(self.para_xml), self.versetext))
        self.paragraph_id = self.cur.fetchone()[0]

    def getVerseForStrongs(self, strong_xml):
        verse_ref = None

        verse_tag = strong_xml.find_next("verse")
        
        if verse_tag != None:
            verse_ref = verse_tag.get("eid") if verse_tag.get("eid") else verse_tag.get("sid")
        
        return verse_ref