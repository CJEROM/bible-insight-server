import requests
from pathlib import Path
import csv

SOURCE_URL = "https://dl.dropboxusercontent.com/scl/fi/pq1gsb2cf6n7hnp1l378d/Strongs-Numbers.xlsx?rlkey=puni8uqrdgcbikq1fkqg52576&e=1"

# Depening on the source I use, the way I preprocess the data for my project will change
class Strongs:
    def __init__(self):
        self.strongs_csv_path = Path(__file__).parents[2] / "downloads" / "strongs.xlsx"
        if not self.strongs_csv_path.exists():
            self.download_strongs_csv()

    def download_strongs_csv(self):
        # In the future considering checking differences, and downloading based on that? if source requires
        url = SOURCE_URL

        self.strongs_csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        with requests.get(url, stream=True, allow_redirects=True, timeout=60) as r:
            r.raise_for_status()
            with open(self.strongs_csv_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print("Downloaded CSV file")

if __name__ == "__main__":
    Strongs()