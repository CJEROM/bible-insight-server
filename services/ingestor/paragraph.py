from translation import Translation
from book import Book
from chapter import Chapter

class Paragraph:
    def __init__(self, this_translation: Translation, this_book: Book, this_chapter: Chapter, paragraph_node_id, para_xml, db_conn):
        self.this_translation = this_translation
        self.this_book = this_book
        self.this_chapter = this_chapter

        self.translation_id = self.this_translation.get_translation_id()
        self.paragraph_node_id = paragraph_node_id
        self.para_xml = para_xml

        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.paragraph_id = None
        self.style_id, self.versetext = self.getParagraphStyle()

        self.createParagraph()

        self.conn.commit()

    def get_paragraph_id(self):
        return self.paragraph_id
    
    def get_paragraph_node_id(self):
        return self.paragraph_node_id
    
    def get_verse_text(self):
        return self.versetext
    
    def get_style_id(self):
        return self.style_id

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
        
    def createParagraph(self):
        self.cur.execute("""
            INSERT INTO bible.paragraphs (node_id, style_id, parent_para, is_versetext) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (self.paragraph_node_id, self.style_id, None, self.versetext))
        self.paragraph_id = self.cur.fetchone()[0]
        self.this_translation.log_ingestion_activity(f"Created New Paragraph [ID: {self.paragraph_id}] [Verse_Text: {str(self.versetext).capitalize()}]", f"[PARAGRAPH]", "DEBUG")