from ingestor.usx.files.base_file import BaseFile
from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

from pathlib import Path
import os
import requests
    
class DownloadFile(BaseFile):
    # Downloading file from link -> return download path 
    #       maps source to licence, create licence if necessary + map attributes
    def __init__(self, 
            main_manager        : ManagerHandler, 
            log                 : LogManager, 
            link                : str, 
            file_name           : str,
            description         : str       | None = None,
            citation            : str       | None = None
        ):
        self.manager            = main_manager
        self.log                = log
        self.db                 = self.manager.get_db()
        self.obj                = self.manager.get_obj()
        self.obj.create_bucket(
            bucket_name     = "reference-data",
            is_versioned    = True,
            is_default      = True
        )

        self.read               = StepBibleReadBoundary(self.db)    
        self.write              = StepBibleWriteBoundary(self.db)

        self.source_id          = None
        self.source_url         = link
        self.file_name          = file_name
        self.description        = description
        self.official_citation  = citation

        self.download_path      = Path(__file__).parents[2] / "downloads"
        os.makedirs(self.download_path, exist_ok=True)

        self.this_file_path     = self.download()
        self.file_id            = None

        self.upload_file(
            object_name     = f"STEPBIBLE/{self.file_name}",
            file_path       = self.this_file_path,
            content_type    = "text/plain",
            data_format     = "TXT",
            version_note    = None
        )

    def download(self):
        response        = requests.get(self.source_url, stream=True)
        response.raise_for_status()  # fail loudly if something goes wrong

        new_file_path   = self.download_path / self.file_name

        with open(new_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)

        self.log.log_to_file(f"Downloaded Files to: {new_file_path}!", "DOWNLOAD", "INFO")

        return new_file_path

    def create_source(self,
            parent_source_code  : str,
            source_code         : str,
            source_name         : str,
            version             : str | None = None,
            note                : str | None = None
        ) -> int:

        parent_source   = self.read.find_source(parent_source_code)
        found_source    = self.read.find_source(source_code)
        source_id       = None

        if found_source == None:
            source_id = self.write.persist_source(
                source_type         = "DAT", # Dataset
                code                = source_code,
                name                = source_name,
                description         = self.description,
                version             = version,
                url                 = self.source_url,
                note                = note,
                parent_source       = parent_source,
                official_citation   = self.official_citation
            )
        else:
            source_id = found_source

        self.source_id = source_id

    def map_license(self, 
            license_code            : str,
            is_new_license          : bool             = False,
            new_license_attributes  : list[str] | None = None,
            new_description         : str       | None = None,
            new_license_name        : str       | None = None,
            new_license_link        : str       | None = None
        ):
        # If this is a new licence
        if is_new_license:
            # Create new licence and map to source
            licence_id = self.write.persist_licence(
                source_id   = self.source_id,
                code        = license_code,
                name        = new_license_name,
                version     = None,
                link        = new_license_link,
                summary     = new_description,
                valid_from  = None,
                valid_until = None,
                notes       = "CUSTOM TERMS OF USE"
            )

            self.write.map_all_licence_attributes(
                licence_id      = licence_id,
                attributes      = new_license_attributes
            )

            self.write.map_source_license(
                source_id       = self.source_id,
                licence_id      = licence_id
            )

        # If existing licence (e.g. CC BY)
        else: 
            # Map source to existing licence
            existing_licence = self.read.find_license(license_code)
            if existing_licence != None:
                self.write.map_source_license(
                    source_id       = self.source_id,
                    licence_id      = existing_licence
                )
            else:
                self.log.log_to_file(f"License code {license_code} not found in database. Cannot map license to source {self.source_id}.", "LICENSE MAPPING", "WARN")