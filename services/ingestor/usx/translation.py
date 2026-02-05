from zipfile import ZipFile
from pathlib import Path
import shutil
import traceback

from ingestor.usx.files.metadata import Metadata
from database.boundary.usx_boundary import USXReadBoundary, USXWriteBoundary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler

class Translation:
    def __init__(self, manager: "ManagerHandler", medium, process_location, source_url, translation_id, dbl_id, agreement_id):
        self.manager = manager
        self.env = manager.get_env()
        self.obj = manager.get_obj()
        self.db = manager.get_db()
        self.label = manager.get_label()

        self.medium = medium # Audio | Video | Text (USX)
        self.process_location = process_location
        self.translation_id = translation_id
        self.dbl_id = dbl_id
        self.agreement_id = agreement_id

        self.revision = None

        print("✅ Starting Upload ...")
        
        self.translation_title = f"{self.medium}-{self.dbl_id}-{self.agreement_id}"

        self.translation_name = None
        self.bible_structure_info = None

        self.style_dict = {}

        self.labelproject = None

        # Initialise logfile
        self.log = self.manager.create_log_in_folder(["logs", "ingestor"], f"{self.translation_id}-{self.translation_title}")
        self.log.set_logging_level(2)

        self.log.log_to_file(f"TRANSLATION: [{self.dbl_id}-{self.agreement_id}] with ID [{self.translation_id}]", "TRANSLATION", "INFO")

        self.write = USXWriteBoundary(self.db)
        self.read = USXReadBoundary(self.db)

        self.source_id = self.get_source(source_url)
        self.metadata = None

        try:
            match medium:
                case "text": # USX Files e.g. for deeper analysis
                    # unzip first
                    self.unzip_folder(self.process_location)
                case "video": # Videos e.g. for the deaf (sign language)
                    # self.check_files(self.process_location)
                    pass
                case "audio": # Audio e.g. for the blind or preference
                    self.check_files(self.process_location)
        except Exception as e:
            error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            self.log.log_to_file(error_message, "TRANSLATION", "ERROR")
            print(f"❌ Failed to Upload Translation {dbl_id}-{agreement_id} with error {e}")

        self.log.log_to_file(f"Completed Translation [{self.translation_name}] Ingestion!", "TRANSLATION", "INFO")

        # Create Label Studio Project for this specific translation of the bible
        self.labelproject = self.label.create_new_translation_project(self.translation_id, self.translation_name, self.translation_title)
        
    def get_metadata(self):
        return self.metadata
    
    def get_translation_id(self):
        return self.translation_id
    
    def get_dbl_id(self):
        return self.dbl_id
    
    def get_agreement_id(self):
        return self.agreement_id
    
    def get_translation_id(self):
        return self.translation_id
    
    def get_translation_project_id(self):
        return self.labelproject
    
    def get_translation_title(self):
        return self.translation_title
    
    def get_language_id(self):
        return self.language_id
    
    def get_style_dict(self):
        return self.style_dict

    def get_source(self, source_url):
        # Find if url is already stored source in database
        source_id = self.db.fetch_clean_one("""SELECT id FROM audit.sources WHERE url = %s;""", (source_url,))
        if source_id != None:
            return source_id
        # Find if source already in the database
        source_id = self.read.find_source(code='DBL')
        # source_id = self.read.

        # if it is return, if it isn't then create it
        
        
        # If not create new and return it
        new_source_id = self.write.persist_source(
            url=source_url
        )

        self.log.log_to_file(f"Created New Source [ID: {new_source_id}] [URL: {source_url}]", "TRANSLATION", "INFO")
        return new_source_id

    def unzip_folder(self, zip_path):
        # This will unzip the zip folder, and then delete the original and replace process location with new path name
        downloads_location = Path(zip_path).parent

        with ZipFile(zip_path, 'r') as zip:
            # list all file paths in the ZIP
            all_files = zip.namelist()

            # find the top-level folder (first part before '/')
            top_levels = {Path(f).parts[0] for f in all_files if '/' in f}
            top_folder = next(iter(top_levels)) if top_levels else None

            # extract everything
            zip.extractall(downloads_location)

            # Saves the new location for the usx files to be ran in next part of pipeline
            new_location = downloads_location / top_folder
            self.log.log_to_file(f"Unzipping [{len(all_files)}] files from {zip_path} in {new_location}", "TRANSLATION", "INFO")

            # Start Ingestion Pipeline for all files
            self.metadata = Metadata(self.translation_id, new_location)

            # Clean up files
            self.delete_files(new_location)

        # After unzipping delete the old zip file
        shutil.rmtree(zip_path, ignore_errors=True)
        self.delete_files(zip_path)
    
    def delete_files(self, file_location):
        if file_location.is_dir():
            shutil.rmtree(file_location, ignore_errors=True)  # delete folder + contents
        elif file_location.is_file():
            Path(file_location).unlink(missing_ok=True)