from bs4 import BeautifulSoup, Tag, NavigableString
import re

from pathlib import Path
import os
import json

class Verse:
    def __init__(self, chapter_xml, verse_ref, chapter_occurence_id, db_conn, is_special_case=False):
        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.chapter_xml = chapter_xml
        self.chapter_occurence_id = chapter_occurence_id
        self.verse_ref = verse_ref
        self.is_special_case = is_special_case

        self.createVerse()

        self.conn.commit()

        if self.is_special_case == False:
            self.xml = self.getVerseAndNoteXML()
            self.text = self.getVerseText(self.xml)
            self.createVerseOccurence()

        self.conn.commit()
    
    def createVerse(self):
        # Check whether non-standard verse has been added or not
        self.cur.execute("""
            SELECT id FROM bible.verses WHERE verse_ref = %s;
        """, (self.verse_ref,))
        verse_found = self.cur.fetchone()

        if verse_found == None:
            verse_splits = self.verse_ref.split("-")
            chapter_ref, verse_num = verse_splits[0].split(":")

            # Check whether verse_ref is non standard e.g. GEN 1:1-2
            if len(verse_splits) > 1:
                # Create new non standard verse first (to preseve foreign key constraint in db as well before verse occurence created)
                self.cur.execute("""
                    INSERT INTO bible.verses (chapter_ref, verse_ref, standard, verse) 
                    VALUES (%s, %s, %s)
                """, (chapter_ref, self.verse_ref, False, verse_num))

                start_verse = int(verse_num)
                end_verse = int(verse_splits[1]) + 1 # because range is non inclusive
                for verse in range(start_verse, end_verse):
                    new_verse_ref = f"{chapter_ref}:{verse}"
                    self.cur.execute("""
                        INSERT INTO bible.verse_correction (non_standard_verse_ref, verse_ref) 
                        VALUES (%s, %s)
                    """, (self.verse_ref, new_verse_ref))
            
            # Taking account of secondary non standard verse
            print(self.verse_ref, self.verse_ref[-1], self.verse_ref[-1].isalpha())
            if self.verse_ref[-1].isalpha(): # e.g. EXO 28:29a
                self.cur.execute("""
                    INSERT INTO bible.verses (chapter_ref, verse_ref, standard, verse) 
                    VALUES (%s, %s, %s)
                """, (chapter_ref, self.verse_ref, False, verse_num))
                
                new_verse_ref = self.verse_ref[:-1]
                self.cur.execute("""
                    INSERT INTO bible.verse_correction (non_standard_verse_ref, verse_ref) 
                    VALUES (%s, %s)
                """, (self.verse_ref, new_verse_ref))

    def createVerseOccurence(self):
        self.cur.execute("""
            INSERT INTO bible.verseoccurences (chapter_occ_id, verse_ref, text, xml) 
            VALUES (%s, %s, %s, %s)
        """, (self.chapter_occurence_id, self.verse_ref, self.text, str(self.xml)))

    def getVerseAndNoteXML(self):
        # Regex to get everything between opening and closing paragraph tag
        start_tag = self.chapter_xml.find("verse", sid=self.verse_ref)
        end_tag = self.chapter_xml.find("verse", eid=self.verse_ref)
        para_tag = "<usx>" + str(start_tag.find_parent("para")).split(">")[0] + ">"

        search_string = f"{start_tag}.*{end_tag}"
        verse_xml = para_tag + "\n"
        verse_found = re.search(search_string, str(self.chapter_xml), re.DOTALL)
        
        verse_xml += verse_found.group(0) if verse_found != None else ""
        verse_xml += "\n</para></usx>"
        
        return verse_xml

    def getVerseText(self, verse_xml):
        temp_verse_xml = BeautifulSoup(str(verse_xml), "xml")

        verse_sub_paras = temp_verse_xml.find_all("para")

        # Check for para tags
        for para in verse_sub_paras:
            # print(para)
            para_style = para.get("style")

            if para_style != None:
                # Get latest translation (the one we are currently working on)
                translation_id = None
                try:
                    self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.translations",))
                    translation_id = self.cur.fetchone()[0]
                except Exception as e:
                    self.conn.rollback()
                    translation_id = 1

                self.cur.execute("""
                    SELECT versetext FROM bible.styles WHERE style = %s AND source_file_id = (SELECT style_file FROM bible.translations WHERE id = %s);
                """, (para_style,translation_id))
                result = self.cur.fetchone()[0]

                is_versetext = True if result else False

                if is_versetext == False:
                    para.decompose()

                # Remove <note> tags completely
                all_notes = para.find_all("note")
                if len(all_notes) > 0:
                    for note in para.find_all("note"):
                        note.decompose()

        final_text = temp_verse_xml.get_text().strip()
        return final_text
