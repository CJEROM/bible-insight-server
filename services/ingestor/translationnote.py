from verse import Verse
from bs4 import BeautifulSoup, Tag
import psycopg2
import re
import os
from pathlib import Path

from dotenv import load_dotenv

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
        break

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

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
        "chapter → footnote": """
            INSERT INTO bible.translationfootnotes (book_map_id, translation_id, chapter_ref, xml, text) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """,
        "verse → footnote": """
            INSERT INTO bible.translationfootnotes (book_map_id, translation_id, verse_ref, xml, text) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """,
        "chapter → chapter": """
            INSERT INTO bible.translationrefnotes (book_map_id, translation_id, from_chapter_ref, to_chapter_ref, xml, parent_ref) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """,
        "verse → chapter": """
            INSERT INTO bible.translationrefnotes (book_map_id, translation_id, from_verse_ref, to_chapter_ref, xml, parent_ref) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """,
        "verse → verse": """
            INSERT INTO bible.translationrefnotes (book_map_id, translation_id, from_verse_ref, to_verse_ref, xml, parent_ref) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """,
        "chapter → verse": """
            INSERT INTO bible.translationrefnotes (book_map_id, translation_id, from_verse_ref, to_chapter_ref, xml, parent_ref) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """,
        "footnote → crossreference": """
            INSERT INTO bible.translation_note_mapping (foot_note, cross_ref) 
            VALUES (%s, %s)
            RETURNING id;
        """,
    }

    def standardise_dash(self, ref):
        new_ref = ref
        dash_formats = ["–", "—", "−", "–"] # Different dashes used
        for dash in dash_formats:
            if dash in ref:
                new_ref = ref.replace(dash, "-")

        return new_ref
    
    def detect_reference_format(self, ref: str):
        patterns = {
            # ❌ Catch invalid (chapter or verse is zero)
            "invalid_zero": r"^[A-Z]{2,4} (\d+:0|\d+:0-\d+|\d+:0-\d+:\d+|0:\d+)", # e.g. GEN 1:0

            # ✅ Valid formats:
            "multi_chapter_range": r"^[A-Z]{2,4} \d+:\d+-\d+:\d+$",     # GEN 1:1-2:1
            "chapter_range": r"^[A-Z]{2,4} \d+-\d+$",                   # GEN 1-2
            "verse_range": r"^[A-Z]{2,4} \d+:\d+-\d+$",                 # GEN 1:1-2
            "single_verse": r"^[A-Z]{2,4} \d+:\d+$",                    # GEN 1:1
            "chapter_only": r"^[A-Z]{2,4} \d+$",                        # GEN 1
        }

        for name, pattern in patterns.items():
            if re.match(pattern, ref):
                return name

        return "unknown_format"
    
    def execute_and_get_id(self, query, params):
        self.cur.execute(query, params)
        return self.cur.fetchone()[0]

    def __init__(self, book_map_id:int, translation_id:int, note_xml:Tag, db_conn, parent_note:int=None, param_note_type:str=None):
        self.book_map_id = book_map_id
        self.translation_id = translation_id
        self.note_xml = note_xml

        self.parent_note = parent_note

        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.note_type = self.get_note_type(param_note_type)
        if self.note_type == None:
            return # if note not valid
        
        self.source_ref = self.get_source_ref()
        
        if self.note_type == "f":
            self.create_footnote()
        elif self.note_type == "x":
            for ref in self.note_xml.find_all("ref"):
                to_ref = self.standardise_dash(ref.get("loc"))
                self.create_cross_references(to_ref, self.note_xml)

        self.conn.commit()

    def get_note_type(self, param_note_type):
        # if passed into class properly then return that
        if param_note_type != None:
            return param_note_type
        
        note_type = None
        
        # if not then figure out from note_xml
        note_style = self.note_xml.get("style")
        if note_style == "f" and self.note_xml.find("char", style="ft"): # footnote with valid footnote text
            note_type = note_style
        elif note_style == "x": # cross reference
            note_type = note_style
        
        return note_type

    def get_source_ref(self):
        self.note_xml.find("char", style="fr")
        self.note_xml.find("char", style="xo")


    def create_footnote(self):
        text = self.note_xml.find("char", style="ft").get_text().strip()

        self.execute_and_get_id(self.SQL.get("chapter → footnote"), (self.book_map_id, self.translation_id, chapter_ref, self.note_xml, text))
        self.execute_and_get_id(self.SQL.get("verse → footnote"), (self.book_map_id, self.translation_id, verse_ref, self.note_xml, text))

        for ref in self.note_xml.find_all("ref"):
            self.create_cross_references(ref, self.note_xml)

        self.execute_and_get_id(self.SQL.get("footnote → crossreference"), (foot_note, cross_ref))
        pass

    def create_cross_references(self, ref, xml):
        to_ref = self.standardise_dash(ref.get("loc"))

        self.execute_and_get_id(self.SQL.get("chapter → chapter"), (self.book_map_id, self.translation_id, from_chapter_ref, to_chapter_ref, xml, self.parent_note))
        self.execute_and_get_id(self.SQL.get("verse → chapter"), (self.book_map_id, self.translation_id, from_verse_ref, to_chapter_ref, xml, self.parent_note))
        self.execute_and_get_id(self.SQL.get("verse → verse"), (self.book_map_id, self.translation_id, from_verse_ref, to_verse_ref, xml, self.parent_note))
        self.execute_and_get_id(self.SQL.get("chapter → verse"), (self.book_map_id, self.translation_id, from_chapter_ref, to_verse_ref, xml, self.parent_note))
        pass

# ✅ Test examples:
tests = {
    "GEN 1": "",        # Valid
    "GEN 10": "",       # Valid
    "GEN 1:1": "",      # Valid
    "GEN 1:10": "",     # Valid
    "GEN 1:1-2": "",    # Valid
    "GEN 1:1-2:3": "",  # Valid
    "GEN 1:0": "",      # ❌ Invalid
    "GEN 0:5": "",      # ❌ Invalid
    "GEN 0": "",        # ❌ Invalid
}

if __name__ == "__main__":
    note_xml = ""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD
    )

    cur = conn.cursor()

    TranslationNote(None, None, note_xml, conn)

    conn.commit()
    cur.close()
    conn.close()