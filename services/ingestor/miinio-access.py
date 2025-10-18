import zipfile
from minio import Minio
from pathlib import Path
import os

client = Minio(
    "localhost:9900",
    access_key="REDACTED_USERNAME",
    secret_key="REDACTED_PASSWORD",
    secure=False
)

# Download a file
response = client.get_object("test", "text-65eec8e0b60e656b-246069/release/USX_1/1CH.usx")
print(response)

# Upload a file
download_path = "C:/Users/CephJ/Documents/git/bible-insight-server/downloads"
zip_path = Path("downloads/en_kjv.zip")
extract_path = Path("tmp/en_kjv")
extract_path.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(zip_path, "r") as zf:
    zf.extractall(extract_path)

for file_path in extract_path.rglob("*.usx"):
    object_name = f"en_kjv/{file_path.name}"
    client.fput_object("bible-raw", object_name, str(file_path))