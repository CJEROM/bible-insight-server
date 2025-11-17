import spacy

# Decided I need to better tokenise so first will load all verses and then update the data for them later, I want tokens afterall in my database.

NLP_MAPPING = {
    "eng": "en",                # ENGLISH
    "Greek": "el",              # Greek
    "grc": "grc",               # ANCIENT GREEK
    "hbo": "he",                # HEBREW
    "heb": "he"                 # HEBREW
}

class Tokenisation:
    def __init__(self, verse_occurence, translation_id, language):
        self.verse_occurence = verse_occurence
        self.translation_id = translation_id
        self.language_id, self.language_iso = language

        self.nlp = None

        spacy_module = NLP_MAPPING.get(self.language_iso)

if __name__ == "__main__":
    pass