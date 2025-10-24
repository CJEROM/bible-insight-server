from bs4 import BeautifulSoup, Tag, NavigableString
import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex
import re
import json
import pathlib

from dbmanager import DBManager

from ingestor.verse import Verse

# Spacy packages need to be installed, so need to account for storage space for these:
# To Install a package run the following command:
#       python3 -m spacy download en_core_web_lg 

# Where "en" can be replaced by any other language code below => See also https://spacy.io/usage/models#section-languages 
# where "lg" can be replaced by ["sm" ,"md", "lg", "trf"] => See https://spacy.io/models/en

# Hebrew has no trained packages so no tokenisation
# Need to change map to consider this
# Add Validation to check for existence of key

# mapping of language name to spacy equivalent for package import - only for supported languages
language_code_map = {
    "Catalan": "ca",
    "Chinese": "zh",
    "Croatian": "hr",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",            # ENGLISH
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Greek": "el",              # GREEK
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Lithuanian": "lt",
    "Macedonian": "mk",
    "Multi-language": "xx",
    "Norwegian Bokmål": "nb",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Slovenian": "sl",
    "Spanish": "es",
    "Swedish": "sv",
    "Ukrainian": "uk",
    "Afrikaans": "af",
    "Albanian": "sq",
    "Amharic": "am",
    "Ancient Greek": "grc",     # ANCIENT GREEK
    "Greek, Ancient": "grc",    # ANCIENT GREEK
    "Arabic": "ar",
    "Armenian": "hy",
    "Azerbaijani": "az",
    "Basque": "eu",
    "Bengali": "bn",
    "Bulgarian": "bg",
    "Czech": "cs",
    "Estonian": "et",
    "Faroese": "fo",
    "Gujarati": "gu",
    "Hebrew": "he",             # HEBREW
    "Hindi": "hi",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Indonesian": "id",
    "Irish": "ga",
    "Kannada": "kn",
    "Kyrgyz": "ky",
    "Latin": "la",
    "Latvian": "lv",
    "Ligurian": "lij",
    "Lower Sorbian": "dsb",
    "Luganda": "lg",
    "Luxembourgish": "lb",
    "Malay": "ms",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Nepali": "ne",
    "Norwegian Nynorsk": "nn",
    "Persian": "fa",
    "Sanskrit": "sa",
    "Serbian": "sr",
    "Setswana": "tn",
    "Sinhala": "si",
    "Slovak": "sk",
    "Tagalog": "tl",
    "Tamil": "ta",
    "Tatar": "tt",
    "Telugu": "te",
    "Thai": "th",
    "Tigrinya": "ti",
    "Turkish": "tr",
    "Upper Sorbian": "hsb",
    "Urdu": "ur",
    "Vietnamese": "vi",
    "Yoruba": "yo"
}

