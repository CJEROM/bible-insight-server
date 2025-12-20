import requests
from pathlib import Path
import csv

SOURCE_URL = "https://dl.dropboxusercontent.com/scl/fi/pq1gsb2cf6n7hnp1l378d/Strongs-Numbers.xlsx?rlkey=puni8uqrdgcbikq1fkqg52576&e=1"

# Depening on the source I use, the way I preprocess the data for my project will change
class Strongs:
    def __init__(self):
        self.strongs_csv_path = Path(__file__).parents[2] / "archive" / "strongs.xlsx"
        if not self.strongs_csv_path.exists():
            self.download_strongs_csv()

    def download_strongs_csv(self):
        # In the future considering checking differences, and downloading based on that? if source requires
        url = "https://www.dropbox.com/scl/fi/pq1gsb2cf6n7hnp1l378d/Strongs-Numbers.xlsx?dl=1"

        self.strongs_csv_path.parent.mkdir(parents=True, exist_ok=True)

        r = requests.get(url, timeout=60)
        r.raise_for_status()

        self.strongs_csv_path.write_bytes(r.content)