from pathlib import Path
import requests
import zipfile

class GeoIngestor():
    def __init__(self):
        # Download main Geo Data
        self.download_data(
            "https://github.com/openbibleinfo/Bible-Geocoding-Data/archive/refs/heads/main.zip",
            "downloads" ,
            "geodata",
            "thumbnails.zip"
        )

        # Download supplemental thumbnail images
        self.download_data(
            "https://a.openbible.info/geo/thumbnails.zip",
            "downloads" ,
            "geoimages",
            "thumbnails.zip"
        )

        # ancient_json = 
        # modern_json = 
        # geometry_json = 
        # image_json = 
        # source_json = 

    def download_data(self, url, base_folder, extract_folder, zip_file):
        base_path = Path(__file__).parents[2] / base_folder
        zip_path = base_path / zip_file
        extract_path = base_path / extract_folder
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        zip_path.write_bytes(response.content)

        # 4. Extract ZIP
        extract_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_path)

        # 5. Locate extracted repo folder (GitHub always nests it)
        # e.g. Bible-Geocoding-Data-main/
        repo_dir = next(extract_path.iterdir())

        print("ZIP saved at:      ", zip_path)
        print("Extracted to:     ", extract_path)
        print("Repo root folder: ", repo_dir)

        zip_path.unlink()  # delete zip after extraction
        return extract_path

    def ingest_jsonl(self, path):
        pass

if __name__ == "__main__":
    GeoIngestor()