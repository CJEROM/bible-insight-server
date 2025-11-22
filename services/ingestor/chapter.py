from bs4 import BeautifulSoup, Tag, NavigableString
import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex
import re
import json
import psycopg2

from paragraph import Paragraph
from verse import Verse
from translationnote import TranslationNote

class Chapter:
    def __init__(self, language_id, translation_id, book_map_id, chapter_ref, chapter_text, db_conn, bible_structure):
        self.language_id = language_id
        self.translation_id = translation_id
        self.book_map_id = book_map_id
        self.chapter_ref = chapter_ref
        self.chapter_xml = BeautifulSoup(chapter_text, "xml")
        self.book_code = chapter_ref.split(" ")[0]

        self.bible_structure = bible_structure

        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()
        
        self.createChapter()
        # Create a Chapter Occurence
        self.cur.execute("""
            SELECT id FROM bible.nodes WHERE book_map_id = %s AND (sid = %s OR eid = %s) AND node_type = 'chapter' ORDER BY id;
        """, (self.book_map_id, self.chapter_ref, self.chapter_ref))
        self.start_node, self.end_node = self.cur.fetchall()

        self.cur.execute("""
            INSERT INTO bible.chapteroccurences (chapter_ref, book_map_id, start_node, end_node) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (self.chapter_ref, self.book_map_id, self.start_node, self.end_node))
        self.chapter_occurence_id = self.cur.fetchone()[0]

        self.conn.commit()

        self.last_verse = self.createVerseOccurences()
        self.createParagraphs()
        self.createTranslationNotes()
        # self.createTokens()

        self.conn.commit()

    # This is to validate the addition of non standard chapters outside the normal 1189 if there are any for a particular translation
    def createChapter(self):
        self.cur.execute("""
            SELECT chapter_ref FROM bible.chapters WHERE chapter_ref = %s
        """, (self.chapter_ref,))
        chapter_found = self.cur.fetchone()

        if chapter_found == None:
            book_code, chapter_num = self.chapter_ref.split(" ")
            self.cur.execute("""
                INSERT INTO bible.chapters (book_code, chapter_num, chapter_ref, standard) 
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (book_code, int(chapter_num), self.chapter_ref, False))
            # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.chapteroccurences",))
            print(f"     Non-Standard Chapter Created: {self.chapter_ref}")

    def createParagraphs(self):
        additions = 0
        # Have to be created here since not all paragraphs fit inside a chapter
        all_paragraphs = self.chapter_xml.find_all("para")
        self.cur.execute("""
            SELECT id FROM bible.nodes WHERE book_map_id = %s AND node_type = 'para' AND id BETWEEN %s AND %s ORDER BY id;
        """, (self.book_map_id, self.start_node, self.end_node))
        para_node_ids = self.cur.fetchall()

        for i, (para) in enumerate(all_paragraphs):
            Paragraph(self.translation_id, para_node_ids[i], para, self.conn)
            additions += 1
        
        if additions > 0:
            # print(f"    [{additions}] Paragraphs added to database")
            pass

    def createVerseOccurences(self):
        additions = 0
        all_verses = self.chapter_xml.find_all("verse")
        latest_ref = None

        for verse in all_verses:
            verse_ref = verse.get("sid")
            if verse_ref:
                Verse(self.chapter_xml, verse_ref, self.chapter_occurence_id, self.conn)
                additions += 1

            latest_ref = verse_ref

        if additions > 0:
            # print(f"    [{additions}] Verse Occurences added to database")
            pass
        return latest_ref # how many verses have been created for this translation

    def standardise_dash(self, ref):
        new_ref = ref
        dash_formats = ["–", "—", "−", "–"] # Different dashes used
        for dash in dash_formats:
            if dash in ref:
                new_ref = ref.replace(dash, "-")

        return new_ref

    def createTranslationNotes(self):
        self.cur.execute("""
            SELECT id FROM bible.nodes WHERE book_map_id = %s AND node_type = 'note' AND id BETWEEN %s AND %s ORDER BY id;
        """, (self.book_map_id, self.start_node, self.end_node))
        translation_note_node_ids = self.cur.fetchall()
        # Go through chapter and grab all cross references and footnotes, and write to database
        for i, this_note in enumerate(self.chapter_xml.find_all("note")):
            TranslationNote(self.book_map_id, self.book_code, self.translation_id, this_note, translation_note_node_ids[i], self.conn)


    # ================================================================================================================= TOKENIZATION LOGIC =================================================================================================================

#region legacy code
    def getParagraphStyle(self, para_style):
        style_file_id = self.cur.execute("""
            SELECT id FROM bible.files WHERE translation_id=? AND type=?
        """, (self.translation_id, "styles")).fetchone()

        versetext = "false"

        if style_file_id != None:
            style = self.db.execute("""
                SELECT versetext FROM Styles WHERE AND style=?
            """, (style_file_id[0], para_style)).fetchone()
            
            if style != None:
                versetext = style[0]

        return versetext == "true"
    
    def loadLanguageLDML(self):
        ldml_content = self.db.execute("""
            SELECT file_content FROM Files WHERE translation_id=? AND type=?
        """, (self.translation_id, "ldml")).fetchone()

        if ldml_content:
            ldml_content = BeautifulSoup(ldml_content[0], 'xml')
        else: 
            return []

        # Extract punctuation tag from file
        punctuation_element = ldml_content.find('exemplarCharacters', {'type': 'punctuation'})
    
        if punctuation_element:
            # Get the text content which contains the punctuation in brackets
            punctuation_text = punctuation_element.get_text()
            
            # Parse the bracket notation to extract individual characters
            punctuation_chars = self.parse_ldml_punctuation(punctuation_text)
            return punctuation_chars
        
        return []# list of punctuation marks
    
    def parse_ldml_punctuation(self, exemplar_text):
        if not exemplar_text.strip():
            return []
    
        # Remove outer brackets
        content = exemplar_text.strip()[1:-1]  # Remove [ and ]
    
        punctuation_chars = []
        i = 0
        
        while i < len(content):
            char = content[i]
            
            if char == '\\' and i + 1 < len(content):
                # Handle escaped characters
                next_char = content[i + 1]
                if next_char == 'u' and i + 5 < len(content):
                    # Unicode escape sequence like \u2019
                    unicode_hex = content[i + 2:i + 6]
                    try:
                        unicode_char = chr(int(unicode_hex, 16))
                        punctuation_chars.append(unicode_char)
                        i += 6
                    except ValueError:
                        punctuation_chars.append(next_char)
                        i += 2
                else:
                    # Regular escape like \: or \-
                    punctuation_chars.append(next_char)
                    i += 2
            elif char == '{' and '}' in content[i:]:
                # Handle multi-character sequences like {...}
                end_brace = content.find('}', i)
                sequence = content[i + 1:end_brace]
                punctuation_chars.append(sequence) # e.g. "..."
                i = end_brace + 1
            elif char not in [' ', '\t', '\n']:
                # Regular character
                punctuation_chars.append(char)
                i += 1
            else:
                i += 1
        
        return punctuation_chars
#endregion