# TEGMC - Translators Expansion of Greek Morphhology Codes - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEGMC%20-%20Translators%20Expansion%20of%20Greek%20Morphhology%20Codes%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

SEGMENTS = set()

class TEGMC():
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
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEGMC%20-%20Translators%20Expansion%20of%20Greek%20Morphhology%20Codes%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TEGMC.txt",
            description         = "TEGMC - Translators Expansion of Greek Morphhology Codes - STEPBible.org CC BY.txt",
            citation            = None
        )
        FILE.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TEGMC",
            source_name         = "TEGMC",
            version             = None,
            note                = "TEGMC - Translators Expansion of Greek Morphhology Codes - STEPBible.org CC BY.txt"
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
        example         = block[3][1:].strip('\"') # Skip tab
        
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

        all_values = []

        for segment in elements.split(";"):
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
        
        return code, all_values

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEGMC(
        manager     = manager,
        log         = log,
    )