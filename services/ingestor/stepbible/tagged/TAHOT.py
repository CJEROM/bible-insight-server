# Translators Amalgamated OT+NT/TAHOT Gen-Deu - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Gen-Deu%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Jos-Est%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Job-Sng%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Isa-Mal%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt


from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

class TAHOT():
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

        GEN_DEU = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Gen-Deu%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TAHOT GEN_DEU.txt",
            description         = "TAHOT Gen-Deu - Translators Amalgamated Hebrew OT",
            citation            = None
        )
        GEN_DEU.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAHOT",
            source_name         = "TAHOT",
            version             = None,
            note                = "TAHOT - Translators Amalgamated Hebrew OT"
        )
        GEN_DEU.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        JOS_EST = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Jos-Est%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TAHOT JOS_EST.txt",
            description         = "TAHOT Jos-Est - Translators Amalgamated Hebrew OT",
            citation            = None
        )
        JOS_EST.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAHOT",
            source_name         = "TAHOT",
            version             = None,
            note                = "TAHOT - Translators Amalgamated Hebrew OT"
        )
        JOS_EST.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        JOB_SNG = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Job-Sng%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TAHOT JOB_SNG.txt",
            description         = "TAHOT Job-Sng - Translators Amalgamated Hebrew OT",
            citation            = None
        )
        JOB_SNG.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAHOT",
            source_name         = "TAHOT",
            version             = None,
            note                = "TAHOT - Translators Amalgamated Hebrew OT"
        )
        JOB_SNG.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        ISA_MAL = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAHOT%20Isa-Mal%20-%20Translators%20Amalgamated%20Hebrew%20OT%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TAHOT ISA_MAL.txt",
            description         = "TAHOT Isa-Mal - Translators Amalgamated Hebrew OT",
            citation            = None
        )
        ISA_MAL.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAHOT",
            source_name         = "TAHOT",
            version             = None,
            note                = "TAHOT - Translators Amalgamated Hebrew OT"
        )
        ISA_MAL.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        return [GEN_DEU, JOS_EST, JOB_SNG, ISA_MAL]

    def process_file(self):
        downloaded_files = self.download_files()

        for file in downloaded_files:
            file_content = file.read_file()
            print(file_content[0:20])

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TAHOT(
        manager     = manager,
        log         = log,
    )