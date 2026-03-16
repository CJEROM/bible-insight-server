# Lexicons/TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESH%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Hebrew%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler

from ingestor.stepbible.lexicon.lexicon_base import LexiconBase

CODES = {
    
}

class TEBSH(LexiconBase):
    def __init__(self, manager, log):
        super().__init__(
            manager         = manager, 
            log             = log, 
            start_marker    = "eStrong#	dStrong	uStrong	Hebrew	Transliteration	Morph	Gloss	Meaning",
            codes           = CODES
        )

    def download_files(self):

        FILE = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESH%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Hebrew%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TEBSH.txt",
            description         = "TEBSH - Translators Brief lexicon of Extended Strongs for Hebrew",
            citation            = None
        )
        FILE.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TEBSH",
            source_name         = "TEBSH",
            version             = None,
            note                = "TEBSH - Translators Brief lexicon of Extended Strongs for Hebrew"
        )
        FILE.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )
        self.process_file(FILE)

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEBSH(
        manager     = manager,
        log         = log,
    )