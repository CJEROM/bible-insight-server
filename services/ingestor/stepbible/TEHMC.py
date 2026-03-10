# TEHMC - Translators Expansion of Hebrew Morphology Codes - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEHMC%20-%20Translators%20Expansion%20of%20Hebrew%20Morphology%20Codes%20-%20STEPBible.org%20CC%20BY.txt


from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

class TEHMC():
    def __init__(self, 
            manager: ManagerHandler, 
            log: LogManager
        ):

        self.manager        = manager
        self.log            = log

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

        file_content = downloaded_file.read_file()
        print(file_content[0:20])

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEHMC(
        manager     = manager,
        log         = log,
    )