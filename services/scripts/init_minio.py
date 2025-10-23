from minio import Minio

client = Minio(
    "localhost:9900",
    access_key="REDACTED_USERNAME",
    secret_key="REDACTED_PASSWORD",
    secure=False
)

# Consider creating buckets for audio, video and text so that it splits types of content?

# Makes buckets (not if they already exist) for each type of category of files I want to store
for bucket in ["bible-dbl-raw", "open-bible-location-data", "bible-nlp"]:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

# List buckets
print(client.list_buckets())