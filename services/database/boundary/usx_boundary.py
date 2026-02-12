
from database.boundary.base_boundary import ReadBoundary, WriteBoundary, DeleteBoundary

import json

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AgreementRecord:
    agreement_id: int
    dbl_id: str
    licence_file_id: int
    base_licence_id: int
    dateLicence: datetime
    dateLicenceExpiry: datetime
    notes: Optional[str]

class USXReadBoundary(ReadBoundary):
    # GET       = Number of items
    # FIND      = Specific item
    # CHECK     = Only get certain subset of data

    # ============================================================================
    #                                   CHAPTERS
    # ============================================================================

    def get_all_chapters(self, 
            book_code: str
        ) -> list[str]:
        if len(book_code) != 3:
            raise ValueError("Book code must be 3 characters long.")
        
        query = """
            SELECT chapter_ref FROM bible.chapters WHERE book_code=%s
        """
        result = self.db.fetch_all(query, (book_code,))
        return result
    
    def find_chapter(self, 
            chapter_ref: str
        ) -> str:
        query = """
            SELECT id FROM bible.chapters WHERE chapter_ref = %s
        """
        result = self.db.fetch_clean_one(query, (chapter_ref,))
        return result
    
    # ============================================================================
    #                                   BOOK
    # ============================================================================
    
    def find_book(self, 
            book_code: str
        ) -> int:
        query = """
            SELECT id FROM bible.books WHERE code = %s;
        """
        result = self.db.fetch_clean_one(query, (book_code,))
        return result
    
    # ============================================================================
    #                                   VERSE
    # ============================================================================
    
    def find_verse(self,
            verse_ref: str
        ) -> int:
        query = """
            SELECT id FROM bible.verses WHERE verse_ref = %s;
        """
        result = self.db.fetch_clean_one(query, (verse_ref,))
        return result
    
    # ============================================================================
    #                                   TRANSLATION
    # ============================================================================

    def find_translation(self,
            dbl_id: int,
            revision: int
        ) -> str:
        query = """
            SELECT id FROM bible.translations WHERE dbl_id = %s AND revision = %s;
        """
        result = self.db.fetch_clean_one(query, (dbl_id, revision))
        return result
    
    # Still need to figure out how this will work, with new split between dbl-agreements and translations
    def is_translation_supported(self, 
            dbl_id: str, 
            revision: int | None = None
        ) -> bool:
        query = """
            SELECT supported
            FROM audit.dbl_info
            WHERE dbl_id = %s
                AND revision IN (%s, 0)
            ORDER BY revision DESC
            LIMIT 1;
        """
        row = self.db.fetch_one(query, (dbl_id, revision))
        return row
    
    # ============================================================================
    #                                   NODES
    # ============================================================================

    def get_node_count(self) -> int:
        query = """
            SELECT COALESCE(MAX(id), 0) FROM bible.nodes;
        """
        node_count = self.db.fetch_clean_one(query)
        return node_count
    
    # ============================================================================
    #                                   PARAGRAPH
    # ============================================================================

    def is_paragraph_versetext(self,
            style: str,
            style_file_id: int
        ) -> bool:
        query = """
            SELECT versetext FROM bible.styles WHERE style = %s AND source_file_id = %s
        """
        result = self.db.fetch_clean_one(query, (style, style_file_id))
        
        if result == "true": 
            return True
        
        # if result == "false" or result is None:
        return False
    
    # ============================================================================
    #                                   AGREEMENT
    # ============================================================================

    def find_agreement(self,
            agreement_id: int
        ) -> AgreementRecord | None:
        query = """
            SELECT dbl_id, agreement_id, licence_file_id, base_licence_id, dateLicence, dateLicenceExpiry, notes
            FROM audit.dbl_agreements WHERE agreement_id=%s;
        """
        result = self.db.fetch_one(query, (agreement_id,))
        if not result:
            return None

        return AgreementRecord(*result)

    def find_agreement_expired(self,
            agreement_id: int
        ) -> bool:
        query = """
            SELECT *
            FROM audit.dbl_agreements
            WHERE dateLicenceExpiry < NOW()
            AND agreement_id=%s;
        """
        result = self.db.fetch_one(query, (agreement_id,))
        return True if result else False

