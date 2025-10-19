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
    def __init__(self, minio_client: Minio, medium):
        self.client = minio_client
        self.medium = medium # Audio | Video | Text (USX)

        # self.stream_file("bible-raw", "text-65eec8e0b60e656b-246069/release/USX_1/1CH.usx")
        match medium:
            case "text": # USX Files e.g. for deeper analysis
                pass
            case "video": # Videos e.g. for the deaf (sign language)
                pass
            case "audio": # Audio e.g. for the blind or preference
                pass

    def validate_upload(self):
        # This is to check whether this translation is already in database, in which case don't upload
        #   Perhaps move this earlier in the process, or actually a secondary check is good.
        pass

    # Make use and amend below function, to feed in files for processing (e.g. Book Classes)
    def stream_file(self, bucket, file_path):
        # Download a file
        response = self.client.get_object(bucket, file_path)
        print(response)

    def unzip_folder(self, zip_path):
        return

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