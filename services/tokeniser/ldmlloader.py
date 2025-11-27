from spacy.tokens import Doc
from minio import Minio
from bs4 import BeautifulSoup

class LDMLLoader:
    def __init__(self):
        pass

    def loadLanguageLDML(self):
        self.cur.execute("""
            SELECT file_path, bucket FROM bible.files WHERE id = (SELECT ldml_file FROM bible.translations WHERE id = %s);
        """, (self.translation_id,))
        ldml_file_object, ldml_file_bucket = self.cur.fetchone()
        ldml_content = self.stream_file(ldml_file_object, ldml_file_bucket)

        # ldml_file = Path(__file__).parents[2] / "logs" / "tests" / f"{self.translation_id}-ldml.xml"
        # with open(ldml_file, 'w', encoding='utf-8') as f:
        #     f.write(ldml_content)

        if ldml_content:
            ldml_content = ldml_content[1:]
            ldml_soup = BeautifulSoup(ldml_content, 'xml')
            # self.log_ingestion_activity(f"LDML File Returned: \n[{ldml_content}\n]", "LDML", "DEBUG")
        else: 
            # self.log_ingestion_activity(f"Can't parse LDML file for Translation [{self.translation_id}]", "LDML", "WARN")
            return

        # Extract punctuation tag from file
        punctuation_element = ldml_soup.find('exemplarCharacters', {'type': 'punctuation'})
    
        if punctuation_element:
            # Get the text content which contains the punctuation in brackets
            punctuation_text = punctuation_element.get_text()
            
            # Parse the bracket notation to extract individual characters
            punctuation_chars = self.parse_ldml_punctuation(punctuation_text)
            # self.log_ingestion_activity(f"No punctuation found in LDML file for Translation [{self.translation_id}]", "LDML", "DEBUG")
            return punctuation_chars
        
        # self.log_ingestion_activity(f"No punctuation found in LDML file for Translation [{self.translation_id}]", "LDML", "WARN")
        return []# list of punctuation marks
    
if __name__ == "__main__":
    pass