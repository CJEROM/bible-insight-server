from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.dbmanager import DBManager

import json

class QueryBoundary:
    def __init__(self, db_manager: "DBManager"):
        self.db = db_manager

class ReadBoundary(QueryBoundary):
    # ============================================================================
    #                                   FILES
    # ============================================================================

    def read_file(self, 
            file_id: int
        ): 
        query = """
            SELECT file_path AS object_name, bucket, version_id FROM audit.files WHERE id = %s
        """
        results = self.db.fetch_one(query, (file_id, ))
        return results
    
    def get_latest_file(self,
            bucket      : str,
            object_path : str
        ) -> int:
        query = """
            SELECT id
            FROM audit.files
            WHERE bucket = %s
                AND object_path = %s
            ORDER BY import_time DESC
            LIMIT 1;
        """
        file_id = self.db.fetch_clean_one(query, (bucket, object_path))
        return file_id
    
    def get_file_by_hash(self,
            content_hash    : str,
            data_format     : str
        ) -> int:
        # Hashes
        #       - Same content → same hash
        #       - Different content → different hash (for all practical purposes)
        #       - Did this file change? = Have these exact bytes ever existed in my system before?
  
        # Try exact content match
        query_hash = """
            SELECT id
            FROM audit.files
            WHERE content_hash = %s
                AND data_format = %s
            LIMIT 1;
        """
        file_id = self.db.fetch_clean_one(
            query_hash,
            (content_hash, data_format)
        )
        return file_id
    
    # ============================================================================
    #                                   LABEL STUDIO
    # ============================================================================
    
    def get_all_label_projects(self) -> list[tuple[int, int, str, str]]:
        query = """
            SELECT tlp.project_id, tlp.translation_id, lp.name, lp.description
            FROM nlp.translation_labelling_projects tlp
            JOIN nlp.labelling_projects lp ON tlp.project_id = lp.id;
        """
        result = self.db.fetch_all(query)
        return result
    
    # ============================================================================
    #                                   SOURCE
    # ============================================================================

    def find_source(self, 
            code    : str
        ) -> int:
        query = """
            SELECT id FROM audit.sources WHERE code=%s
        """
        source_id = self.db.fetch_clean_one(query, (code,))
        return source_id
    
    # ============================================================================
    #                                   LANGUAGE
    # ============================================================================

    def find_language(self, 
            iso_code    : str
        ) -> int:
        query = """
            SELECT id FROM language.languages WHERE iso = %s;
        """
        result = self.db.fetch_clean_one(query, (iso_code,))
        return result
    
    # ============================================================================
    #                                   LICENCE
    # ============================================================================

    def find_license(self,
            license_code    : str
        ) -> int:
        query = """
            SELECT id FROM audit.licences WHERE code=%s
        """
        licence_id = self.db.fetch_clean_one(query, (license_code, ))
        return licence_id

