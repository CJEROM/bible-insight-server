from ingestor.usx.files.base_file import BaseFile
from database.boundary.unicode_boundary import UnicodeReadBoundary, UnicodeWriteBoundary

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class ISO15927(BaseFile):
    def __init__(self, 
            main_manager: "ManagerHandler", 
            log         : "LogManager", 
            source_id   : int, 
            file_path   : Path
        ):
        super().__init__(main_manager, log, source_id, file_path)

        self.read           = UnicodeReadBoundary(self.db)
        self.write          = UnicodeWriteBoundary(self.db)

        self.read_file()

    def read_file(self):
        added_scripts = 0

        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # Code ; N° ; English Name ; Nom français ; PVA ; Unicode Version ; Date
            
            # Skip all header lines
            header_lines = 7
            for _ in range(header_lines):
                next(f)

            # Split all actual data rows
            for line in f:
                columns = line.rstrip("\n").split(";")

                self.write.persist_script(
                    code            = columns[0], 
                    numeric         = columns[1], 
                    name            = columns[2],
                    unicode_age     = columns[5], 
                    date_added      = columns[6]
                )
                added_scripts += 1
                self.log.log_to_file(f"New ISO 15924 Code: {columns}", "INGESTOR", "TRACE")
        
        print(f"Added [{added_scripts}] New ISO 15924 Codes")
        self.log.log_to_file(f"Added [{added_scripts}] New ISO 15924 Codes", "INGESTOR", "INFO")

if __name__ == "__main__":
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

    ISO15927(
        ManagerHandler(),
        LogManager(),
        0,
        Path("/Users/cepherom/git/bible-insight-server/services/downloads/iso15924.txt")
    )