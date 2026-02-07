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

class WriteBoundary(QueryBoundary):
    pass

class DeleteBoundary(QueryBoundary):
    pass