class WriteBoundary(QueryBoundary):
    # ============================================================================
    #                                   LABEL STUDIO
    # ============================================================================
    def persist_label_studio_project(self,
            label_project_id    : int,
            project_name        : str,
            project_description : str
        ) -> None:
        query = """
            INSERT INTO nlp.labelling_projects (id, name, description) 
            VALUES (%s, %s, %s);
        """
        self.db.fetch_clean_one(query, (
            label_project_id,
            project_name,
            project_description
        ))

    def map_label_studio_project(self,
            translation_id      : int,
            label_project_id    : int
        ) -> int:
        query = """
            INSERT INTO nlp.translation_labelling_projects (translation_id, project_id) 
            VALUES (%s, %s)
            RETURNING id;
        """
        mapping_id = self.db.execute(query, (
            translation_id,
            label_project_id
        ))
        return mapping_id
    
    # ============================================================================
    #                                   FILES
    # ============================================================================

    def persist_file(self,
            etag            : str,
            type            : str,
            object_path     : str,
            bucket          : str,
            source_id       : int,
            version_id      : str, 
            data_format     : str,
            content_hash    : str,
            version_note    : str = None,
        ) -> int:
        query = """
            INSERT INTO audit.files (etag, type, object_path, bucket, source_id, version_id, version_note, data_format, content_hash) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        file_id = self.db.fetch_clean_one(query, (etag, type, object_path, bucket, source_id, version_id, version_note, data_format, content_hash))
        return file_id
    
    # ============================================================================
    #                                   SOURCES
    # ============================================================================

    def init_source(self,
            source_type     : str,
            url             : str
        ):
        query = """
            INSERT INTO audit.sources(source_type, url)
            VALUES (%s, %s)
            RETURNING id;
        """
        source_id = self.db.execute(query, (source_type, url))
        return source_id
    
    def update_source(self,
            code                : str,
            name                : str,
            description         : str,
            version             : str, 
            note                : str,
            parent_source       : str,
            official_citation   : str = None,
            date_published      : str = None,
            metadata            : json = None
        ):
        query = """
            UPDATE audit.sources
            SET code = %s,
                name = %s,
                description = %s,
                version = %s,
                note = %s,
                official_citation = %s,
                date_published = %s,
                metadata = %s,
            WHERE id = %s
        """
        self.db.fetch_clean_one(query, (code, name, description, version, note, parent_source, official_citation, date_published, metadata))

    def persist_source(self,
            source_type         : str,
            code                : str,
            name                : str,
            description         : str,
            version             : str,
            url                 : str,    
            note                : str,
            parent_source       : str,
            official_citation   : str = None,
            date_published      : str = None,
            metadata            : json = None
        ) -> int:
        query = """
            INSERT INTO audit.sources (source_type, code, name, description, version, url, note, parent_source, official_citation, date_published, metadata) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        source_id = self.db.fetch_clean_one(query, (source_type, code, name, description, version, url, note, parent_source, official_citation, date_published, metadata))
        return source_id
    
    # ============================================================================
    #                                   INGESTION
    # ============================================================================

    def start_ingestion(self,
            source_id   : int,
            start_time  : str
        ) -> int: 
        query = """
            INSERT INTO audit.ingestion_stats (source_id, start_time)
            VALUES (%s, %s)
            RETURNING id;
        """
        ingestion_id = self.db.fetch_clean_one(query, (source_id, start_time))
        return ingestion_id

    def end_ingestion(self,
            ingestion_id    : int,
            end_time        : str,
            error_message   : str = None
        ) -> None:
        query = """
            UPDATE audit.ingestion_stats
            SET end_time = %s,
                error_message = %s
            WHERE id = %s
        """
        self.db.execute(query, (end_time, error_message, ingestion_id))

    # ============================================================================
    #                                   LICENCES
    # ============================================================================
    
    def persist_licence(self, 
            source_id       : int,
            code            : str,
            name            : str,
            version         : str,
            link            : str,
            valid_from      : str = None,
            valid_until     : str = None,
            notes           : str = None
        ) -> int:
        query = """
            INSERT INTO audit.licences (source_id, code, name, version, valid_from, valid_until, notes) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        licence_id = self.db.fetch_clean_one(query, (source_id, code, name, version, link, valid_from, valid_until, notes))
        return licence_id

    def persist_licence_attribute(self,
            attribute_code  : str,
            name            : str,
            description     : str,
            attribute_type  : int         
        ) -> str:
        query = """
            INSERT INTO audit.licence_attributes (attribute_code, name, description, attribute_type)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        self.db.execute(query , (attribute_code, name, description, attribute_type))
        
        return

    def persist_licence_attribute_mapping(self,
            licence_id      : int,
            attribute_code  : str,
            custom_note     : str = None                  
        ) -> None:
        query = """
            INSERT INTO audit.licence_attribute_mapping (licence_id, attribute_code, custom_note)
            VALUES (%s, %s, %s)
        """
        self.db.execute(query, (licence_id, attribute_code, custom_note))

    def map_all_licence_attributes(self,
            licence_id  : int,
            attributes  : list
        ): 

        for attribute in attributes:
            self.persist_licence_attribute_mapping(
                licence_id      = licence_id,
                attribute_code  = attribute
            )

class DeleteBoundary(QueryBoundary):
    pass

