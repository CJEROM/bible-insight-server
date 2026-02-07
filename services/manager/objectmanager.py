from minio import Minio
from minio.commonconfig import ENABLED
from minio.versioningconfig import VersioningConfig

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.envmanager import EnvManager

from database.boundary.base_boundary import ReadBoundary, WriteBoundary

class ObjectManager:
    def __init__(self, 
            this_manager    : "ManagerHandler"  = None, 
            default_bucket  : str               = None
        ):
        self.this_manager   = this_manager
        self.env            = None
        if this_manager == None:
            self.env        = EnvManager()
        else:
            self.env        = self.this_manager.get_env()

        config              = self.env.get_minio_config()
        self.db             = self.this_manager.get_db()

        self.read           = ReadBoundary(self.db)
        self.write          = WriteBoundary(self.db)

        # Passes Minio client connection on to the MinioUSXUpload class
        self.client = Minio(
            endpoint        = config["endpoint"],
            access_key      = config["username"],
            secret_key      = config["password"],
            secure          = False
        )

        self.bucket             = None
        self.configured_buckets = []

        self.create_bucket(
            bucket_name     = "bible-dbl-raw",
            is_versioned    = True
        )
        self.create_bucket(
            bucket_name     = "open-bible-location-data",
        )
        self.create_bucket(
            bucket_name     = "bible-nlp"
        )
        
        # Allow for setting default bucket
        self.create_bucket(
            bucket_name     = default_bucket,
            is_default      = True
        )
    
    def create_bucket(self, 
            bucket_name     : str, 
            is_versioned    : bool = False,
            is_default      : bool = False
        ):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

        cfg = self.client.get_bucket_versioning(bucket_name)
        if is_versioned and cfg.status != ENABLED:
            self.client.set_bucket_versioning(
                bucket_name,
                VersioningConfig(ENABLED)
            )

        if bucket_name not in self.configured_buckets:
            self.configured_buckets.append(bucket_name)

        if is_default:
            self.bucket = bucket_name

    def stream_file(self,
        object_name : str,
        version_id  : str | None = None,
        bucket      : str | None = None,
        decode      : bool = True
    ):
        bucket = bucket or self.bucket

        response = None
        try:
            response = self.client.get_object(
                bucket_name=bucket,
                object_name=object_name,
                version_id=version_id
            )

            if decode:
                return response.read().decode("utf-8")
            return response.read()

        finally:
            if response:
                response.close()
                response.release_conn()

    def stream_file_from_file_id(self, file_id):
        file_object_name, file_bucket, version_id = self.read.read_file(file_id)

        return self.stream_file(
            object_name     = file_object_name, 
            bucket          = file_bucket,
            version_id      = version_id
        )

    # ADD METHOD TO CHEck FILE EXISTS ALREADY? IF SO UPDATE IT, DO DB WRITING HERE? INSTEAD OF IN INGESTOR CODE? OR PROCESESS THAT THERE INSTEAD

    # EDIT METHOD: Needs to also include Object versioning
    def upload_file(self, 
            object_name : str, 
            file_path   : str, 
            content_type: str, 
            bucket      : str = None
        ):
        if bucket == None:
            bucket  = self.bucket
        self.client.fput_object(bucket, object_name, str(file_path), content_type=content_type)
        info        = self.client.stat_object(self.bucket, object_name)
        return info
    
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