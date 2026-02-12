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
        added_iso_codes = 0

        with open(self.this_file_path, "r", encoding="utf-8") as f:
            # ['Id', 'Ref_Name', 'Ret_Reason', 'Change_To', 'Ret_Remedy', 'Effective']
            header = next(f).rstrip("\n").split("\t") # Skip Header line

            # Go through file line by line
            for line in f:
                # Tab separated values -> Array
                columns = line.rstrip("\n").split("\t")

                self.write.persist_iso_code(
                    iso_code    = columns[0],   # Id
                    part2b      = None,         # Part2b
                    part2t      = None,         # Part2t
                    part1       = None,         # Part1
                    scope       = 'U',          # DEFAULT: Unknown -> Scope
                    type        = 'U',          # DEFAULT: Unknown -> Language_Type
                    ref_name    = columns[1],   # Ref_Name
                    status      = 'R',          # DEFAULT: Retired 
                    comment     = 'DERIVED -> FROM Retirements'  # Comment
                )
                added_iso_codes += 1

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

                retirement_id = None

                # Change codes mapped to retirement_id
                if columns[3] != "":
                    # Get retirement to link to first
                    retirement_id = self.read.get_retirement(columns[0])
                
                    if retirement_id != None:
                        print(retirement_id)

                        self.write.persist_iso_retirement_changes(
                            retirement_id   = retirement_id,
                            changed_to      = columns[3] # Change_To
                        )
                        added_change_codes += 1
                    else:
                        print(columns)
                        pass

                # In the case of Ret_Reason 'S' - 'Split' it has all the new codes that the retired has been chaged to
                #       within 
                if columns[2] == 'S':
                    change_codes = re.findall(r"\[([^\]]+)\]", columns[4]) # Ret_Remedy
                    for code in change_codes:
                        # Get retirement to link to first
                        retirement_id = self.read.get_retirement(code)

                        if retirement_id != None:
                            print(retirement_id)
                            self.write.persist_iso_retirement_changes(
                                retirement_id   = retirement_id,
                                changed_to      = code
                            )
                            added_change_codes += 1
                        else:
                            print(columns)
            
        print(f"Added [{added_retirements}] Retirements + [{added_change_codes}] Change Codes + [{added_iso_codes}] Retired ISO Codes")
                
if __name__ == "__main__":
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

    ISO6393Retirements(
        ManagerHandler(),
        LogManager(),
        0,
        Path("/Users/cepherom/git/bible-insight-server/services/downloads/iso-639-3_Code_Tables_20260115/iso-639-3_Retirements.tab")
    )