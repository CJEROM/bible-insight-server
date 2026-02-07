from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.dbmanager import DBManager

class QueryBoundary:
    def __init__(self, db_manager: "DBManager"):
        self.db = db_manager

class ReadBoundary(QueryBoundary):
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
    
    def get_all_label_projects(self) -> list[tuple[int, int, str, str]]:
        query = """
            SELECT tlp.project_id, tlp.translation_id, lp.name, lp.description
            FROM nlp.translation_labelling_projects tlp
            JOIN nlp.labelling_projects lp ON tlp.project_id = lp.id;
        """
        result = self.db.fetch_all(query)
        return result

class WriteBoundary(QueryBoundary):
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
    
class DeleteBoundary(QueryBoundary):
    pass

