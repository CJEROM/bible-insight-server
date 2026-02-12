from ingestor.usx.files.base_file import BaseFile
from database.boundary.sil_boundary import SILReadBoundary, SILWriteBoundary, SILDeleteBoundary

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class ISO6393Names(BaseFile):
    def __init__(self, 
            main_manager: "ManagerHandler", 
            log         : "LogManager", 
            source_id   : int, 
            file_path   : Path
        ):
        super().__init__(main_manager, log, source_id, file_path)

        self.read           = SILReadBoundary(self.db)
        self.write          = SILWriteBoundary(self.db)

        self.log.log_to_file(f"SIL Ingestion of Active ISO 639-3 Language Code Names ...", "INGESTOR", "INFO")

        self.read_file()

    def read_file(self):
        added_iso_code_names = 0

        self.log.log_to_file(f"Reading File ...", "INGESTOR", "INFO")

        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # ['Id', 'Print_Name', 'Inverted_Name']
            header = next(f).rstrip("\n").split("\t")

            for line in f:
                columns = line.rstrip("\n").split("\t")
                
                self.write.persist_iso_names(
                    iso_code        = columns[0],
                    print_name      = columns[1],
                    inverted_name   = columns[2]
                )
                added_iso_code_names += 1
                self.log.log_to_file(f"New ISO 639-3 Code Name: {columns}", "INGESTOR", "TRACE")

        print(f"Added [{added_iso_code_names}] Iso Code Names")
        self.log.log_to_file(f"Added [{added_iso_code_names}] New ISO 639-3 Code Names", "INGESTOR", "INFO")
        
                
if __name__ == "__main__":
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

    ISO6393Names(
        ManagerHandler(),
        LogManager(),
        0,
        Path("/Users/cepherom/git/bible-insight-server/services/downloads/iso-639-3_Code_Tables_20260115/iso-639-3_Name_Index.tab")
    )