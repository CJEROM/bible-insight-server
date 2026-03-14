# Tagged-Bibles/TTESV - Tyndale Translation tags for ESV - TyndaleHouse.com STEPBible.org CC BY-NC.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Tagged-Bibles/TTESV%20-%20Tyndale%20Translation%20tags%20for%20ESV%20-%20TyndaleHouse.com%20STEPBible.org%20CC%20BY-NC.txt


from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

class TTESV():
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
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Tagged-Bibles/TTESV%20-%20Tyndale%20Translation%20tags%20for%20ESV%20-%20TyndaleHouse.com%20STEPBible.org%20CC%20BY-NC.txt",
            file_name           = "TTESV.txt",
            description         = "TTESV - Tyndale Translation tags for ESV - TyndaleHouse.com STEPBible.org",
            citation            = None
        )
        FILE.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TTESV",
            source_name         = "TTESV",
            version             = None,
            note                = "TTESV - Tyndale Translation tags for ESV - TyndaleHouse.com STEPBible.org"
        )
        FILE.map_license(
            license_code    = "CC BY-NC 4.0",
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

    TTESV(
        manager     = manager,
        log         = log,
    )