from pathlib import Path
import requests
import zipfile

BASE_DIR = Path(__file__).parents[2] / "downloads" 
BASE_DIR.mkdir(parents=True, exist_ok=True)

ZIP_PATH = BASE_DIR / "Bible-Geocoding-Data.zip"
EXTRACT_DIR = BASE_DIR 

class GeoIngestor():
    def __init__(self):
        self.download_geo_data()

    def download_geo_data(self):
        # 
        url = "https://github.com/openbibleinfo/Bible-Geocoding-Data/archive/refs/heads/main.zip"

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        ZIP_PATH.write_bytes(response.content)

        # 4. Extract ZIP
        EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(ZIP_PATH) as z:
            z.extractall(EXTRACT_DIR)

        # 5. Locate extracted repo folder (GitHub always nests it)
        # e.g. Bible-Geocoding-Data-main/
        repo_dir = next(EXTRACT_DIR.iterdir())

        print("ZIP saved at:      ", ZIP_PATH)
        print("Extracted to:     ", EXTRACT_DIR)
        print("Repo root folder: ", repo_dir)

        ZIP_PATH.unlink()  # delete zip after extraction

if __name__ == "__main__":
    GeoIngestor()
    pass