class USXWriteBoundary(WriteBoundary):
    # ============================================================================
    #                                   CHAPTER
    # ============================================================================

    def persist_chapter_occurence(self, 
            chapter_ref:str, book_map_id: int, translation_id: int, start_node: int=None, end_node: int=None
        ) -> int:
        query = """
            INSERT INTO bible.chapteroccurences (chapter_ref, book_map_id, translation_id, start_node, end_node) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        chapter_occurence_id = self.db.fetch_clean_one(query, (chapter_ref, book_map_id, translation_id, start_node, end_node))
        return chapter_occurence_id
    
    def persist_chapter(self, 
            book_code: str, 
            chapter_num: int, 
            chapter_ref: str, 
            is_standard: bool
        ) -> None:
        query = """
            INSERT INTO bible.chapters (book_code, chapter_num, chapter_ref, standard) 
            VALUES (%s, %s, %s, %s);
        """ # ON CONFLICT (chapter_ref) DO NOTHING;
        self.db.execute(query, (book_code, chapter_num, chapter_ref, is_standard))

    # ============================================================================
    #                                   TRANSLATION
    # ============================================================================

    def persist_translation_info(self,
            dbl_id: str,
            revision: int,
            is_supported: bool,
            is_test_import: bool,
            reason_not_supported: str = None
        ) -> None:
        # If we add this and we already have stored supported for translation revision, skip
        query = """
            INSERT INTO audit.dbl_info (dbl_id, revision, supported, test_import, reason_not_supported)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (dbl_id, revision) DO NOTHING;
        """
        self.db.execute(query, (dbl_id, revision, is_supported, is_test_import, reason_not_supported))

    def persist_usx_translation(self,
            dbl_id: str,
            revision: int,
            revision_note: str,
            revision_date: str,
            language_id: int,
            medium: str,
            name: str,
            name_local: str,
            abbreviation: str,
            abbreviationLocal: str,
            copyright: str,
            promotion: str,
        ) -> int:
        query = """
            INSERT INTO bible.translations (dbl_id, revision, revision_note, revision_date, language_id, medium, name, nameLocal, abbreviation, abbreviationLocal, copyright, promotion) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        translation_id = self.db.fetch_clean_one(query, (dbl_id, revision, revision_note, revision_date, language_id, medium, name, name_local, abbreviation, abbreviationLocal, copyright, promotion))
        return translation_id
    
    def persist_translation_relation(self,
            from_dbl_id: int,
            from_revision: int,
            to_dbl_id: str,
            to_revision: str,
            relation_type: str
        ) -> None:
        query = """
            INSERT INTO bible.translationrelationships (from_translation, from_revision, to_translation, to_revision, type) 
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute(query, (from_dbl_id, from_revision, to_dbl_id, to_revision, relation_type))

    # ============================================================================
    #                                   NODES
    # ============================================================================

    def persist_nodes(self, 
            new_nodes: list[tuple]
        ) -> None:
        query = """
            INSERT INTO bible.nodes (node_text, node_type, code, sid, eid, vid, style, number, caller, closed, version, strong, loc, parent_node_id, index_in_parent, book_map_id, canonical_path, align, translation_id, is_tokenisable) 
            VALUES %s;
        """
        self.db.bulk_insert(query, new_nodes)

    # ============================================================================
    #                                   PARAGRAPH
    # ============================================================================

    def persist_paragraph(self, 
            paragraph_node_id: int, 
            style_id: int, 
            is_versetext: bool,
            parent_para_id: int = None
        ) -> int:
        query = """
            INSERT INTO bible.paragraphs (node_id, style_id, parent_para, is_versetext) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        paragraph_id = self.db.fetch_clean_one(query, (paragraph_node_id, style_id, parent_para_id, is_versetext))
        return paragraph_id
    
    # ============================================================================
    #                                   AGREEMENT
    # ============================================================================

    def persit_dbl_agreement(self,
            dbl_id: str,
            agreement_id: int,
            license_id: int,
            dateLicensed: str,
            dateLicenceExpires: str,
            file_id: int,
            active: bool
        ) -> int:
        query = """
            INSERT INTO audit.dbl_agreements (dbl_id, agreement_id, license_id, date_licensed, date_licence_expires, file_id, active) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        dbl_agreement_id = self.db.fetch_clean_one(query, (dbl_id, agreement_id, license_id, dateLicensed, dateLicenceExpires, file_id, active))
        return dbl_agreement_id
    
    def init_agreement(self,
            agreement_id: int
        ) -> None:
        query = """
            INSERT INTO audit.dbl_agreements (agreement_id)
            VALUES (%s);
        """
        self.db.execute(query, (agreement_id, ))

    def update_agreement(self, 
            agreement_id: int,
            dbl_id: str,
            base_licence_id: int,
            dateLicence: str,
            dateLicenceExpiry: str,
            licence_file_id: int
        ) -> None:
        query = """
            UPDATE audit.dbl_agreements 
            SET dbl_id  = %s, 
                base_licence_id = %s, 
                dateLicence = %s, 
                dateLicenceExpiry = %s, 
                licence_file_id = %s
            WHERE agreement_id = %s;
        """
        self.db.execute(query, (dbl_id, base_licence_id, dateLicence, dateLicenceExpiry, licence_file_id, agreement_id))
    
    def persist_agreement_revision_mapping(self,
            agreement_id: int,
            revision: int
        ) -> None:
        query = """
            INSERT INTO audit.dbl_revision_agreements (agreement_id, revision)
            VALUES (%s, %s);
        """
        self.db.execute(query, (agreement_id, revision))

    def persist_agreement_attributes(self,
            agreement_id: int,
            attribute_code: str,
            attribute_value: str           
        ) -> None:
        query = """
            INSERT INTO audit.agreement_attributes (agreement_id, attribute_code, attribute_value)
            VALUES (%s, %s, %s);
        """
        self.db.execute(query, (agreement_id, attribute_code, attribute_value))

    # ============================================================================
    #                                   FILES
    # ============================================================================

    def persist_translation_file(self,
            file_id: int,
            translation_id: int,
            type: str,
            version: str
        ) -> None:
        query = """
            INSERT INTO bible.translation_files (file_id, translation_id, type, version) 
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute(query, (file_id, translation_id, type, version))

    
    def persist_book_file(self,
            book_code: str,
            translation_id: int,
            file_id: int,
            short: str,
            long: str
        ) -> int:
        query = """
            INSERT INTO bible.booktofile (book_code, translation_id, file_id, short, long) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        book_map_id = self.db.fetch_clean_one(query, (book_code, translation_id, file_id, short, long))
        return book_map_id
    
    # ============================================================================
    #                                   STYLES
    # ============================================================================
    
    def persist_style_property(self,
            name: str,
            value: str,
            unit: str = None,
            style_id: int = None
        ) -> None:
        query = """
            INSERT INTO bible.properties (name, value, unit, style_id) 
            VALUES (%s, %s, %s, %s);
        """
        self.db.execute(query, (name, value, unit, style_id))
    
    def persist_style(self,
            style: str,
            name: str,
            description: str,
            is_versetext: bool,
            is_publishable: bool,
            source_file_id: int
        ) -> int:
        query = """
            INSERT INTO bible.styles (style, name, description, versetext, publishable, source_file_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        style_id = self.db.fetch_clean_one(query, (style, name, description, is_versetext, is_publishable, source_file_id))
        return style_id
    
    # ============================================================================
    #                                   VERSE
    # ============================================================================

    def persist_excluded_verse(self,
            verse_ref: str,
            translation_id: int
        ) -> None:
        query = """
            INSERT INTO bible.excludedverses (verse_ref, translation_id) 
            VALUES (%s, %s);
        """
        self.db.execute(query, (verse_ref, translation_id))

    def persist_verse(self,
            chapter_ref: str,
            verse_ref: str,
            verse: str,
            is_standard: bool
        ) -> int:
        query = """
            INSERT INTO bible.verses (chapter_ref, verse_ref, verse, standard) 
            VALUES (%s, %s, %s, %s)
        """
        verse_id = self.db.execute(query, (chapter_ref, verse_ref, verse, is_standard))
        return verse_id
    
    def persist_verse_correction(self,
            non_standard_verse_ref: str,
            verse_ref: str
        ) -> None:
        query = """
            INSERT INTO bible.verse_correction (non_standard_verse_ref, verse_ref) 
            VALUES (%s, %s)
        """
        self.db.execute(query, (non_standard_verse_ref, verse_ref))
    
    def persist_verse_occurence(self,
            chapter_id: int,
            book_map_id: int,
            translation_id: int,
            verse_ref: str,
            start_node: int,
            end_node: int
        ) -> int:
        query = """
            INSERT INTO bible.verseoccurences (chapter_id, book_map_id, translation_id, verse_ref, start_node, end_node) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        verse_occurence_id = self.db.fetch_clean_one(query, (chapter_id, book_map_id, translation_id, verse_ref, start_node, end_node))
        return verse_occurence_id
    
    # ============================================================================
    #                          CROSS REFERENCES + FOOTNOTES
    # ============================================================================
    
    def persist_footnote(self,
            node_id: int,
            chapter_ref: str,
            verse_ref: str
        ) -> int:
        query = """
            INSERT INTO bible.translationfootnotes (node_id, chapter_ref, verse_ref) 
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        footnote_id = self.db.fetch_clean_one(query, (node_id, chapter_ref, verse_ref))
        return footnote_id
    
    def persist_cross_reference(self,
            node_id: int,
            from_verse_ref: str,
            to_verse_ref: str,
            from_chapter_ref: str,
            to_chapter_ref: str
        ) -> int:
        query = """
            INSERT INTO bible.translationrefnotes (node_id, from_verse_ref, to_verse_ref, from_chapter_ref, to_chapter_ref) 
            VALUES %s
            RETURNING id;
        """
        cross_reference_id = self.db.fetch_clean_one(query, (node_id, from_verse_ref, to_verse_ref, from_chapter_ref, to_chapter_ref))
        return cross_reference_id
    
class USXDeleteBoundary(DeleteBoundary):
    # ============================================================================
    #                                   TRANSLATION
    # ============================================================================

    def delete_translation(self,
            translation_id: int
        ) -> None:
        # Ideas is to cancel USX translation and all its derivative data
        query = """
            DELETE FROM bible.translations WHERE id = %s;
        """
        self.db.execute(query, (translation_id,))