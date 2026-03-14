# TEHMC - Translators Expansion of Hebrew Morphology Codes - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEHMC%20-%20Translators%20Expansion%20of%20Hebrew%20Morphology%20Codes%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

import re

class TEHMC():
    def __init__(self, 
            manager: ManagerHandler, 
            log: LogManager
        ):

        self.manager        = manager
        self.log            = log
        self.db             = manager.get_db()

        self.read           = StepBibleReadBoundary(self.db)
        self.write          = StepBibleWriteBoundary(self.db)


        self.process_file()

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

        return FILE

    def process_file(self):
        downloaded_file = self.download_files()

        # Read the downloaded file
        with open(downloaded_file.this_file_path, "r", encoding="utf-8") as f:
            # Loop through file line by line
            count = 0
            valid = False

            for line in f:

                if line.startswith("$"):
                    if count == 0:
                        valid = True

                    count += 1

                    if valid:
                        block = [
                            next(f).rstrip("\n"),
                            next(f).rstrip("\n"),
                            next(f).rstrip("\n"),
                            next(f).rstrip("\n"),
                        ]

                        self.process_block(
                            block       = block, 
                            source_id   = downloaded_file.source_id
                        )
        
        self.db.commit()

    def process_block(self, 
            block       : list[str],
            source_id   : int
        ):
        # line 1: full list of morphological elements with values
        code, elements  = self.process_line_one(block[0])
        # line 2: morphology: a phrase summarising these elements
        morphology      = block[1][1:].strip('\"') # Skip tab
        # line 3: explanation: a description of the function of this morphology
        explanation     = block[2][1:].strip('\"') # Skip tab
        # line 4: example: an example sentence that includes an underlined word having this same function.
        example         = block[3][10:].strip('\"') # Skip tab + 'Example: '
        
        code_id = self.write.write_morphological_code(
            iso         = None,
            code        = code,
            morphology  = morphology,
            explanation = explanation,
            example     = example,
            source_id   = source_id,
            raw_data    = "\n".join(block)
        )

        for value_id in elements:
            self.write.write_morphology_code_values(
                code_id     = code_id,
                value_id    = value_id
            )

    def process_line_one(self, line: str):
        code, elements = line.split("\t", 1)

        normal_elements = elements
        derived_elements = None
        derived_parent = None

        all_values = []

        match = re.search(r"\(hence\s*([^)]*)\)", elements)
        if match:
            derived_elements = match.group(1)[7: -2] # Exclude (hence )
            derived_parent = elements.split("(hence")[0].split(";")[-1].strip()
            normal_elements = re.sub(r"\(hence\s*[^)]*\)", "", elements)
            
        for segment in normal_elements.split(";"):
            if segment.strip() == "":
                continue
            
            name, data = segment.split("=")

            feature_id = self.write.write_morphology_features(
                name    = name
            )

            parent_value_id = self.write.write_morphology_feature_value(
                feature_id  = feature_id,
                feature     = name,
                value       = data
            )
            all_values.append(parent_value_id)

            if segment == derived_parent and derived_parent != None:
                for segment in derived_elements.split(";"):
                    name, data = segment.split("=")

                    derived_feature_id = self.write.write_morphology_features(
                        name    = name
                    )

                    derived_value_id = self.write.write_morphology_feature_value(
                        feature_id  = derived_feature_id,
                        feature     = name,
                        value       = data
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