import spacy
import json
from pathlib import Path

SMART_QUOTES = {
    "double": ['“', '”'],
    "single_open": ['‘'],
    "single_close": ['’']
}

SMART_QUOTES_PATTERN = (
    r"[\u201C\u201D]"      # Smart double “ ”
    r"|[\u2018]"           # Smart single opening ‘
    r"|[\u2019]"           # Smart single closing ’
)

PRONOUN_REFERENTS = {
    "he", "him", "his", "she", "her", "hers",
    "they", "them", "their", "you", "your",
    "we", "us", "our", "i", "me", "my"
}

class Labeller:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

        self.translation_title = "TEST"
        pass

    def create_ls_result(self, start, end, text_part, label):
        return {
            "id": f"{start}-{end}",
            "from_name": "label",
            "to_name": "text",
            "type": "labels",
            "value": {
                "start": start,
                "end": end,
                "text": text_part,
                "labels": [label]
            }
        }
    
    def is_apostrophe_in_token(self, doc, index):
        for token in doc:
            if token.idx <= index < token.idx + len(token.text):
                # Check token contains the ’ character and is longer than 1 char
                if "’" in token.text and len(token.text) > 1:
                    return True
                # Check whether the ’ character if by itself is tagged as punctuation POS
                if token.pos_ != "PUNCT":
                    return True
        return False

    def detect_smart_quotes(self, doc):
        results = []

        # Use regex to locate all smart quotes
        for match in re.finditer(SMART_QUOTES_PATTERN, self.text):
            start = match.start()
            end = match.end()
            char = match.group()

            # Smart double quotes → always include
            if char in SMART_QUOTES["double"]:
                results.append(self.create_ls_result(start, end, char, "Q"))

            # Smart single opening quote → always include
            elif char in SMART_QUOTES["single_open"]:
                results.append(self.create_ls_result(start, end, char, "Q"))

            # Smart single closing quote — only include if not apostrophe
            elif char in SMART_QUOTES["single_close"]:
                if not self.is_apostrophe_in_token(doc, start):
                    results.append(self.create_ls_result(start, end, char, "Q"))
                else: # if actually apostrophe
                    results.append(self.create_ls_result(start, end, char, "APOS"))

        return results
    
    def detect_tokens_to_label(self):
        doc = self.nlp(self.text)
        # Inherit results for smart quotes first, then add nouns and pronouns found on top
        results = self.detect_smart_quotes(doc)

        # Store all token related pos in for pre annotated labelling
        for token in doc:
            if token.pos_ == "PRON" and token.text.lower() in PRONOUN_REFERENTS: # Pronoun (that refers to people)
                start = token.idx
                end = start + len(token.text)
                results.append(self.create_ls_result(start, end, token.text, "PRON"))
            elif token.pos_ == "PROPN": # Proper Noun
                start = token.idx
                end = start + len(token.text)
                results.append(self.create_ls_result(start, end, token.text, ""))

        return results

    def createLabelStudioTask(self):
        # After receiving text start feeding into label studio project to create tasks for annotating this verse translation accordingly
        # Perhaps be selective only for instances where quotes have been found
        # Or doing a quick nlp if a pronoun or a noun has been found in this verse, then try and highlight for later, 
        # then using results see if we can make it smarter to recognise these before, perhaps loaded into 

        # This should write the details to a json file inside Minio or stored locally then sent over to minio to store for us
        # as we go through verses we append the information in there so that we can just import all labelling tasks for this translation
        # straight into label studio to create, instead of create labelling tasks one by one (which is uneccessary)

        # We can however programatically set up how we want to project and interfaces etc to be created through the api and then call the data import
        # or automate our very own machine learning backend to highlight specific things for us :)
        
        # create a json file in downloads folder like text-DBL-AGREEMENT-import

        # Then append verse to it with annotation aspects as part of the json in the file, then at the end for translation upload it to project.
        # Should create the file on minio-usx-upload (then should upload the file to minio on finish uploading, while also reading it to import into label studio)
        nlp_import_file = Path(__file__).parents[2] / "downloads" / f"{self.translation_title}.json"

        nlp_data = {
            "data": {
                "text": self.text,
                "verse_ref": self.verse_ref
            },
            "predictions": [
                {
                    "model_version": "one",
                    "score": 0.5,
                    "result": self.detect_tokens_to_label()
                }
            ]
        }

        with open(nlp_import_file, 'a', encoding="utf-8") as f:
            f.write("\n")
            json.dump(nlp_data, f)
            f.write(",")


        
if __name__ == "__main__":
