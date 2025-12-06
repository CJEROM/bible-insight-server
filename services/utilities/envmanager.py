from pathlib import Path
import os
from dotenv import load_dotenv

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

DBL_USERNAME = os.getenv("DBL_USERNAME")
DBL_PASSWORD = os.getenv("DBL_PASSWORD")

class EnvManager:
    def __init__(self):
        pass

    def load_env(self):
        # Find the project root containing .env
        current = Path(__file__).resolve()
        for parent in current.parents:
            env_file = parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                break

