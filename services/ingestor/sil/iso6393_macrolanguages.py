from ingestor.usx.files.base_file import BaseFile
from database.boundary.sil_boundary import SILReadBoundary, SILWriteBoundary, SILDeleteBoundary

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class ISO6393MacroLanguages(BaseFile):
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
        added_macro_languages = 0

        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # ['M_Id', 'I_Id', 'I_Status']
            header = next(f).rstrip("\n").split("\t")

            for line in f:
                columns = line.rstrip("\n").split("\t")
                
                if (self.read.is_iso_code(columns[1])):
                    self.write.persist_iso_macrolanguage(
                        macro_id    = columns[0], # M_Id
                        iso_id      = columns[1], # I_Id
                        iso_status  = columns[2]  # I_Status
                    )
                    added_macro_languages += 1
                else:
                    # If macro language retired, then insert that into iso_codes
                    self.write.persist_iso_code(
                        iso_code    = columns[0],   # Id
                        part2b      = None,         # Part2b
                        part2t      = None,         # Part2t
                        part1       = None,         # Part1
                        scope       = 'M',          # DEFAULT: Unknown -> Scope
                        type        = 'U',          # DEFAULT: Unknown -> Language_Type
                        ref_name    = 'UNKNOWN',    # Ref_Name
                        status      = 'R',          # DEFAULT: Retired 
                        comment     = 'DERIVED -> FROM Macrolanguages'  # Comment
                    )

        print(f"Added [{added_macro_languages}] Macro Languages")
                
if __name__ == "__main__":
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

    ISO6393MacroLanguages(
        ManagerHandler(),
        LogManager(),
        0,
        Path("/Users/cepherom/git/bible-insight-server/services/downloads/iso-639-3_Code_Tables_20260115/iso-639-3-macrolanguages.tab")
    )