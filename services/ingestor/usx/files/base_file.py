from pathlib import Path
import hashlib

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
    # IF IT DOES, USE UPDATE INSTEAD OF INSERT?


    def sha256_file(path: str) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def upload_file(self, 
            object_name     : str, 
            file_path       : Path, 
            content_type    : str, 
            data_format     : str,
            version_note    : str = None
        ) -> int:
        # New file's hash
        file_hash = self.sha256_file(file_path)

        # Try find matching hash

        matched_file = self.read.get_file_by_hash(
            content_hash    = file_hash,
            data_format     = data_format
        )
        file_id = None

        # Only upload the file to object storage, if it changed from its previous version
        if matched_file is None:
            info = self.obj.upload_file(object_name, str(file_path), content_type)

            file_id = self.write.persist_file(
                etag            = info.etag,
                type            = info.content_type,
                object_path     = info.object_name,
                bucket          = info.bucket_name,
                source_id       = self.source_id,
                version_id      = info.version_id,
                data_format     = data_format,
                version_note    = version_note,
                content_hash    = file_hash
            )
            self.log.log_to_file(f"Created New File: [{object_name}] [File ID:{file_id}] [Bucket: {info.bucket_name}] [etag: {info.etag}]", "BASE_FILE", "DEBUG")

        else:
            file_id = matched_file
            self.log.log_to_file(f"File Version Matched: [{object_name}] [File ID:{file_id}] [Bucket: {self.obj.bucket}]", "BASE_FILE", "DEBUG")
        
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