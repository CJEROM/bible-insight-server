import requests
from pathlib import Path
import pandas

from manager.managerhandler import ManagerHandler

SOURCE_URL = "https://dl.dropboxusercontent.com/scl/fi/pq1gsb2cf6n7hnp1l378d/Strongs-Numbers.xlsx?rlkey=puni8uqrdgcbikq1fkqg52576&e=1"
# See: https://www.ancient-hebrew.org/ahlb/aleph.html

# Depening on the source I use, the way I preprocess the data for my project will change
class StrongsIngestor:
    SQL = {
        "create_strongs": """
            INSERT INTO bible.lexemes (source, strongs_code, language_id, lemma, raw_pos, transliteration, pronunciation, raw_gloss) VALUES %s
        """,
        "create_strongs_relation": """
            INSERT INTO bible.lexeme_relations (from_lexeme, to_lexeme, relation_type) VALUES %s
        """,
    }
    def __init__(self, manager: ManagerHandler):
        self.manager = manager
        self.log = manager.create_log_in_folder(["logs", "strongsingestor"], "strongs")
        self.db = manager.get_db()
        self.obj = manager.get_obj()

        self.strongs_csv_path = Path(__file__).parents[2] / "downloads" / "strongs.xlsx"
        if not self.strongs_csv_path.exists():
            self.download_strongs_csv()

        self.lexeme_mapping = {}
        self.lexeme_relation_mapping = {}
        self.strongs_data = []
        self.strongs_relations = []
        self.lexeme_id = 1

        self.pre_process_xlsx()
        self.process_hebrew_sheet()
        self.process_greek_sheet()

        self.bulk_export_strongs()

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

        self.log.log_to_file(f"Downloaded Strongs Concordance Data with XLSX file", "STRONGS_INGESTOR", "DEBUG")

    def pre_process_xlsx(self):
        xls = pandas.ExcelFile(self.strongs_csv_path)
        print(xls.sheet_names) # Allows for reading .xlsx files

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

    def extract_strongs(self, sheet, language_id, language):
        for row in sheet.itertuples(index=False):
            this_lexeme = [None] * 8
            this_lexeme[0] = "strongs"
            strongs_code = f"{language}{row.number}"
            this_lexeme[1] = strongs_code
            this_lexeme[2] = language_id

            if row.root != "" and row.root != "NaN":
                this_lexeme[3] = row.root

            this_lexeme[4] = row.part_of_speech

            raw_gloss = ""

            if type(row.gloss) == str:
                for i, line in enumerate(row.gloss.splitlines()):
                    temp_relations = []
                    if i == 0:  
                        split_bracket = line.split("(")

                        if len(split_bracket) < 2:
                            continue

                        transliteration = split_bracket[0].strip()
                        this_lexeme[5] = transliteration

                        pronunciation = split_bracket[1].split(")")[0]
                        this_lexeme[6] = pronunciation
                        
                        raw_gloss += f"{line}\n"

                    elif not line.startswith("KJV") and not line.startswith("Root") and not line.startswith("Compare"):
                        raw_gloss += f"{line}\n"

                    elif line.startswith("Root(s): "):
                        all_roots_raw = line[8:].split(",")
                        for root in all_roots_raw:
                            if root.strip() == '': continue
                            temp_relations.append((root.strip(), "root"))
                            
                    elif line.startswith("Compare: "):
                        all_compares_raw = line[8:].split(",")
                        for compare in all_compares_raw:
                            compare_str = compare.strip()
                            if compare_str == '': continue
                            if (compare_str.startswith("H") or compare_str.startswith("G")) and compare_str[1:].isdigit():
                                temp_relations.append((compare_str, "compare"))
                    
                    if len(temp_relations) > 0:
                        self.lexeme_relation_mapping[self.lexeme_id] = temp_relations
            
            this_lexeme[7] = raw_gloss
            self.strongs_data.append(tuple(this_lexeme))
            self.lexeme_mapping[strongs_code] = self.lexeme_id
            # print(row.word)
            self.lexeme_id+=1 # Increment every row

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
        self.extract_strongs(sheet, language_id, "H")

    def process_greek_sheet(self):
        sheet = self.get_sheet(
            "Greek",
            ['#', 'Word', 'Gloss', 'Root',
            'prep1', 'prep2', 'R1', 'R1-Gk', 'R2', 'R2-Gk',
            'R3', 'R3-Gk', 'Part of Speech', 'cl.Heb.eqt.']
        )
        language_id = self.db.fetch_clean_one("""
            SELECT id FROM bible.languages WHERE name LIKE 'Greek%'
        """)
        self.extract_strongs(sheet, language_id, "G")

    def bulk_export_strongs(self):
        self.db.bulk_insert(self.SQL.get("create_strongs"), self.strongs_data)
        self.db.commit()

        for from_lexeme_id, to_strongs_relations in self.lexeme_relation_mapping.items():
            from_strongs = next((k for k, v in self.lexeme_mapping.items() if v == from_lexeme_id), None)

            for to_strong, relation_type in to_strongs_relations:

                to_lexeme_id = self.lexeme_mapping.get(to_strong)
                if to_lexeme_id == None:
                    self.log.log_to_file(f"{to_strong} doesn't exist", "STRONGS_INGESTOR", "WARN")
                    continue

                self.log.log_to_file(f"{from_strongs}:{from_lexeme_id} <= {relation_type} => {to_strong}:{to_lexeme_id}", "STRONGS_INGESTOR", "DEBUG")
                
                new_relation = (from_lexeme_id, to_lexeme_id, relation_type)

                # Remove duplicates
                if new_relation in self.strongs_relations:
                    print(f"=======> {new_relation}")
                    continue

                self.strongs_relations.append(new_relation)

        self.db.bulk_insert(self.SQL.get("create_strongs_relation"), self.strongs_relations)
        self.db.commit()

        self.log.log_to_file(f"Completed Strongs Data Import", "STRONGS_INGESTOR", "DEBUG")

if __name__ == "__main__":
    StrongsIngestor(ManagerHandler())