class Chapter:
    def __init__(self, language_id, translation_id, revision, book_id, file_id, medium, chapter_ref, db: DBManager, chapter_text):
        self.language_id = language_id
        self.translation_id = translation_id
        self.revision = revision
        self.book_id = book_id
        self.file_id = file_id
        self.medium = medium
        self.chapter_ref = chapter_ref
        self.chapter_xml = BeautifulSoup(chapter_text, "xml")

        self.db = db

        self.chapter_id = self.getChapterID()

        self.checkMedium()

        self.db.commit()

    def checkMedium(self):
        if self.medium == "audio":
            # Create a Chapter Occurence if chapter id exists
            self.db.execute("""
                INSERT INTO ChapterOccurences (chapter_id, chapter_file_id) 
                VALUES (?, ?)
            """, (self.chapter_id, self.file_id))
        else:
            # Create a Chapter Occurence if chapter id exists
            self.db.execute("""
                INSERT INTO ChapterOccurences (chapter_id, book_file_id) 
                VALUES (?, ?)
            """, (self.chapter_id, self.file_id))
            self.createVerseOccurences()
            self.createTokens()

    def createVerseOccurences(self):
        all_verses = self.chapter_xml.find_all("verse")

        for verse in all_verses:
            verse_ref = verse.get("sid")
            if verse_ref:
                Verse(self.db, self.chapter_xml, verse_ref, self.file_id)
        
    def getChapterID(self):
        # cursor.execute("""SELECT seq FROM sqlite_sequence WHERE name = "Translations" """)
        chapter_id = self.db.execute("""SELECT id FROM Chapters WHERE chapter_ref=? """, (self.chapter_ref,)).fetchone()

        if chapter_id:
            return chapter_id[0]
        
        return chapter_id

    def getParagraphStyle(self, para_style):
        style_file_id = self.db.execute("""
            SELECT id FROM Files WHERE translation_id=? AND type=?
        """, (self.translation_id, "styles")).fetchone()

        versetext = "false"

        if style_file_id != None:
            style = self.db.execute("""
                SELECT versetext FROM Styles WHERE style_file_id=? AND style=?
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
    
    def createTokens(self):
        # Make sure to commit anything not written to the database so far before we start processing tokens
        self.db.commit()

        language_name = self.db.execute("""
            SELECT name FROM Languages WHERE id=?
        """, (self.language_id,)).fetchone()

        # Figure out language code and if supported by spacy for tokenisation
        spacy_language_code = ""
        if language_name != None:
            language_name = language_name[0]
            spacy_language_code = ""

            try:
                spacy_language_code = language_code_map[language_name]
            except Exception as e:
                # If I can't find this then return
                return

            if len(spacy_language_code) == 0:
                return
        else:
            return
        
        # if supported, then initialise spacy and allow for tokenisation
        nlp = None
        try:
            nlp = spacy.load(f"{spacy_language_code}_core_web_lg")
        except Exception as e:
            # If I can't find this or the module for it is not installed, just return and skip tokenisation tasks

            # Because skipped try and create all notes here instead.
            for this_note in self.chapter_xml.find_all("note"):
                note_type = this_note.get("style")
                
                ref = this_note.find("char", style="fr") # Specific to footnote
                if ref == None:
                    ref = this_note.find("char", style="xo") # Specific to cross reference

                ref = ref.text.strip()

                note_verse_ref = self.chapter_ref.split(" ")[0] + " " + ref

                if note_type == "f":
                    self.db.execute("""
                        INSERT OR REPLACE INTO TranslationFootNotes (verse_ref, xml) 
                        VALUES (?, ?)
                    """, (note_verse_ref, str(this_note)))
                elif note_type == "x":
                    for ref in this_note.find_all("ref"):
                        to_ref = ref.get("loc")
                        split_ref = to_ref.split("-")
                        # ISA 28:11-12
                        to_verse_start = split_ref[0] # ISA 28:11
                        to_verse_end = None if len(split_ref) == 1 else to_verse_start.split(":")[0] + ":" + split_ref[1] # "ISA 28" + ":" + 12

                        self.db.execute("""
                            INSERT OR REPLACE INTO TranslationRefNotes (from_verse_ref, to_verse_start, to_verse_end, xml) 
                            VALUES (?, ?, ?, ?)
                        """, (note_verse_ref, to_verse_start, to_verse_end, str(this_note)))

            return
        
        # Extract existing infix patterns
        infixes = nlp.Defaults.infixes

        # Add new punctuation from LDML (e.g., em dash)
        custom_infixes = list(infixes)  # em dash
        for punc in self.loadLanguageLDML():
            custom_infixes.append(re.escape(punc))

        custom_infixes.append(re.escape("±")) # Added to represet notes replaced in document

        # Compile new regex
        infix_re = compile_infix_regex(custom_infixes)
        
        # Customises NLP object to include new punctuation for better tokenization
        nlp.tokenizer = Tokenizer(
            nlp.vocab,
            rules=nlp.Defaults.tokenizer_exceptions,
            prefix_search=nlp.tokenizer.prefix_search,
            suffix_search=nlp.tokenizer.suffix_search,
            infix_finditer=infix_re.finditer,
            token_match=nlp.tokenizer.token_match
        )

        # Get paragraph_id for lowest id with chapter ID number for this translation from paragraphs
        paragraph_id = self.db.execute("""
            SELECT id FROM Paragraphs WHERE chapter_id=? AND book_file_id=?
        """, (self.chapter_id, self.file_id)).fetchone()

        if paragraph_id:
            paragraph_id = paragraph_id[0]

        paragraphs = {}
        verses = {}

        all_paragraph_xml = self.chapter_xml.find_all("para")

        text_mapping = []

        # Redo text_mapping
        # use regex to extract all text, and get paragraphs, then from paragraph get verse
        # continue verse if no sid from vid in para header, if no end verse but end of para, temp end

        # This will help use get_text(), if encapsulate properly from xml, to then get_text() easily

        # Then combine per para, into massive text again for tokenisation
        # Also then calculate idx so that can be used to determine what map it falls in (for para and verse)

        # Once complete can focus on creating all the correct parsing



        # Even further, I only need to consider whether I breached a new boundary, and then update or increment
        #   Counters to reflect that, if not I should be able to continue using the same values
        #   for paragraph and verse for the next token, so no need to check what range its in

        # Can also just extract first paragraph for this book file from database (to get starting para)
        #   can also check whether its versetext, if not skip and increment another
        #   then can split text on verse, and paras on new line, so we record new changes in line and
        #   whether passed a verse split, which decide the verse has also been incremented

        verse_ref = None

        for para in all_paragraph_xml:
            para_style = para.get("style")

            # if text not verse text (text I shouldn't tokenise)
            if not self.getParagraphStyle(para_style): 
                paragraph_id += 1
                continue

            para_text_mapping = []
            notes_xml = []

            for elem in para.descendants:
                if elem.name == "verse":
                    # update current verse context
                    verse_ref = elem.get("sid")

                # Handle notes: store, then skip adding to snippet
                if isinstance(elem, Tag) and elem.name == "note":
                    # Persist note
                    notes_xml.append(elem)
                    para_text_mapping.append(("±", paragraph_id, verse_ref))

                if elem.name == "note" or elem.find_parent("note"):
                    # Add some functionality for treating notes as a token?
                    continue

                elif isinstance(elem, NavigableString):
                    text = str(elem)

                    if text in ["\n","\t"]:
                        continue  # skip empty whitespace if you want

                    # para_text_mapping.append((text, para_id, verse_ref))
                    if para_text_mapping and para_text_mapping[-1][1] == paragraph_id and para_text_mapping[-1][2] == verse_ref:
                        # merge with previous
                        prev_text, _, _ = para_text_mapping[-1]
                        para_text_mapping[-1] = (prev_text + text, paragraph_id, verse_ref)
                    else:
                        para_text_mapping.append((text, paragraph_id, verse_ref))

            # merge with global text_mapping
            # if latest in text_mapping has same para and verse as first in local para text mapping
            if text_mapping and para_text_mapping and text_mapping[-1][1:] == para_text_mapping[0][1:]:
                # Merge it into final entry, and then add the rest of para_text_mapping
                prev_text, para_id, verse_id = text_mapping[-1]
                text_mapping[-1] = (prev_text + para_text_mapping[0][0], para_id, verse_id)
                text_mapping.extend(para_text_mapping[1:])
            else:
                text_mapping.extend(para_text_mapping)

            # Increment paragraph_id to align
            paragraph_id += 1

        chapter_text = ""
        spans = []  # [(start, end, para_id, verse_ref)]

        last_para_id = None

        for text, para_id, verse_ref in text_mapping:
            start = len(chapter_text)
            chapter_text += text
            if last_para_id != para_id and start > 0:
                # print(len(chapter_text), para_id, verse_ref)
                chapter_text += "\n" # Adds an extra character
                last_para_id = para_id
                # print(len(chapter_text))
            end = len(chapter_text)
            spans.append((start, end, para_id, verse_ref))

        # Now chapter_text is the whole block
        # spans tells you exactly where verses/paras are

        # if text_mapping:
        #     log_path = f"/Users/cepherom/git/bibleSearchTool/logs/{self.chapter_ref.split(' ')[0]}/"
        #     log_file = f"{log_path}{self.chapter_ref}.xml"

        #     pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)

        #     with open(log_file, 'a') as f:
        #         f.write("\n")
        #         # f.write(str(text_mapping))
        #         for map in text_mapping:
        #             f.write(chapter_text)
        #             f.write("\n")

            # print(f"{log_file} Created!")

        # Get all text for chapter.

        # Set up mapping correctly

        # Feed into nlp as a document
        doc = nlp(chapter_text)

        # note_count = 0
        newline_counts = 0

        # Create Tokens from all the subsidary data from all tokens in the document
        for token in doc:
            # Skip new line character artificially inserted into text
            if token.text == "\n":
                newline_counts+=1
                continue

            token_pos = token.idx # character offset
            token_paragraph_id = None
            token_verse_ref = None

            for start, end, para_id, verse_ref in spans:
                if start <= token_pos < end:
                    token_paragraph_id = para_id
                    token_verse_ref = verse_ref

            # Logic to add Note to Database following token they were mentioned after
            if token.text == "±" and notes_xml:
            # Uses substring position to determine if we are going over where a note was positioned, and if so create it
                # this_note = notes_xml[note_count]
                this_note = notes_xml[0]
                note_type = this_note.get("style")

                note_verse_ref = verse_ref # verse_ref.split(" ")[0] + " " + this_note.stripped_strings[0]

                prev_token_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Tokens",)).fetchone()[0]

                if note_type == "f":
                    self.db.execute("""
                        INSERT OR REPLACE INTO TranslationFootNotes (previous_token, verse_ref, xml) 
                        VALUES (?, ?, ?)
                    """, (prev_token_id, note_verse_ref, str(this_note)))
                elif note_type == "x":
                    for ref in this_note.find_all("ref"):
                        to_ref = ref.get("loc")
                        split_ref = to_ref.split("-")
                        # ISA 28:11-12
                        to_verse_start = split_ref[0] # ISA 28:11
                        to_verse_end = None if len(split_ref) == 1 else to_verse_start.split(":")[0] + ":" + split_ref[1] # "ISA 28" + ":" + 12

                        self.db.execute("""
                            INSERT OR REPLACE INTO TranslationRefNotes (previous_token, from_verse_ref, to_verse_start, to_verse_end, xml) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (prev_token_id, note_verse_ref, to_verse_start, to_verse_end, str(this_note)))
                
                notes_xml.pop(0)
                # note_count+=1
                # Skip token after adding note to database, since not part of text?
                continue

            llema_id = None

            # Need to check what type of token this is, should only create llema on words. - eventually
            if not token.is_punct:
            # Check llema existence in table
                llema_id = self.db.execute("""
                    SELECT id FROM Llemas WHERE text=? AND language_id=?
                """, (token.lemma_, self.language_id)).fetchone()

                if llema_id == None:
                    self.db.execute("""
                        INSERT INTO Llemas (text, language_id) 
                        VALUES (?, ?)
                    """, (token.lemma_, self.language_id))
                    # self.db.commit()
                    llema_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Llemas",)).fetchone()[0]
                else:
                    llema_id = llema_id[0]

            self.db.execute("""
                INSERT INTO Tokens (
                    text, llema_id, paragraph_id, verse_ref,
                    pos, tag, dep, head_token_id, 
                    trailing_space, is_alpha, is_punct, like_num) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                token.text, llema_id, token_paragraph_id, token_verse_ref, 
                token.pos_, token.tag_, token.dep_, token.head.i,
                len(token.whitespace_) > 0, token.is_alpha, token.is_punct, token.like_num
            ))

            token_id = self.db.execute("""SELECT seq FROM sqlite_sequence WHERE name=? """, ("Tokens",)).fetchone()[0]

            # If this is an opening quote then create quote instance
            if token.text == "‘" or token.text == "“":

                self.db.execute("""
                    INSERT INTO Quotes (text, start_token) 
                    VALUES (?, ?)
                """, (token.text, token_id))