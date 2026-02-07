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

class WriteBoundary(QueryBoundary):
    pass

class DeleteBoundary(QueryBoundary):
    pass

