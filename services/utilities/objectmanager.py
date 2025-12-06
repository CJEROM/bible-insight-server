from minio import Minio

from envmanager import EnvManager

class ObjectManager:
    def __init__(self, default_bucket):
        self.env = EnvManager()

        config = self.env.get_minio_config()

        # Passes Minio client connection on to the MinioUSXUpload class
        self.client = Minio(
            config["endpoint"],
            access_key=config["username"],
            secret_key=config["password"],
            secure=False
        )

        self.configured_buckets = [
            "bible-dbl-raw", 
            "open-bible-location-data", 
            "bible-nlp"
        ]

        self.bucket = None

    def set_default_bucket(self, default_bucket):
        if default_bucket not in self.configured_buckets:
            self.client.make_bucket(default_bucket)
            self.configured_buckets.append(default_bucket)

        self.bucket = default_bucket

    def get_configured_buckets(self):
        return self.configured_buckets

    def init_object_storage(self):
        for bucket in self.configured_buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

    def stream_file(self, object_name):
        # Get file
        response = None 
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name,
            )
            # Read the data as bytes, then decode as UTF-8
            data = response.read().decode("utf-8")
            return data
        finally:
            if response:
                response.close()
                response.release_conn()

    def upload_file(self, object_name, file_path, content_type, bucket=None):
        if bucket == None:
            bucket = self.bucket
        self.client.fput_object(bucket, object_name, str(file_path), content_type=content_type)
        info = self.client.stat_object(self.bucket, object_name)
        #region Object Return Example
            # Object(
            #     bucket_name='bible-dbl-raw', 
            #     object_name='text-65eec8e0b60e656b-246069/10/2JN.usx', 
            #     last_modified=datetime.datetime(2025, 10, 23, 16, 43, 21, tzinfo=datetime.timezone.utc), 
            #     etag='9b6bcda7e20ed8ffad0953711880191e', 
            #     size=3713, 
            #     metadata=HTTPHeaderDict(
            #         {'Accept-Ranges': 'bytes', 
            #          'Content-Length': '3713', 
            #          'Content-Type': 'application/xml', 
            #          'ETag': '"9b6bcda7e20ed8ffad0953711880191e"', 
            #          'Last-Modified': 'Thu, 23 Oct 2025 16:43:21 GMT', 
            #          'Server': 'MinIO', 
            #          'Strict-Transport-Security': 'max-age=31536000; includeSubDomains', 
            #          'Vary': 'Origin, Accept-Encoding', 
            #          'X-Amz-Id-2': 'dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8', 
            #          'X-Amz-Request-Id': '18712C730E5C7C9C', 
            #          'X-Content-Type-Options': 'nosniff', 
            #          'X-Ratelimit-Limit': '6778', 
            #          'X-Ratelimit-Remaining': '6778', 
            #          'X-Xss-Protection': '1; mode=block', 
            #          'Date': 'Thu, 23 Oct 2025 16:43:21 GMT'}), 
            #     version_id=None, 
            #     is_latest=None, 
            #     storage_class=None, 
            #     owner_id=None, 
            #     owner_name=None, 
            #     content_type='application/xml', 
            #     is_delete_marker=False, 
            #     tags=None, 
            #     is_dir=False
            # )
        #endregion

    