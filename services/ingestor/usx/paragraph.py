from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ingestor.usx.chapter import Chapter
    from manager.logmanager import LogManager

class Paragraph:
    def __init__(self, this_chapter: "Chapter", paragraph_node_id, para_xml, log: "LogManager"):
        self.this_chapter               = this_chapter
        self.this_book                  = self.this_chapter.this_book
        self.metadata                   = self.this_book.metadata

        self.translation_id             = self.metadata.translation_id
        self.paragraph_node_id          = paragraph_node_id
        self.para_xml                   = para_xml

        self.log                        = log
        self.manager                    = self.log.get_manager_handler()
        self.db                         = self.manager.get_db()

        self.paragraph_id               = None
        self.style_id, self.versetext   = self.getParagraphStyle()

        self.read                       = self.metadata.read
        self.write                      = self.metadata.write

        self.createParagraph()

        self.db.commit()

    def getParagraphStyle(self):
        para_style  = self.para_xml.get("style")

        style_id    = self.metadata.styles.get_style_dict()[para_style]["id"]
        versetext   = self.metadata.styles.get_style_dict()[para_style]["versetext"]

        return style_id, versetext
        
    def createParagraph(self):
        self.paragraph_id = self.write.persist_paragraph(
            paragraph_node_id   = self.paragraph_node_id,
            style_id            = self.style_id,
            is_versetext        = self.versetext
            # parent_para         = None
        )
        self.log.log_to_file(f"Created New Paragraph [ID: {self.paragraph_id}] [Verse_Text: {str(self.versetext).capitalize()}]", f"PARAGRAPH", "TRACE")