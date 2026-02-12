from manager.managerhandler import ManagerHandler

from database.boundary.unicode_boundary import UnicodeWriteBoundary, UnicodeReadBoundary, UnicodeDeleteBoundary

from ingestor.unicode.iso15924 import ISO15927

import requests
import os
import shutil
from pathlib import Path

class UnicodeIngestor:
    def __init__(self,
            manager: ManagerHandler | None = None
        ):
        self.manager        = manager or ManagerHandler()
        self.log            = self.manager.create_log_in_folder(["logs", "ingestor", "unicode"])
        self.db             = self.manager.get_db()

        self.log.set_logging_level(1)

        self.obj            = self.manager.get_obj()
        self.obj.create_bucket(
            bucket_name     = "reference-data",
            is_versioned    = True,
            is_default      = True
        )

        self.read           = UnicodeReadBoundary(self.db)
        self.write          = UnicodeWriteBoundary(self.db)

        self.object_start   = "Unicode-data"

        self.download_path  = Path(__file__).parents[2] / "downloads"
        os.makedirs(self.download_path, exist_ok=True)

        self.source_id      = None

        self.read_download("https://www.unicode.org/iso15924/iso15924.txt")

        self.db.commit()
        self.log.log_to_file(f"SIL Ingestion of Active ISO 639-3 Language Codes ...", "INGESTOR", "INFO")

    def create_source(self,
            source_url : str
        ) -> int:
        parent_source = self.read.find_source("UNICODE")

        source_id = self.write.persist_source(
            source_type         = "DAT", # Dataset
            code                = "ISO15924",
            name                = "ISO 15924",
            description         = "The ISO 15924/RA receives and reviews applications for requesting new script codes and for the change of existing ones according to criteria indicated in the standard. It maintains an accurate list of information associated with registered script codes, processes updates of registered script codes, and distributes them on a regular basis to subscribers and other parties",
            version             = None,
            url                 = source_url,
            note                = None,
            parent_source       = parent_source,
            official_citation   = "Copyright © 1991-Present Unicode, Inc."
        )

        return source_id
    
    def map_license(self):
        # Maps licensing details to the files or at least the source for now
        found_licence = self.read.find_license("UNICODE")

        if found_licence == None:
            licence_id = self.write.persist_licence(
                source_id   = self.source_id,
                code        = "UNICODE",
                name        = "ISO 15924 Terms of Use",
                version     = None,
                link        = "https://www.unicode.org/copyright.html",
                valid_from  = None,
                valid_until = None,
                notes       = "CUSTOM TERMS OF USE"
            )

            licence_attributes = [
                "ATTRIBUTION",
                "NO_DERIVATIVES",
                "NO_DISTRIBUTION"
            ]
            self.write.map_all_licence_attributes(
                licence_id      = licence_id,
                attributes      = licence_attributes
            )

    def read_download(self, 
            source_url : str              
        ):

        response            = requests.get(source_url, stream = True)
        response.raise_for_status()

        file_name = "iso15924.txt"
        new_file_path = self.download_path / file_name

        with open(new_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: # Filter out keep-alive chunks
                    f.write(chunk)

        self.log.log_to_file(f"Downloaded Latest Unicode ISO 15924 File to: {new_file_path}!", "INGESTOR", "INFO")

        self.source_id      = self.create_source(source_url)
        self.map_license()

        scripts = ISO15927(
            main_manager    = self.manager,
            log             = self.log,
            source_id       = self.source_id,
            file_path       = new_file_path
        )
        
        scripts.upload_file(
            object_name     = f"{self.object_start}/{file_name}",
            file_path       = new_file_path,
            content_type    = "text/plain",
            data_format     = "TXT"
        )

if __name__ == "__main__":
    UnicodeIngestor()