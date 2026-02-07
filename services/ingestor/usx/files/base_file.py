from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

from database.boundary.usx_boundary import USXReadBoundary, USXWriteBoundary

class BaseFile:
    def __init__(self, main_manager: "ManagerHandler", log: "LogManager", source_id: int | None, file_path: Path = None):
        self.manager        = main_manager
        self.obj            = main_manager.get_obj()
        self.db             = main_manager.get_db()
        self.log            = log

        self.source_id      = source_id
        self.this_file_path = file_path
        self.file_id        = None

        self.read           = USXReadBoundary(self.manager.get_db())
        self.write          = USXWriteBoundary(self.manager.get_db())

        self.check_file_exists()

    # CHECK FILE EXISTS FIRST?
    # IF IT DOES, USE UPDATE INSTEAD OF INSERT

    # EDIT METHOD: Needs to also include Object versioning
    def upload_file(self, 
            object_name, 
            file_path, 
            content_type, 
            data_format: str,
            version_note: str = None
        ) -> int:
        info = self.obj.upload_file(object_name, str(file_path), content_type)

        file_id = self.write.persist_file(
            etag            = info.etag,
            type            = info.content_type,
            file_path       = info.object_name,
            bucket          = info.bucket_name,
            source_id       = self.source_id,
            version_id      = info.version_id,
            data_format     = data_format,
            version_note    = version_note
        )

        self.log.log_to_file(f"Created New File: [{info.object_name}] [File ID:{file_id}] [Bucket: {info.bucket_name}] [etag: {info.etag}]", "BASE_FILE", "DEBUG")

        return file_id # Return file_id to link to
    
    def check_file_exists(self):
        if self.this_file_path.exists():
            pass
        elif self.this_file_path == None:
            self.log.log_to_file(f"File Read Failure: File Path NOT set!", "FILE", "WARN")
        else:
            self.log.log_to_file(f"File Read Failure: '{str(self.this_file_path)}' does not exist", "FILE", "ERROR")

    def read_file(self):
        with open(self.this_file_path, encoding="utf-8") as file:
            return file.read()