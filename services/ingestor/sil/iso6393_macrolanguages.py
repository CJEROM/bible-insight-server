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
                
                #
                retirement_id = self.read.get_retirement(columns[1])
                if retirement_id == None:
                    self.write.persist_iso_macrolanguage(
                        macro_id        = columns[0], # M_Id
                        iso_id          = columns[1], # I_Id
                        retirement_id   = None,
                        iso_status      = columns[2]  # I_Status
                    )
                    added_macro_languages += 1
                else:
                    self.write.persist_iso_macrolanguage(
                        macro_id        = columns[0], # M_Id
                        iso_id          = None, # I_Id
                        retirement_id   = retirement_id,
                        iso_status      = columns[2]  # I_Status
                    )
                    added_macro_languages += 1

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