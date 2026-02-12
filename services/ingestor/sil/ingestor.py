from manager.managerhandler import ManagerHandler

from database.boundary.sil_boundary import SILReadBoundary, SILWriteBoundary, SILDeleteBoundary

from ingestor.sil.iso6393_codes import ISO6393Codes
from ingestor.sil.iso6393_names import ISO6393Names
from ingestor.sil.iso6393_macrolanguages import ISO6393MacroLanguages
from ingestor.sil.iso6393_retirements import ISO6393Retirements

import requests

from zipfile import ZipFile
import os
from pathlib import Path
import shutil
from bs4 import BeautifulSoup

class SILIngestor:
    def __init__(self,
            manager: ManagerHandler | None = None
        ):
        self.manager        = manager or ManagerHandler()
        self.log            = self.manager.create_log_in_folder(["logs", "ingestor", "sil"], f"")
        self.db             = self.manager.get_db()

        self.log.set_logging_level(1)

        self.log.log_to_file(f"SIL Ingestion starting ...", "INGESTOR", "INFO")

        self.obj            = self.manager.get_obj().create_bucket(
            bucket_name     = "reference-data",
            is_versioned    = True,
            is_default      = True
        )

        self.read           = SILReadBoundary(self.db)
        self.write          = SILWriteBoundary(self.db)

        self.object_start   = "SIL-data"

        self.download_path  = Path(__file__).parents[2] / "downloads"
        os.makedirs(self.download_path, exist_ok=True)

        # Need playwright to visit so that the path will be the latest zip download file?
        self.source_url     = None

        self.source_id      = None

        self.get_latest_dowload_link()

        self.db.commit()

    def create_source(self):
        pass

    def map_license(self):
        # Maps licensing details to the files or at least the source for now
        pass

    def get_latest_dowload_link(self):
        DOWNLOAD_PAGE = "https://iso639-3.sil.org/code_tables/download_tables"

        html = requests.get(DOWNLOAD_PAGE)
        html.raise_for_status()

        soup = BeautifulSoup(html.text, "html.parser")
        link = soup.select_one('a[href*="iso-639-3_Code_Tables_"][href$=".zip"]')
        if not link:
            raise RuntimeError("Latest ISO 639-3 ZIP not found")
        
        final_link = link["href"]

        self.download(final_link)

    def download(self, link: str):
        self.source_url = link

        response = requests.get(link, stream=True)
        response.raise_for_status()  # fail loudly if something goes wrong

        filename = "sil_iso_data.zip"
        new_file_path = self.download_path / filename

        with open(new_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)

        self.log.log_to_file(f"Downloaded SIL Language Files to: {new_file_path}!", "INGESTOR", "INFO")

        self.create_source()
        self.unzip_folder(new_file_path)

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

            self.read_downloads(new_location)

            self.delete_files(new_location)

        # After unzipping delete the old zip file
        shutil.rmtree(zip_path, ignore_errors=True)
        self.delete_files(zip_path)

    def read_downloads(self, file_path: Path):
        # Goes through all the child files and loads them into the appropriate class to download accordingly
        files = {
            0: "iso-639-3.tab",
            1: "iso-639-3_Name_Index.tab",
            2: "iso-639-3_Retirements.tab",
            3: "iso-639-3-macrolanguages.tab"
        }

        # Get latest part of the folder to get date it was recently uploaded, this will be object start
        file_date = file_path.parts[-1].split("_")[-1]

        # Can use versionig instead to set or access these files, so that its easier

        for id, file in files.items():
            data_file_path = file_path / file

            match id:
                case 0:
                    # 7927 Entries
                    codes = ISO6393Codes(
                        main_manager    = self.manager,
                        log             = self.log,
                        source_id       = self.source_id,
                        file_path       = data_file_path
                    )

                    codes.upload_file(
                        object_name     = f"{self.object_start}/{file}",
                        file_path       = data_file_path,
                        content_type    = "text/tab-separated-values",
                        data_format     = "TSV",
                        version_note    = f"{file_date}"
                    )
                case 1:
                    # 8321 Entries
                    names = ISO6393Names(
                        main_manager    = self.manager,
                        log             = self.log,
                        source_id       = self.source_id,
                        file_path       = data_file_path
                    )

                    names.upload_file(
                        object_name     = f"{self.object_start}/{file}",
                        file_path       = data_file_path,
                        content_type    = "text/tab-separated-values",
                        data_format     = "TSV",
                        version_note    = f"{file_date}"
                    )
                case 2:
                    # 386 Entries
                    retirements = ISO6393Retirements(
                        main_manager    = self.manager,
                        log             = self.log,
                        source_id       = self.source_id,
                        file_path       = data_file_path
                    )

                    retirements.upload_file(
                        object_name     = f"{self.object_start}/{file}",
                        file_path       = data_file_path,
                        content_type    = "text/tab-separated-values",
                        data_format     = "TSV",
                        version_note    = f"{file_date}"
                    )
                case 3:
                    # 459 Entries
                    macroLanguages = ISO6393MacroLanguages(
                        main_manager    = self.manager,
                        log             = self.log,
                        source_id       = self.source_id,
                        file_path       = data_file_path
                    )

                    macroLanguages.upload_file(
                        object_name     = f"{self.object_start}/{file}",
                        file_path       = data_file_path,
                        content_type    = "text/tab-separated-values",
                        data_format     = "TSV",
                        version_note    = f"{file_date}"
                    )

    def delete_files(self, file_location: Path):
        if file_location.is_dir():
            shutil.rmtree(file_location, ignore_errors=True)  # delete folder + contents
        elif file_location.is_file():
            Path(file_location).unlink(missing_ok=True)

if __name__ == "__main__":
    SILIngestor()