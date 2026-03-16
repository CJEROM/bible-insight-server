# TEGMC - Translators Expansion of Greek Morphhology Codes - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/TEGMC%20-%20Translators%20Expansion%20of%20Greek%20Morphhology%20Codes%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile
from manager.managerhandler import ManagerHandler
from ingestor.stepbible.morphology.morphology_base import MorphologyBase

class TEGMC(MorphologyBase):
    def __init__(self, manager, log):
        super().__init__(
            manager = manager, 
            log     = log
        )

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
        self.process_file(FILE)

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEGMC(
        manager     = manager,
        log         = log,
    )