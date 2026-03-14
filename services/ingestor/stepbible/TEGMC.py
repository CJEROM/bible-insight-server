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
            intro = False

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

                        self.process_block(block)
        
        print()
        for segment in SEGMENTS:
            print(f"'{segment}'")

    def process_block(self, 
            block: list[str]
        ):
        pass
        # print(block)
        # line 1: full list of morphological elements with values
        self.process_line_one(block[0])
        # line 2: a phrase summarising these elements
        # self.process_line_two(block[1])
        # # line 3: a description of the function of this morphology
        # self.process_line_three(block[2])
        # # line 4: an example sentence that includes an underlined word having this same function.
        # self.process_line_four(block[3])

    def process_line_one(self, line: str):
        section_mapping = {
            "Case"                      : 0,
            "Adj.Numb."                 : 1,
            "Indeclinable"              : 2,
            "Name in Original language" : 3,
            "Form"                      : 4,
            "Voice"                     : 5,
            "Person"                    : 6,
            "Mood"                      : 7,
            "Name type"                 : 8,
            "Tense"                     : 9,
            "Gender"                    : 10,
            "Function"                  : 11,
            "Extra"                     : 12,
            "Original language"         : 13,
            "Number"                    : 14
        }
        sections = [None] * 15

        code, rest = line.split("\t", 1)
        segments = rest.split(";")
        for segment in segments:
            name, data = segment.split("=")
            sections[section_mapping[name.strip()]] = data.strip()
        
        # print(sections)

    def verify_line_one(self, block: str):
        code, rest = block[0].split("\t", 1)
        segments = rest.split(";")
        for segment in segments:
            segment_name = segment.split("=")[0].strip()
            SEGMENTS.add(segment_name)

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEGMC(
        manager     = manager,
        log         = log,
    )