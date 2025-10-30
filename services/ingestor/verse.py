from bs4 import BeautifulSoup, Tag, NavigableString
import re

from pathlib import Path
import os
import json

class Verse:
    def __init__(self, chapter_xml, verse_ref, chapter_occurence_id, db_conn, translation_title):
        # Adds a database connection
        self.conn = db_conn
        self.cur = self.conn.cursor()

        self.chapter_xml = chapter_xml
        self.chapter_occurence_id = chapter_occurence_id
        self.verse_ref = verse_ref

        self.translation_title = translation_title

        self.xml = None
        self.text = None

        self.createVerse()

        self.conn.commit()
    
    def createVerse(self):
        self.getVerseAndNoteXML()
        self.getVerseText()

        verse_splits = self.verse_ref.split("-")
        chapter_ref, verse_num = verse_splits[0].split(":")

        # Check whether verse_ref is non standard e.g. GEN 1:1-2
        if len(verse_splits) > 1:
            # Create new non standard verse first (to preseve foreign key constraint in db as well before verse occurence created)
            self.cur.execute("""
                INSERT INTO bible.verses (chapter_ref, verse_ref, standard) 
                VALUES (%s, %s, %s)
            """, (chapter_ref, self.verse_ref, False))

            start_verse = int(verse_num)
            end_verse = int(verse_splits[1]) + 1 # because range is non inclusive
            for verse in range(start_verse, end_verse):
                new_verse_ref = f"{chapter_ref}:{verse}"
                self.cur.execute("""
                    INSERT INTO bible.verses (non_standard_verse_ref, verse_ref) 
                    VALUES (%s, %s)
                """, (self.verse_ref, new_verse_ref))

        self.cur.execute("""
            INSERT INTO bible.verseoccurences (chapter_occ_id, verse_ref, text, xml) 
            VALUES (%s, %s, %s, %s)
        """, (self.chapter_occurence_id, self.verse_ref, self.text, str(self.xml)))

        self.createLabelStudioTask()

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
        
        self.xml = verse_xml

    def getVerseText(self):
        temp_verse_xml = BeautifulSoup(str(self.xml), "xml")

        verse_sub_paras = temp_verse_xml.find_all("para")

        # Check for para tags
        for para in verse_sub_paras:
            # print(para)
            para_style = para.get("style")

            if para_style != None:
                self.cur.execute("""
                    SELECT versetext FROM bible.styles WHERE style=%s
                """, (para_style,))
                result = self.cur.fetchone()

                is_versetext = result[0] if result else None

                if str(is_versetext) != True:
                    para.decompose()

                # Remove <note> tags completely
                all_notes = para.find_all("note")
                if len(all_notes) > 0:
                    for note in para.find_all("note"):
                        note.decompose()

        self.text = temp_verse_xml.get_text().strip()
        # CHANGE LOGIC TO EXTRACT JUST CONTINUOS TEXT, NO LINE BREAKS

    def createQuotesOccurences(self):
        # Consider here creating objects for
        # Quotes
        # 
        pass

    def createLabelStudioTask(self):
        # After receiving text start feeding into label studio project to create tasks for annotating this verse translation accordingly
        # Perhaps be selective only for instances where quotes have been found
        # Or doing a quick nlp if a pronoun or a noun has been found in this verse, then try and highlight for later, 
        # then using results see if we can make it smarter to recognise these before, perhaps loaded into 

        # This should write the details to a json file inside Minio or stored locally then sent over to minio to store for us
        # as we go through verses we append the information in there so that we can just import all labelling tasks for this translation
        # straight into label studio to create, instead of create labelling tasks one by one (which is uneccessary)

        # We can however programatically set up how we want to project and interfaces etc to be created through the api and then call the data import
        # or automate our very own machine learning backend to highlight specific things for us :)
        
        # create a json file in downloads folder like text-DBL-AGREEMENT-import

        # Then append verse to it with annotation aspects as part of the json in the file, then at the end for translation upload it to project.
        # Should create the file on minio-usx-upload (then should upload the file to minio on finish uploading, while also reading it to import into label studio)
        nlp_import_file = Path(__file__).parents[2] / "downloads" / f"{self.translation_title}.json"

        nlp_data = {
            "data": {
                "text": self.text,
                "verse_ref": self.verse_ref
            }
        }

        with open(nlp_import_file, 'a', encoding="utf-8") as f:
            f.write("\n")
            json.dump(nlp_data, f)
            f.write(",")
            
