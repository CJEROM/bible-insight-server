# TEGMC - Translators Expansion of Greek Morphhology Codes - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEGMC%20-%20Translators%20Expansion%20of%20Greek%20Morphhology%20Codes%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

class TEGMC():
    def __init__(self, 
            manager: ManagerHandler, 
            log: LogManager
        ):

        self.manager        = manager
        self.log            = log

        self.process_file()

    def download_files(self):

        MAT_JHN = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
            file_name           = "TAGNT MAT-JHN.txt",
            description         = "Translators Amalgamated Greek NT",
            citation            = None
        )
        MAT_JHN.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAGNT",
            source_name         = "TAGNT",
            version             = None,
            note                = "Translators Amalgamated Greek NT"
        )
        MAT_JHN.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        ACT_REV = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Act-Rev%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
            file_name           = "TAGNT ACT-REV.txt",
            description         = "Translators Amalgamated Greek NT",
            citation            = None
        )
        ACT_REV.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAGNT",
            source_name         = "TAGNT",
            version             = None,
            note                = "Translators Amalgamated Greek NT"
        )
        ACT_REV.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        return [MAT_JHN, ACT_REV]

    def process_file(self):
        downloaded_files = self.download_files()

        for file in downloaded_files:
            file_content = file.read_file()
            print(file_content[0:20])

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEGMC(
        manager     = manager,
        log         = log,
    )