from pathlib import Path
import os
from dotenv import load_dotenv

class EnvManager:
    def __init__(self):
        self._load_env()

    def _load_env(self):
        # Find the project root containing .env
        current = Path(__file__).resolve()
        for parent in current.parents:
            env_file = parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                break

    # Generic Getter for environment variables
    def get(self, key: str, default=None, required=False):
        value = os.getenv(key, default)
        if required and value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
        
    # ======================== Group Getters ========================
    def get_postgres_config(self) -> dict:
        return {
            "username": self.get("POSTGRES_USERNAME", required=True),
            "password": self.get("POSTGRES_PASSWORD", required=True),
            "database": self.get("POSTGRES_DB", required=True),
            "host": self.get("POSTGRES_HOST", default="localhost"),
            "port": int(self.get("POSTGRES_PORT", default="5432")),
        }

    def get_minio_config(self) -> dict:
        return {
            "endpoint": self.get("MINIO_ENDPOINT", required=True),
            "username": self.get("MINIO_USERNAME", required=True),
            "password": self.get("MINIO_PASSWORD", required=True),
        }

    def get_dbl_credentials(self) -> dict:
        return {
            "username": self.get("DBL_USERNAME", required=True),
            "password": self.get("DBL_PASSWORD", required=True),
        }
    
    def get_label_studio(self) -> dict:
        return {
            "endpoint": self.get("LABEL_STUDIO_URL", required=True),
            "username": self.get("LABEL_STUDIO_USERNAME", required=True),
            "password": self.get("LABEL_STUDIO_PASSWORD", required=True),
            "api_token": self.get("LABEL_STUDIO_API_TOKEN", required=True),
        }