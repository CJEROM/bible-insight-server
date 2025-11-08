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

    def standardise_ref(self, ref):
        new_ref = ref
        # Removes all non standard dashes with normal one
        dash_formats = ["–", "—", "−", "–"] # Different dashes used
        for dash in dash_formats:
            if dash in ref:
                new_ref = ref.replace(dash, "-")

        # If Chapter-verse divide is full stop replace with a colon
        if ":" not in new_ref:
            new_ref = new_ref.replace(".", ":", 1)

        return new_ref
    
    def detect_reference_format(self, ref):
        options = (None, "chapter", "verse")

        patterns = {
            # ❌ Catch invalid (chapter or verse is zero)
            "invalid_verse":                        [r"^[A-Z]{2,4} \d+:0", (options[1])],              # e.g. PSA 9:0

            "invalid_verse_range":                  [r"^[A-Z]{2,4} \d+:0-\d+", (options[0])],          # e.g. GEN 1:0-3
            "invalid_verse_range_across_chapters":  [r"^[A-Z]{2,4} \d+:0-\d+:\d+", (options[0])],      # e.g. GEN 1:0-2:1
            "invalid_chapter":                      [r"^[A-Z]{2,4} 0:\d+", (options[0])],              # e.g. GEN 0:5

            # Multi Fragment Formats
            "verses_across_chapters_1":     [r"^[A-Z]{2,4} \d+:1-\d+:\d+$", (options[1], options[1], options[2])],      # GEN 1:1-2:13
            "verses_across_chapters_other": [r"^[A-Z]{2,4} \d+:\d+-\d+:\d+$", (options[2], options[1], options[2])],    # 2KI 6:31-7:20

            # Corrective Formats
            "single_verse_alpha":           [r"^[A-Z]{2,4} \d+:\d+[a-z]$", (options[2])],                               # 1KI 7:8a

            # Double Fragmented Formats
            "chapter_range":                [r"^[A-Z]{2,4} \d+-\d+$", (options[1], options[1])],                        # JOS 3-4
            "verse_range":                  [r"^[A-Z]{2,4} \d+:\d+-\d+$", (options[2], options[2])],                    # ISA 28:11-12

            # Simple Formats
            "single_verse":                 [r"^[A-Z]{2,4} \d+:\d+$", (options[2])],                                    # GEN 1:5
            "single_chapter":               [r"^[A-Z]{2,4} \d+$", (options[1])],                                        # GEN 1
        }

        for name, info in patterns.items():
            pattern, format = info
            if re.match(pattern, ref):
                return format, name

        return None, None
    
    def execute_and_get_id(self, query, params):
        self.cur.execute(query, params)
        return self.cur.fetchone()[0]

    def __init__(self, book_map_id:int, book_code:str, translation_id:int, note_xml:Tag, db_conn, param_note_type:str=None):
        self.book_map_id = book_map_id
        self.translation_id = translation_id
        self.note_xml = note_xml

        self.parent_note = None

        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.note_type = self.get_note_type(param_note_type)
        if self.note_type == None:
            return # if note not valid
        
        self.source_book_code = book_code
        self.source_ref, self.source_type = self.get_source_ref()
        
        if self.note_type == "f":
            self.create_footnote()
        elif self.note_type == "x":
            for ref in self.note_xml.find_all("ref"):
                self.create_destination_ref(ref, self.note_xml)

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
        # Get text from note xml to indicate chapter and verse
        note_ref = self.note_xml.find("char", style="fr")
        if note_ref == None:
            note_ref = self.note_xml.find("char", style="xo")
        # Clean up into correct format and then
        cleaned_ref = f"{self.source_book_code} {self.standardise_ref(note_ref)}"

        source_ref = None
        source_type = None

        format, format_name = self.detect_reference_format(cleaned_ref)

        # Source format isn't as extensive as destination format so we want to limit it's expression
        #   To only set up ref like its a single or double format (tho only verse-range accepted), so force ref into that format
        #   Double format will only ever extend another 1 verse, and it migth turn into multi if that's into the next chapter (supress these)

        fragment_format = format[0]
        if fragment_format == None:
            return None
        
        source_type = fragment_format

        if len(format) == 1: # Single Format
            source_ref = cleaned_ref

        elif len(format) == 2: # Double Fragment Format
            if format_name == "verse_range":
                source_ref = cleaned_ref
            else: 
                source_ref = cleaned_ref.split("-")[0] # e.g. JOS 3-4 => JOS 3, we don't accept spanning chapters for source

        elif len(format) == 3: # Multi Fragment Format
            partial_ref = cleaned_ref.split("-")[0] #  e.g. 2KI 6:31-7:20 => 2KI 6:31 OR GEN 1:1-2:13 => GEN 1
            if source_type == "chapter":
                source_ref = partial_ref.split(":")[0]

            elif source_type == "verse":
                source_ref = partial_ref
        
        return source_ref, source_type
    
    def create_destination_ref(self, ref:Tag, xml):
        destination_ref, destination_type = (None, None)

        cleaned_ref = self.standardise_ref(ref.get("loc"))
        ref_book_code, ref_origin = cleaned_ref.split(" ") # e.g GEN 1 => "GEN", "1"

        format_types, format_name = self.detect_reference_format(cleaned_ref)
        if None in format_types: # if there is an invalid reference in format
            return None # don't make a cross reference

        main_note = None # parent note that gets returned for linking to footnote, if cross references created through it

        # Logic for creating fragments for destination references
        if len(format_types) == 1: # Single Format
            destination_ref = cleaned_ref
            destination_type = format_types[0]
            
            main_note = self.create_cross_reference(xml, destination_ref, destination_type)

        elif len(format_types) == 2: # Double Fragment Format
            if format_name == "verse_range": # Verse class robust enough to handle it so just pass along
                destination_type = format_types[0]
                destination_ref = cleaned_ref
                
                self.create_cross_reference(xml, destination_ref, destination_type)
            else:  # currently only have chapter range so this is tailored to that
                start_range, end_range = ref_origin.split("-")
                start_chapter = int(start_range.split(":")[0])
                end_chapter = int(end_range.split(":")[0])

                for chapter in range(start_chapter, end_chapter+1):
                    destination_ref = f"{ref_book_code} {chapter}"
                    if chapter == start_chapter:
                        destination_type = format_types[0]

                        main_note = self.create_cross_reference(xml, destination_ref, destination_type)
                        self.parent_note = main_note
                    else:
                        destination_type = format_types[1]
                
                        self.create_cross_reference(xml, destination_ref, destination_type)

        elif len(format_types) == 3: # Multi Fragment Format
            start_range, end_range = ref_origin.split("-")
            start_chapter = int(start_range.split(":")[0])
            end_chapter = int(end_range.split(":")[0])

            for chapter in range(start_chapter, end_chapter+1):
                if chapter == start_chapter:
                    destination_type = format_types[0]
                    if destination_type == "chapter":
                        destination_ref = f"{ref_book_code} {chapter}"
                    elif destination_type == "verse":
                        destination_ref = f"{ref_book_code} {start_range}"

                    main_note = self.create_cross_reference(xml, destination_ref, destination_type)
                    self.parent_note = main_note
                elif chapter == end_chapter:
                    destination_type = format_types[2]
                    if destination_type == "chapter":
                        destination_ref = f"{ref_book_code} {chapter}"
                    elif destination_type == "verse":
                        destination_ref = f"{ref_book_code} {end_range}"

                    self.create_cross_reference(xml, destination_ref, destination_type)
                else:
                    destination_type = format_types[1]
                    destination_ref = f"{ref_book_code} {chapter}"

                    self.create_cross_reference(xml, destination_ref, destination_type)

        self.parent_note = None

        # only first fragment is returned, since the others link to first fragment as parent
        return main_note

    def create_footnote(self):
        text = self.note_xml.find("char", style="ft").get_text().strip()
        footnote_id = None

        # Simpler logic since can only have foot note for a chapter "PSA 46" or verse "LUK 1:17", (verse can be non-standard "MIC 4:14a" or mixed "MAT 12:18-21")
        if self.source_type == "verse":
            footnote_id = self.execute_and_get_id(self.SQL.get("verse → footnote"), (self.book_map_id, self.translation_id, self.source_ref, self.note_xml, text))
        elif self.source_type == "chapter":
            footnote_id = self.execute_and_get_id(self.SQL.get("chapter → footnote"), (self.book_map_id, self.translation_id, self.source_ref, self.note_xml, text))

        for ref in self.note_xml.find_all("ref"):
            cross_reference_id = self.create_destination_ref(ref, self.note_xml)
            self.execute_and_get_id(self.SQL.get("footnote → crossreference"), (footnote_id, cross_reference_id))

    def create_cross_reference(self, xml, destination_ref, destination_type):
        query = None

        if self.source_type == "verse" and destination_type == "chapter":
            query = self.SQL.get("verse → chapter")
        elif self.source_type == "verse" and destination_type == "verse":
            query = self.SQL.get("verse → verse")
        elif self.source_type == "chapter" and destination_type == "chapter":
            query = self.SQL.get("chapter → chapter")
        elif self.source_type == "chapter" and destination_type == "verse":
            query = self.SQL.get("chapter → verse")

        cross_reference_id = self.execute_and_get_id(query, (self.book_map_id, self.translation_id, self.source_ref, destination_ref, xml, self.parent_note))
        return cross_reference_id

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