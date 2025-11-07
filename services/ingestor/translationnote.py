from verse import Verse
from bs4 import BeautifulSoup, Tag
import psycopg2

class TranslationNote:
    SQL = {
        "": """
            S
        """,
    }

    def standardise_dash(self, ref):
        new_ref = ref
        dash_formats = ["–", "—", "−", "–"] # Different dashes used
        for dash in dash_formats:
            if dash in ref:
                new_ref = ref.replace(dash, "-")

        return new_ref

    def __init__(self, book_map_id:int, translation_id:int, note_xml:Tag, db_conn, parent:int=None, param_note_type:str=None):
        self.book_map_id = book_map_id
        self.translation_id = translation_id
        self.note_xml = note_xml

        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.note_type = self.get_note_type(param_note_type)
        if self.note_type == None:
            return # if note not valid

        
        self.source_ref = None
        self.destination_ref = None

        self.conn.commit()

    def get_note_type(self, param_note_type):
        # if passed into class properly then return that
        if param_note_type != None:
            return param_note_type
        
        # if not then figure out from note_xml
        note_style = self.note_xml.get("style")
        if note_style == "f": # footnote
            pass
        if note_style == "x": # cross reference
            pass
        pass

    def get_source_ref(self):
        pass