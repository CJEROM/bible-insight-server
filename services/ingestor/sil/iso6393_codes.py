from ingestor.usx.files.base_file import BaseFile
from database.boundary.sil_boundary import SILReadBoundary, SILWriteBoundary, SILDeleteBoundary

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class ISO6393Codes(BaseFile):
    def __init__(self, 
            main_manager: "ManagerHandler", 
            log         : "LogManager", 
            source_id   : int, 
            file_path   : Path
        ):
        super().__init__(main_manager, log, source_id, file_path)

        self.read           = SILReadBoundary(self.db)
        self.write          = SILWriteBoundary(self.db)

        self.read_file()

    def read_file(self):
        added_codes = 0
        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # ['Id', 'Part2b', 'Part2t', 'Part1', 'Scope', 'Language_Type', 'Ref_Name', 'Comment']
            header = next(f).rstrip("\n").split("\t")

            for line in f:
                columns = line.rstrip("\n").split("\t")

                self.write.persist_iso_code(
                    iso_code    = columns[0], # Id
                    part2b      = columns[1], # Part2b
                    part2t      = columns[2], # Part2t
                    part1       = columns[3], # Part1
                    scope       = columns[4], # Scope
                    type        = columns[5], # Language_Type
                    ref_name    = columns[6], # Ref_Name
                    status      = 'A',        # DEFAULT - All Iso Codes importer are active ones
                    comment     = columns[7]  # Comment
                )
                added_codes += 1
        
        print(f"Added [{added_codes}] New ISO 639-3 Codes")

                
if __name__ == "__main__":
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

    ISO6393Codes(
        ManagerHandler(),
        LogManager(),
        0,
        Path("/Users/cepherom/git/bible-insight-server/services/downloads/iso-639-3_Code_Tables_20260115/iso-639-3.tab")
    )