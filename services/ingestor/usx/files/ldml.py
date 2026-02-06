from ingestor.usx.files.base_file import BaseFile

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class LDML(BaseFile):
    def __init__(self, main_manager: "ManagerHandler", log: "LogManager", source_id: int | None, file_path: Path = None):
        super.__init__(self, main_manager, log, source_id, file_path)
        # Currently no functionality derived from it, but we may use it for improving NLP
        #   Clean up so that tokenisation can be more accurate.
        pass