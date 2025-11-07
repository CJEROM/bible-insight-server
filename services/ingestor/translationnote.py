from verse import Verse
from bs4 import BeautifulSoup, Tag
import psycopg2

class TranslationNote:
    SQL = {
        "": """
            S
        """,
    }

    def __init__(self, book_map_id:int, translation_id:int, note_xml:Tag, db_conn, parent:int=None, note_type:str=None):
        self.book_map_id = book_map_id
        self.translation_id = translation_id
        self.note_xml = note_xml

        self.conn = db_conn
        self.cur = self.conn.cursor()


        
        self.source_ref = None
        self.destination_ref = None

        self.conn.commit()

    def get_note_type(self):
        pass

    def get_source_ref(self):
        pass