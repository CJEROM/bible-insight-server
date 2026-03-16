# TEHMC - Translators Expansion of Hebrew Morphology Codes - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEHMC%20-%20Translators%20Expansion%20of%20Hebrew%20Morphology%20Codes%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile
from manager.managerhandler import ManagerHandler
from ingestor.stepbible.morphology.morphology_base import MorphologyBase

import re

class TEHMC(MorphologyBase):
    def __init__(self, manager, log):
        super().__init__(
            manager = manager, 
            log     = log
        )

    def download_files(self):

        FILE = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEHMC%20-%20Translators%20Expansion%20of%20Hebrew%20Morphology%20Codes%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TEHMC.txt",
            description         = "TEHMC - Translators Expansion of Hebrew Morphology Codes - STEPBible.org CC BY.txt",
            citation            = None
        )
        FILE.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TEHMC",
            source_name         = "TEHMC",
            version             = None,
            note                = "TEHMC - Translators Expansion of Hebrew Morphology Codes - STEPBible.org CC BY.txt"
        )
        FILE.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )
        self.process_file(FILE)

    def process_line_one(self, line: str):
        code, elements = line.split("\t", 1)

        normal_elements = re.sub(r"\(hence\s*[^)]*\)", "", elements)
        all_values = []

        matches = re.findall(r"\(hence\s*([^)]*)\)", elements)
        derived_elements = [None] * len(matches)
        derived_parents = [None] * len(matches)

        for i, match in enumerate(matches):
            matched_split = elements.split("(hence")

            derived_elements[0] = match.strip() # Grab first derived hence
            derived_parents[0] = matched_split[i].split(";")[-1].strip()
            
        for segment in normal_elements.split(";"):
            if segment.strip() == "":
                continue
            
            name, data = segment.split("=")

            feature_id = self.write.write_morphology_features(
                name    = name.strip()
            )

            parent_value_id = self.write.write_morphology_feature_value(
                feature_id  = feature_id,
                feature     = name.strip(),
                value       = data.strip()
            )
            all_values.append(parent_value_id)

            for i, parent in enumerate(derived_parents):
                if segment.strip() == parent and parent != None:
                    for segment in derived_elements[i].split(";"):
                        derived_name, derived_data = segment.split("=")

                        derived_feature_id = self.write.write_morphology_features(
                            name    = derived_name.strip()
                        )

                        derived_value_id = self.write.write_morphology_feature_value(
                            feature_id  = derived_feature_id,
                            feature     = derived_name.strip(),
                            value       = derived_data.strip()
                        )
                        all_values.append(derived_value_id)

                        self.write.write_morphology_derived_feature_value(
                            from_value      = parent_value_id,
                            derived_value   = derived_value_id
                        )
        
        return code, all_values
    
if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEHMC(
        manager     = manager,
        log         = log,
    )