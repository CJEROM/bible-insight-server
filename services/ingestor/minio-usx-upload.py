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
    def __init__(self, minio_client: Minio):
        self.client = minio_client

        self.stream_file("bible-raw", "text-65eec8e0b60e656b-246069/release/USX_1/1CH.usx")

    def stream_file(self, bucket, file_path):
        # Download a file
        response = self.client.get_object(bucket, file_path)
        print(response)

    def unzip_folder(self, zip_path):
        return

    def upload_zip_folder(self, original_location, minio_location):

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