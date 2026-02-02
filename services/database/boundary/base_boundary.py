from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.dbmanager import DBManager

class QueryBoundary:
    def __init__(self, db_manager: "DBManager"):
        self.db = db_manager

class ReadBoundary(QueryBoundary):
    pass

class WriteBoundary(QueryBoundary):
    pass

class DeleteBoundary(QueryBoundary):
    pass

