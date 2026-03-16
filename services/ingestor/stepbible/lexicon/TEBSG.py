# Lexicons/TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler

from ingestor.stepbible.lexicon.lexicon_base import LexiconBase

CODES = {
    "A"      : {
        "Function": "Adjective",
    },
    "A--C"   : {
        "Function": "Adjective",
        "Extra": "Comparative"
    },
    "A--L"   : {
        "Function": "Adjective",
        "Name type": "Location"
    },
    "A--LG"  : {
        "Function": "Adjective",
        "Name type": "Location Gentilic"
    },
    "A--PG"  : {
        "Function": "Adjective",
        "Name type": "Person Gentilic"
    },
    "A--S"   : {
        "Function": "Adjective",
        "Extra": "Superlative"
    },
    "A-F"    : {
        "Function": "Adjective",
        "Gender": "Feminine"
    },
    "A-M"    : {
        "Function": "Adjective",
        "Gender": "Masculine"
    },
    "C"      : {
        "Function": "Reciprocal Pronoun"
    },
    "D"      : {
        "Function": "Demonstrative pronoun"
    },
    "F-1"    : {
        "Function": "Reflexive Pronoun",
        "Person": "1st"
    },
    "F-2"    : {
        "Function": "Reflexive Pronoun",
        "Person": "2nd"
    },
    "F-3"    : {
        "Function": "Reflexive Pronoun",
        "Person": "3rd"
    },
    "I"      : {
        "Form": "Interrogative"
    },
    "K"      : {
        "Function": "Correlative"
    },
    "N"      : {
        "Function": "Noun"
    },
    "N--L"   : {
        "Function": "Noun",
        "Name type" : "Location"
    },
    "N--LG"  : {
        "Function": "Noun",
        "Name type": "Location Gentilic"
    },
    "N--PG"  : {
        "Function": "Noun",
        "Name type": "Person Gentilic"
    },
    "N--T"   : {
        "Function": "Noun",
        "Name type": "Title"
    },
    "N-F"    : {
        "Function": "Noun",
        "Gender": "Feminine"
    },
    "N-F-L"  : {
        "Function": "Noun",
        "Gender": "Feminine",
        "Name type" : "Location"
    },
    "N-F-LG" : {
        "Function": "Noun",
        "Gender": "Feminine",
        "Name type" : "Location Gentilic"
    },
    "N-F-P"  : {
        "Function": "Noun",
        "Gender": "Feminine",
        "Name type" : "Person"
    },
    "N-M"    : {
        "Function": "Noun",
        "Gender": "Masculine",
    },
    "N-M-L"  : {
        "Function": "Noun",
        "Gender": "Masculine",
    },
    "N-M-LG" : {
        "Function": "Noun",
        "Gender": "Masculine",
    },
    "N-M-P"  : {
        "Function": "Noun",
        "Gender": "Masculine",
    },
    "N-M-T"  : {
        "Function": "Noun",
        "Gender": "Masculine",
        "Name type": "Title"
    },
    "N-N"    : {
        "Function": "Noun",
        "Gender": "Neuter"
    },
    "P"      : {
        "Function": "Personal Pronoun"
    },
    "P-1"    : {
        "Function": "Personal Pronoun",
        "Person": "1st"
    },
    "P-2"    : {
        "Function": "Personal Pronoun",
        "Person": "2nd"
    },
    "Q"      : {
        "Function": "Correlative or Interrogative"
    },
    "R"      : {
        "Function": "Relative Pronoun"
    },
    "S-1"    : {
        "Function": "Possessive Pronoun",
        "Person": "1st"
    },
    "S-2"    : {
        "Function": "Possessive Pronoun",
        "Person": "2nd"
    },
    "T"      : {
        "Function": "Article"
    },
    "V"      : {
        "Function": "Verb"
    },
    "X"      : {
        "Function": "Indefinite Pronoun"
    },
}

class TEBSG(LexiconBase):
    def __init__(self, manager, log):
        super().__init__(
            manager         = manager, 
            log             = log, 
            start_marker    = "eStrong	dStrong	uStrong	Greek	Transliteration	Morph	Gloss	Abbott-Smith lexicon (AS), with gaps occationally filled from edited versions of  Middle LSJ ",
            codes           = CODES
        )
        
    def download_files(self):

        FILE = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TEBSG.txt",
            description         = "TEBSG - Translators Brief lexicon of Extended Strongs for Greek",
            citation            = None
        )
        FILE.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TEBSG",
            source_name         = "TEBSG",
            version             = None,
            note                = "TEBSG - Translators Brief lexicon of Extended Strongs for Greek"
        )
        FILE.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )
        self.process_file(FILE)

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEBSG(
        manager     = manager,
        log         = log,
    )