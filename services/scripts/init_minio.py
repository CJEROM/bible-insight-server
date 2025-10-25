from minio import Minio
import os
from dotenv import load_dotenv
from pathlib import Path

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
        break

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_USERNAME,
    secret_key=MINIO_PASSWORD,
    secure=False
)

# Consider creating buckets for audio, video and text so that it splits types of content?

# Makes buckets (not if they already exist) for each type of category of files I want to store
for bucket in ["bible-dbl-raw", "open-bible-location-data", "bible-nlp"]:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

# List buckets
print(client.list_buckets())