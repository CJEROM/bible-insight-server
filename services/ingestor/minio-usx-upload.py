from zipfile import ZipFile
from minio import Minio
from pathlib import Path
import os

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

        # self.stream_file("bible-raw", "text-65eec8e0b60e656b-246069/release/USX_1/1CH.usx")
        match medium:
            case "text": # USX Files e.g. for deeper analysis
                # unzip first
                self.unzip_folder(self.process_location)
            case "video": # Videos e.g. for the deaf (sign language)
                pass
            case "audio": # Audio e.g. for the blind or preference
                pass

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

        # After unzipping delete the old zip file
        Path(zip_path).unlink(missing_ok=True)

    def validate_upload(self):
        # This is to check whether this translation is already in database, in which case don't upload
        #   Perhaps move this earlier in the process, or actually a secondary check is good.
        pass

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
    MinioUSXUpload(client, "text", r"C:/Users/CephJ/Documents/git/bible-insight-server/downloads/518ee924-6cf4-4622-b073-39b25ed06fad.zip", "bible_raw")