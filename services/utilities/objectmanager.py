from minio import Minio

from envmanager import EnvManager

class ObjectManager:
    def __init__(self):
        self.env = EnvManager()

        config = self.env.get_minio_config()

        # Passes Minio client connection on to the MinioUSXUpload class
        self.client = Minio(
            config["endpoint"],
            access_key=config["username"],
            secret_key=config["password"],
            secure=False
        )

    