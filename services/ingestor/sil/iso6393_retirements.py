from ingestor.usx.files.base_file import BaseFile
from database.boundary.sil_boundary import SILReadBoundary, SILWriteBoundary, SILDeleteBoundary

from pathlib import Path
import re

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class ISO6393Retirements(BaseFile):
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
        added_retirements = 0
        added_change_codes = 0

        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # ['Id', 'Ref_Name', 'Ret_Reason', 'Change_To', 'Ret_Remedy', 'Effective']
            header = next(f).rstrip("\n").split("\t") # Skip Header line

            # Go through file line by line
            for line in f:
                # Tab separated values -> Array
                columns = line.rstrip("\n").split("\t")

                # Persist to database
                retirement_id = self.write.persist_iso_retirements(
                    iso_code        = columns[0], # Id
                    ref_name        = columns[1], # Ref_Name
                    retired_reason  = columns[2], # Ret_Reason
                    retired_remedy  = columns[4], # Ret_Remedy
                    effective       = columns[5]  # Effective
                )
                added_retirements += 1
        
        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # ['Id', 'Ref_Name', 'Ret_Reason', 'Change_To', 'Ret_Remedy', 'Effective']
            header = next(f).rstrip("\n").split("\t") # Skip Header line

            # Go through file line by line
            for line in f:
                # Tab separated values -> Array
                columns = line.rstrip("\n").split("\t")

                # Change codes mapped to retirement_id
                if columns[3] != "":
                    # Get retirement to link to first
                    added_change_codes += self.create_retirement_changes(
                        from_iso    = columns[0],
                        to_iso      = columns[3] # Change_To
                    )

                # In the case of Ret_Reason 'S' - 'Split' it has all the new codes that the retired has been chaged to
                #       within 
                if columns[2] == 'S':
                    change_codes = re.findall(r"\[([^\]]+)\]", columns[4]) # Ret_Remedy
                    for code in change_codes:
                        # Get retirement to link to first
                        added_change_codes += self.create_retirement_changes(
                            from_iso    = columns[0],
                            to_iso      = code
                        )
            
        print(f"Added [{added_retirements}] Retirements + [{added_change_codes}] Change Codes")

    def create_retirement_changes(self, 
            from_iso : str, 
            to_iso: str
        ):
        added_change_codes = 0

        from_retirement = self.read.get_retirement(from_iso)
        
        if from_retirement != None:
            to_retirement = self.read.get_retirement(to_iso)

            if to_retirement == None:
                self.write.persist_iso_retirement_changes(
                    from_retirement     = from_retirement,
                    to_iso_code         = to_iso,
                    to_retirement       = None
                )
                
            else:
                self.write.persist_iso_retirement_changes(
                    from_retirement     = from_retirement,
                    to_iso_code         = None,
                    to_retirement       = to_retirement
                )

            added_change_codes += 1
        else:
            print(to_iso)
            pass

        return added_change_codes
                
if __name__ == "__main__":
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

    ISO6393Retirements(
        ManagerHandler(),
        LogManager(),
        0,
        Path("/Users/cepherom/git/bible-insight-server/services/downloads/iso-639-3_Code_Tables_20260115/iso-639-3_Retirements.tab")
    )