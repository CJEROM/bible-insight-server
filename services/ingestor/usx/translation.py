from zipfile import ZipFile
from pathlib import Path
import shutil
import traceback

from ingestor.usx.files.metadata import Metadata
from database.boundary.usx_boundary import USXReadBoundary, USXWriteBoundary, USXDeleteBoundary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from ingestor.usx.files.agreements import DBLAgreement
    from manager.logmanager import LogManager

class Translation:
    def __init__(self, manager: "ManagerHandler", medium: str, process_location: Path, source_url: str, dbl_id: str, agreement: "DBLAgreement", log: "LogManager"):
        self.manager            = manager
        self.db                 = manager.get_db()
        self.log                = log

        self.write              = USXWriteBoundary(self.db)
        self.read               = USXReadBoundary(self.db)
        self.delete             = USXDeleteBoundary(self.db)

        self.dbl_id             = dbl_id

        self.medium             = medium # Audio | Video | Text (USX)
        self.process_location   = process_location
       
        self.dbl_agreement      = agreement
        self.agreement_id       = agreement.get_id()

        self.source_url         = source_url

        print("✅ Starting Upload ...")

        self.labelproject       = None

        self.log.log_to_file(f"TRANSLATION: [{self.dbl_id}-{self.agreement_id}]", "TRANSLATION", "INFO")

        self.metadata           = None

        self.ingest()
        # Can Choose to run outside of Try block for harsher fails (more error details for now?)
        # self.choose_medium() 
        
    def ingest(self):
        try:
            self.choose_medium()
        except Exception as e:
            print(e)
            error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            self.log.log_to_file(error_message, "TRANSLATION", "ERROR")
            print(f"❌ Failed to Upload Translation {self.dbl_id}-{self.agreement_id} with error {e}")
            # ON FAIL -> DELETE ALL TRANSLATION DATA (Clears away partial data in the DB)
            if self.metadata.translation_id != None:
                self.delete.delete_translation(self.metadata.translation_id)

        self.log.log_to_file(f"Completed Translation Ingestion!", "TRANSLATION", "INFO")

    def choose_medium(self):
        match self.medium:
            case "text": # USX Files e.g. for deeper analysis
                # unzip first
                self.unzip_folder(self.process_location)
            case "video": # Videos e.g. for the deaf (sign language)
                # self.check_files(self.process_location)
                pass
            case "audio": # Audio e.g. for the blind or preference
                # Start Ingestion Pipeline for all files
                self.process_metadata(self.process_location)

    def get_metadata(self):
        return self.metadata
    
    def get_dbl_id(self):
        return self.dbl_id
    
    def process_metadata(self, file_location: Path):
        self.dbl_agreement.set_translation(self, file_location)

        # Start Ingestion Pipeline for all files
        self.metadata = Metadata(
            this_translation        = self,
            translation_file_path   = file_location, 
            log                     = self.log, 
            source_url              = self.source_url,
            main_manager            = self.manager,
            agreement               = self.dbl_agreement
        )

        self.dbl_agreement.link_agreement_revision(self.metadata.get_metadata("revision"))

        # Clean up files - Only after successful run, don't automatically delete all files
        self.delete_files(file_location)

    def unzip_folder(self, zip_path):
        # This will unzip the zip folder, and then delete the original and replace process location with new path name
        downloads_location = Path(zip_path).parent

        with ZipFile(zip_path, 'r') as zip:
            # list all file paths in the ZIP
            all_files   = zip.namelist()

            # find the top-level folder (first part before '/')
            top_levels  = {Path(f).parts[0] for f in all_files if '/' in f}
            top_folder  = next(iter(top_levels)) if top_levels else None

            # extract everything
            zip.extractall(downloads_location)

            # Saves the new location for the usx files to be ran in next part of pipeline
            new_location = downloads_location / top_folder
            self.log.log_to_file(f"Unzipping [{len(all_files)}] files from {zip_path} in {new_location}", "TRANSLATION", "INFO")

            self.process_metadata(new_location)

        # After unzipping delete the old zip file
        shutil.rmtree(zip_path, ignore_errors=True)
        self.delete_files(zip_path)
    
    def delete_files(self, file_location: Path):
        if file_location.is_dir():
            shutil.rmtree(file_location, ignore_errors=True)  # delete folder + contents
        elif file_location.is_file():
            Path(file_location).unlink(missing_ok=True)