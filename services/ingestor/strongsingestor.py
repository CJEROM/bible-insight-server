import requests
from pathlib import Path
import pandas

from manager.managerhandler import ManagerHandler

SOURCE_URL = "https://dl.dropboxusercontent.com/scl/fi/pq1gsb2cf6n7hnp1l378d/Strongs-Numbers.xlsx?rlkey=puni8uqrdgcbikq1fkqg52576&e=1"

# Depening on the source I use, the way I preprocess the data for my project will change
class StrongsIngestor:
    def __init__(self, manager: ManagerHandler):
        self.manager = manager
        self.log = manager.create_log_in_folder()
        self.db = manager.get_db()
        self.obj = manager.get_obj()

        self.strongs_csv_path = Path(__file__).parents[2] / "downloads" / "strongs.xlsx"
        if not self.strongs_csv_path.exists():
            self.download_strongs_csv()

        self.pre_process_xlsx()
        self.process_hebrew_sheet()
        self.process_greek_sheet()

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

    def pre_process_xlsx(self):
        pass
        xls = pandas.ExcelFile(self.strongs_csv_path)
        print(xls.sheet_names) # Allows for reading .xlsx files
        # Sheets of interst: ['Hebrew', 'Greek', 'letters', 'BibleBook Numbers']
        # Next Steps
        # Remove specific mentions of english word occurence from Gloss (our system will handle that for translations that support this)

        # No need to do occurences

        # A need to see letter occurence

    def get_sheet(self, sheet_name: str, columns:list):
        sheet = pandas.read_excel(
            self.strongs_csv_path,
            sheet_name=sheet_name,
            engine="openpyxl",
            usecols=columns,
            dtype=str
        )
        # Clean Up column names
        sheet.columns = (
            sheet.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(".", "_")
            .str.replace("#", "number")
        )
        print(sheet.columns)
        return sheet

    def process_hebrew_sheet(self):
        sheet = self.get_sheet(
            "Hebrew",
            ['#', 'Word', 'Gloss', 'Root', 'Pic Root',
            '1st Root Strongs', '1st Root Hebrew', '2nd Root Strongs',
            '2nd Root Hebrew2', '3rd Root Strongs', '3rd Root Hebrew',
            'Part of Speech', 'cl.Gk.eqt.']
        )
        language_id = self.db.fetch_clean_one("""
            SELECT id FROM bible.languages WHERE name LIKE 'Hebrew%'
        """)
        for row in sheet.itertuples(index=False):
            strongs_code = f"H{row.number}"
            print(strongs_code)

    def process_greek_sheet(self):
        sheet = self.get_sheet(
            "Greek",
            ['#', 'Word', 'Gloss', 'Root',
            'Occ in other words', 'prep1', 'prep2', 'R1', 'R1-Gk', 'R2', 'R2-Gk',
            'R3', 'R3-Gk', 'Part of Speech', 'cl.Heb.eqt.']
        )
        language_id = self.db.fetch_clean_one("""
            SELECT id FROM bible.languages WHERE name LIKE 'Greek%'
        """)
        for row in sheet.itertuples(index=False):
            # print(row.word)
            pass
        pass

    def create_strongs(self):
        # Write New Strongs entry to the database
        pass

    def create_strongs_relation(self):
        # Write New Strongs Relation to the database e.g. from Root strongs etc.
        pass

if __name__ == "__main__":
    StrongsIngestor()