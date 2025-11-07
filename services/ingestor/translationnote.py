from verse import Verse
from bs4 import BeautifulSoup, Tag
import psycopg2

#region Cases To Handle (both from source and for destination for both cross references and footnotes)
# 2KI 6:31-7:20
# COL 2:47-3:1
# PSA 9:0
# ISA 28:11-12
# 1KI 7:8a
# JOS 3-4
#endregion

#region Footnotes Samples

    # <note caller="+" style="f"><char style="fr" closed="false">1:17 </char><char style="ft" closed="false">orthodox Jewish</char></note>

    # <note caller="+" style="f">
    #     <char style="fr" closed="false">1:17 </char><char style="ft" closed="false">
    #         <char style="xt">
    #             <ref loc="2CO 5:21">2C 5:21</ref>; 
    #             <ref loc="ROM 8:4">Ro 8:4</ref>; 
    #             <ref loc="PHP 3:9">Pp 3:9</ref>
    #         </char>
    #     </char>
    # </note>

    # <note caller="+" style="f"><char style="fr" closed="false">1:17 </char><char style="ft" closed="false">orthodox Jewish</char></note>

#endregion

#region Cross reference Samples

    # <note caller="-" style="x"><char style="xo" closed="false">1:1 </char><char style="xt" closed="false"><ref loc="PSA 51:10">Ps 51:10</ref></char></note>

#endregion

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