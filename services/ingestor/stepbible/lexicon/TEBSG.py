# Lexicons/TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

import re

class TEBSG():
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
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TEBSG.txt",
            description         = "TEBSG - Translators Brief lexicon of Extended Strongs for Greek",
            citation            = None
        )
        FILE.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TEBSG",
            source_name         = "TEBSG",
            version             = None,
            note                = "TEBSG - Translators Brief lexicon of Extended Strongs for Greek"
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
            valid = False

            for line in f:
                if line.startswith("eStrong	dStrong	uStrong	Greek	Transliteration	Morph	Gloss	Abbott-Smith lexicon (AS), with gaps occationally filled from edited versions of  Middle LSJ "):
                    valid = True
                    continue
                
                # Skip the empty lines so we can start ingesting the data
                if line.strip() == "" or line.startswith("==="):
                    continue

                if valid:
                    columns = line.split("\t")

                    morph_code = columns[5] if columns[5].strip() != "" else None

                    data_id = self.write.write_lexicon_data(
                        e_strong            = columns[0],
                        d_strong            = self. get_strong_relationship(
                                                raw_d_strong    = columns[1],
                                                result          = 0
                                            ),
                        d_u_relationship    = self. get_strong_relationship(
                                                raw_d_strong    = columns[1],
                                                result          = 1
                                            ),
                        u_strong            = columns[2],
                        text                = columns[3],
                        transliteration     = columns[4],
                        morph               = morph_code,
                        gloss               = columns[6],
                        meaning             = columns[7].strip(),
                        source_id           = downloaded_file.source_id
                    )

                    if morph_code:
                        self.process_morph_code(
                            data_id = data_id,
                            code    = morph_code
                        )
        
        self.db.commit()

    import re

    def process_morph_code(self, data_id: int, code: str):

        # -------------------------------------------------------
        # 1. Expand feature alternates (case 3 -> case 4)
        # Example: G:N-M/F -> G:N-M / G:N-F
        # -------------------------------------------------------

        match = re.search(r"([A-Z]:[A-Z]+-[^/\s]+)/([^\s+]+)", code)

        if match:
            base_left = match.group(1)      # e.g. G:N-M
            alt = match.group(2)            # e.g. F

            prefix = base_left.rsplit("-", 1)[0]  # G:N

            left = base_left
            right = f"{prefix}-{alt}"

            expanded = code.replace(match.group(0), f"{left} / {right}")

            # Re-run parser with expanded string
            return self.process_morph_code(data_id, expanded)

        # -------------------------------------------------------
        # 2. Split components normally
        # -------------------------------------------------------

        components = re.split(r"(\s*[+/]\s*)", code)

        relation_type = "single"

        position = 1

        for part in components:

            # ---------------------------------------------------
            # Detect relationship separators
            # ---------------------------------------------------

            if part == '+':
                relation_type = "compound"
                continue

            elif part == ' + ':
                relation_type = "multi_word"
                continue

            elif part.strip() == '/':
                relation_type = "alternate"
                continue

            # ---------------------------------------------------
            # Otherwise it's a morphology code
            # ---------------------------------------------------

            language = None
            sub_code = None

            if ":" in part:
                language, sub_code = part.split(":", 1)

            else:
                # Observed only in Hebrew entries
                language = "H"
                sub_code = part

            if self.read.find_morph_code(sub_code) == None:
                print(f"\t{sub_code}")
            else:
                self.write.map_lexicon_morph_codes(
                    data_id         = data_id,
                    position        = position,
                    relation_type   = relation_type,
                    language        = language,
                    sub_code        = sub_code
                )

            position += 1

    def get_strong_relationship(self,
            raw_d_strong    : str,
            result          : int # 0 (d_strong) | 1 (relationship)
        ):
        d_strong = raw_d_strong.split("=")[0].strip()

        relationship = None
        if len(raw_d_strong.split("=")) < 2:
            relationship = "="
        else:
            relationship = raw_d_strong.split("=")[1].strip()

        if result == 0:
            return d_strong
        elif result == 1:
            return relationship
        else: 
            return None

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEBSG(
        manager     = manager,
        log         = log,
    )