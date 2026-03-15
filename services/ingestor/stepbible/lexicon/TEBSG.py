# Lexicons/TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

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

                    self.process_morph_code(
                        code    = columns[5]
                    )

                    self.write.write_lexicon_data(
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
                        morph               = columns[5],
                        gloss               = columns[6],
                        meaning             = columns[7],
                        source_id           = downloaded_file.source_id
                    )
        
        self.db.commit()

    def process_morph_code(self,
            code    : str
        ):
        language        = None #code.split(":")[0]
        type            = None
        gender          = None
        number          = None
        extra           = None

        self.write.write_lexicon_morph_codes(
            code        = code,
            language    = language,
            type        = type,
            gender      = gender,
            number      = number,
            extra       = extra
        )

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