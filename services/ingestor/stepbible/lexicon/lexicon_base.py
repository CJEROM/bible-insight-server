# Lexicons/TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESH%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Hebrew%20-%20STEPBible.org%20CC%20BY.txt


from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

import re

class LexiconBase():
    def __init__(self, 
            manager         : ManagerHandler, 
            log             : LogManager,
            start_marker    : str,
            codes           : dict
        ):

        self.manager        = manager
        self.log            = log
        self.db             = manager.get_db()

        self.read           = StepBibleReadBoundary(self.db)
        self.write          = StepBibleWriteBoundary(self.db)

        self.start_marker   = start_marker

        self.exceptions     = set()
        self.codes          = codes

        self.download_files()

    def download_files(self):
        pass
        # Can run this more than once here as well
        # Get FILE -> DownloadFile
        # self.process_file(FILE)

    def process_file(self, downloaded_file: DownloadFile):

        self.add_extra_morph_codes(downloaded_file.source_id)

        # Read the downloaded file
        with open(downloaded_file.this_file_path, "r", encoding="utf-8") as f:
            # Loop through file line by line
            valid = False

            for line in f:
                if line.startswith(self.start_marker):
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

        for exception in self.exceptions:
            print(exception)

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
                # First letter is language for the Hebrew Morphology codes
                #   Either H or A
                language = code[0] 
                sub_code = part

            # FOR EXCEPTIONS I KNOW OF - UNCLEAN DATA
            if sub_code == 'C-':
                sub_code = 'C'
            elif sub_code == '':
                sub_code = None

            if self.read.find_morph_code(sub_code) == None:
                # self.exceptions.add(f"\t{code}\t->\t{sub_code}\t[{relation_type}]")
                # self.exceptions.add(f"\"{sub_code}\"\t: "+"{},")
                self.exceptions.add(sub_code)
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
        
    def add_extra_morph_codes(self, source_id):
        for code, elements in self.codes.items():
            code_id = self.write.write_morphological_code(
                iso         = None,
                code        = code,
                morphology  = None,
                explanation = None,
                example     = None,
                source_id   = source_id,
                raw_data    = None
            )

            for feature, value in elements.items():
                feature_id = self.write.write_morphology_features(
                    name    = feature.strip()
                )

                value_id = self.write.write_morphology_feature_value(
                    feature_id  = feature_id,
                    feature     = feature.strip(),
                    value       = value.strip()
                )
                
                self.write.write_morphology_code_values(
                    code_id     = code_id,
                    value_id    = value_id
                )

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    LexiconBase(
        manager         = manager,
        log             = log,
        start_marker    = None
    )