import requests
from pathlib import Path
import csv

SOURCE_URL = "https://dl.dropboxusercontent.com/scl/fi/pq1gsb2cf6n7hnp1l378d/Strongs-Numbers.xlsx?rlkey=puni8uqrdgcbikq1fkqg52576&e=1"

class Strongs:
    def __init__(self):
        self.strongs_csv_path = self.download_strongs_csv()

    def download_strongs_csv(self):
        url = "https://www.dropbox.com/scl/fi/pq1gsb2cf6n7hnp1l378d/Strongs-Numbers.xlsx?dl=1"
        strongs_csv = Path(__file__).parents[2] / "archive"

        strongs_csv.parent.mkdir(parents=True, exist_ok=True)

        r = requests.get(url, timeout=60)
        r.raise_for_status()

        strongs_csv.write_bytes(r.content)
        return strongs_csv