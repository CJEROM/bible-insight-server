from ingestor.usx.files.base_file import BaseFile

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

        self.read_file()

    def read_file(self):
        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # ['M_Id', 'I_Id', 'I_Status']
            header = next(f).rstrip("\n").split("\t")
            
            print(header)

            for line in f:
                columns = line.rstrip("\n").split("\t")
                # print(columns)
                # columns is now a list of values
                
if __name__ == "__main__":
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

    ISO6393MacroLanguages(
        ManagerHandler(),
        LogManager(),
        0,
        Path("/Users/cepherom/git/bible-insight-server/services/downloads/iso-639-3_Code_Tables_20260115/iso-639-3-macrolanguages.tab")
    )