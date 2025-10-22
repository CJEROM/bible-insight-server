from zipfile import ZipFile
from minio import Minio
from pathlib import Path
import os
from bs4 import BeautifulSoup
import psycopg2

# Passes Minio client connection on to the class
client = Minio(
    "localhost:9900",
    access_key="REDACTED_USERNAME",
    secret_key="REDACTED_PASSWORD",
    secure=False
)

class MinioUSXUpload:
    def __init__(self, minio_client: Minio, medium, process_location, bucket):
        self.client = minio_client
        self.medium = medium # Audio | Video | Text (USX)
        self.process_location = process_location
        self.bucket = bucket # The Minio bucket to create the files in.

        # Adds a database connection
        conn = psycopg2.connect(
            host="REDACTED_IP",
            port=5444,
            dbname="postgres",
            user="postgres",
            password="REDACTED_PASSWORD"
        )

        self.cur = conn.cursor()

        # self.stream_file("bible-raw", "text-65eec8e0b60e656b-246069/release/USX_1/1CH.usx")
        match medium:
            case "text": # USX Files e.g. for deeper analysis
                # unzip first
                self.unzip_folder(self.process_location)
            case "video": # Videos e.g. for the deaf (sign language)
                self.upload_files(self.process_location)
            case "audio": # Audio e.g. for the blind or preference
                self.upload_files(self.process_location)

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
            print(new_location)
            self.upload_files(new_location)

        # After unzipping delete the old zip file
        # Path(zip_path).unlink(missing_ok=True)

    def upload_files(self, file_location):
        top_folder = str(file_location).split("\\")[-1]
        # Validate bible upload (is already)
        valid = self.validate_upload(top_folder)
        if valid == True:
            # Don't continue if already in database
            Path(file_location).unlink(missing_ok=True) # Delete extracted folder
            return 

        # Find metadata file
        metadata_file_path = Path(file_location) / "metadata.xml"
        metadata_file_content = ""
        with open(metadata_file_path, 'r') as file:
            metadata_file_content = file.read()

        revision = 0

        license_file_path = Path(file_location) / "license.xml"


        object_name = f"{top_folder}/{revision}/{file}"
        object_name = f"{top_folder}/{revision}/USX/file.xml"
        self.client.fput_object("bible-dbl-raw", object_name, str(metadata_file_path))

        # Get data of an object of version-ID.
        response = None 
        try:
            response = self.client.get_object(
                bucket_name="bible-dbl-raw",
                object_name=object_name,
            )
            print(str(response.data))
        finally:
            if response:
                response.close()
                response.release_conn()
        

        # Selectively upload the files I want in the format I want (from metadata)

        # Update database entries with files or rely on books class to do so.

    def validate_upload(self, folder):
        # This is to check whether this translation is already in database, in which case don't upload
        #   Perhaps move this earlier in the process, or actually a secondary check is good.
        medium, dbl, agreement = folder.split("-")

        # Query database to see whether this dbl_id and agreement exist in the database with corresponding data or not (Through Translations table)
        self.cur.execute("""
            SELECT id FROM bible.Translations WHERE dbl_id = %s AND agreement_id = %s;
        """, (dbl, agreement))
        
        # If this translation not been loaded in database
        if self.cur.fetchone() == None:
            return False # Not Valid => Therefore create new
        
        return True # Valid => Therefore skip to next upload file

    # Make use and amend below function, to feed in files for processing (e.g. Book Classes)
    def stream_file(self, bucket, file_path):
        # Download a file
        response = self.client.get_object(bucket, file_path)
        print(response)

    def upload_zip_folder(self, original_location, minio_location):
        base = Path(__file__).parent.parent.parent
        downloads_path = base / "downloads"

        # Upload a file
        download_path = "C:/Users/CephJ/Documents/git/bible-insight-server/downloads"
        zip_path = Path(original_location)
        extract_path = Path("tmp/en_kjv")
        extract_path.mkdir(parents=True, exist_ok=True)

        with ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_path)

        for file_path in extract_path.rglob("*.usx"):
            object_name = f"en_kjv/{file_path.name}"
            self.client.fput_object("bible-raw", object_name, str(file_path))

    def upload_folder(self, original_location, minio_location):
        return
    
if __name__ == "__main__":
    MinioUSXUpload(client, "text", r"C:/Users/CephJ/Documents/git/bible-insight-server/downloads/c1c304e5-9e97-49bb-8637-6f5137a69d71.zip", "bible_raw")