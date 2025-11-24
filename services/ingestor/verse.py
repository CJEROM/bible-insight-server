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
            self.createVerseOccurence()

        self.conn.commit()

    def get_verse_ref(self):
        return self.verse_ref
    
    def get_start_node(self):
        return self.start_node
    
    def get_end_node(self):
        return self.end_node
    
    def get_verse_occurence_id(self):
        return self.verse_occurence_id
    
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
                    INSERT INTO bible.verses (chapter_ref, verse_ref, standard) 
                    VALUES (%s, %s, %s)
                """, (chapter_ref, self.verse_ref, False))

                start_verse = int(verse_num)
                end_verse = int(verse_splits[1]) + 1 # because range is non inclusive
                for verse in range(start_verse, end_verse):
                    new_verse_ref = f"{chapter_ref}:{verse}"
                    self.cur.execute("""
                        INSERT INTO bible.verse_correction (non_standard_verse_ref, verse_ref) 
                        VALUES (%s, %s)
                    """, (self.verse_ref, new_verse_ref))
            
            # Taking account of secondary non standard verse
            if self.verse_ref[-1].isalpha(): # e.g. EXO 28:29a
                self.cur.execute("""
                    INSERT INTO bible.verses (chapter_ref, verse_ref, standard, verse) 
                    VALUES (%s, %s, %s, %s)
                """, (chapter_ref, self.verse_ref, False, verse_num))
                
                new_verse_ref = self.verse_ref[:-1]
                self.cur.execute("""
                    INSERT INTO bible.verse_correction (non_standard_verse_ref, verse_ref) 
                    VALUES (%s, %s)
                """, (self.verse_ref, new_verse_ref))

    def createVerseOccurence(self):
        self.cur.execute("""
            SELECT start_node, end_node FROM bible.chapteroccurences WHERE id = %s;
        """, (self.chapter_occurence_id,))
        chapter_start_node, chapter_end_node = self.cur.fetchone()

        self.cur.execute("""
            SELECT id FROM bible.nodes 
            WHERE (sid = %s OR eid = %s) 
                AND node_type = 'verse' 
                AND id BETWEEN %s AND %s
            ORDER BY id;
        """, (self.verse_ref, self.verse_ref, chapter_start_node, chapter_end_node))
        start_node, end_note = self.cur.fetchall()

        self.cur.execute("""
            INSERT INTO bible.verseoccurences (chapter_id, verse_ref, start_node, end_node) 
            VALUES (%s, %s, %s, %s)
        """, (self.chapter_occurence_id, self.verse_ref, start_node, end_note))