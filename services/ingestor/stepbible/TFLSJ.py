# Lexicons/TFLSJ  0-5624 - Translators Formatted full LSJ Bible lexicon - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TFLSJ%20%200-5624%20-%20Translators%20Formatted%20full%20LSJ%20Bible%20lexicon%20-%20STEPBible.org%20CC%20BY.txt

# Lexicons/TFLSJ extra - Translators Formatted full LSJ Bible lexicon - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TFLSJ%20extra%20-%20Translators%20Formatted%20full%20LSJ%20Bible%20lexicon%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

class TFLSJ():
    def __init__(self, 
            manager: ManagerHandler, 
            log: LogManager
        ):

        self.manager        = manager
        self.log            = log

        self.process_file()

    def download_files(self):

        NORMAL = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TFLSJ%20%200-5624%20-%20Translators%20Formatted%20full%20LSJ%20Bible%20lexicon%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TFLSJ.txt",
            description         = "TFLSJ 0-5624 - Translators Formatted full LSJ Bible lexicon",
            citation            = None
        )
        NORMAL.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TFLSJ",
            source_name         = "TFLSJ",
            version             = None,
            note                = "TFLSJ 0-5624 - Translators Formatted full LSJ Bible lexicon"
        )
        NORMAL.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        EXTRA = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TFLSJ%20extra%20-%20Translators%20Formatted%20full%20LSJ%20Bible%20lexicon%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TFLSJ EXTRA.txt",
            description         = "TFLSJ extra - Translators Formatted full LSJ Bible lexicon",
            citation            = None
        )
        EXTRA.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TFLSJ",
            source_name         = "TFLSJ",
            version             = None,
            note                = "TFLSJ extra - Translators Formatted full LSJ Bible lexicon"
        )
        EXTRA.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        return [NORMAL, EXTRA]

    def process_file(self):
        downloaded_files = self.download_files()

        for file in downloaded_files:
            file_content = file.read_file()
            print(file_content[0:20])

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TFLSJ(
        manager     = manager,
        log         = log,
    )