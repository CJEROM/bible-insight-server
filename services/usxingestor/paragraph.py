from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from usxingestor.chapter import Chapter
    from manager.logmanager import LogManager

class Paragraph:
    def __init__(self, this_chapter: "Chapter", paragraph_node_id, para_xml, log: "LogManager"):
        self.this_chapter =         this_chapter
        self.this_book =            self.this_chapter.get_this_book()
        self.this_translation =     self.this_book.get_this_translation()

        self.translation_id = self.this_translation.get_translation_id()
        self.paragraph_node_id = paragraph_node_id
        self.para_xml = para_xml

        self.log = log
        self.manager = self.log.get_manager_handler()
        self.db = self.manager.get_db()

        self.paragraph_id = None
        self.style_id, self.versetext = self.getParagraphStyle()

        self.createParagraph()

        self.db.commit()

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

        style_id = self.this_translation.get_style_dict()[para_style]["id"]
        versetext = self.this_translation.get_style_dict()[para_style]["versetext"]

        return style_id, versetext
        
    def createParagraph(self):
        self.paragraph_id = self.db.fetch_clean_one("""
            INSERT INTO bible.paragraphs (node_id, style_id, parent_para, is_versetext) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (self.paragraph_node_id, self.style_id, None, self.versetext))
        self.log.log_to_file(f"Created New Paragraph [ID: {self.paragraph_id}] [Verse_Text: {str(self.versetext).capitalize()}]", f"PARAGRAPH", "DEBUG")