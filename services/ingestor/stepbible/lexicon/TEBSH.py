# Lexicons/TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESH%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Hebrew%20-%20STEPBible.org%20CC%20BY.txt

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler

from ingestor.stepbible.lexicon.lexicon_base import LexiconBase

CODES = {
    "Adv"       : {
        "Function": "Adverb"
    },
    "Cond"      : {
        "Function": "Conditional"
    },
    "Conj"      : {
        "Function": "Conjunction"
    },
    "DemP"      : {
        "Function": "Demonstrative Pronoun"
    },
    "IndP"      : {
        "Function": "Indefinite Pronoun"
    },
    "Intg"      : {
        "Function": "Interogative"
    },
    "Intj"      : {
        "Function": "Interjection"
    },
    "N--TG"     : {
        "Function": "Noun",
        "Name type": "Title Gentilic"
    },
    "N-F-PG"    : {
        "Function": "Noun",
        "Gender": "Feminine",
        "Name type": "Person Gentilic"
    },
    "N-F-T"     : {
        "Function": "Noun",
        "Gender": "Feminine",
        "Name type": "Title"
    },
    "N-M-PG"    : {
        "Function": "Noun",
        "Gender": "Masculine",
        "Name type": "Person Gentilic"
    },
    "Neg"       : {
        "Function": "Negative"
    },
    "Op1c"      : {
        "Function": "Suffix",
        "Person": "1st",
        "Form": "Common",
        "Number": "Plural"
    },
    "Op2f"      : {
        "Function": "Suffix",
        "Person": "2nd",
        "Gender": "Feminine",
        "Number": "Plural"
    },
    "Op2m"      : {
        "Function": "Suffix",
        "Person": "2nd",
        "Gender": "Masculine",
        "Number": "Plural"
    },
    "Op3f"      : {
        "Function": "Suffix",
        "Person": "3rd",
        "Gender": "Feminine",
        "Number": "Plural"
    },
    "Op3m"      : {
        "Function": "Suffix",
        "Person": "3rd",
        "Gender": "Masculine",
        "Number": "Plural"
    },
    "Os1c"      : {
        "Function": "Suffix",
        "Person": "1st",
        "Form": "Common",
        "Number": "Singular"
    },
    "Os2f"      : {
        "Function": "Suffix",
        "Person": "2nd",
        "Gender": "Feminine",
        "Number": "Singular"
    },
    "Os2m"      : {
        "Function": "Suffix",
        "Person": "2nd",
        "Gender": "Masculine",
        "Number": "Singular"
    },
    "Os3f"      : {
        "Function": "Suffix",
        "Person": "3rd",
        "Gender": "Feminine",
        "Number": "Singular"
    },
    "Os3m"      : {
        "Function": "Suffix",
        "Person": "3rd",
        "Gender": "Masculine",
        "Number": "Singular"
    },
    "Part"      : {
        "Function": "Particle"
    },
    "PerP-CP"   : {
        "Function": "Personal Pronoun",
        "Form": "Common",
        "Number": "Plural"
    },
    "PerP-CS"   : {
        "Function": "Personal Pronoun",
        "Form": "Common",
        "Number": "Singular"
    },
    "PerP-FP"   : {
        "Function": "Personal Pronoun",
        "Gender": "Feminine",
        "Number": "Plural"
    },
    "PerP-FS"   : {
        "Function": "Personal Pronoun",
        "Gender": "Feminine",
        "Number": "Singular"
    },
    "PerP-MP"   : {
        "Function": "Personal Pronoun",
        "Gender": "Masculine",
        "Number": "Plural"
    },
    "PerP-MS"   : {
        "Function": "Personal Pronoun",
        "Gender": "Masculine",
        "Number": "Singular"
    },
    "Pp1c"      : {
        "Function": "Suffix",
        "Form": "Common",
        "Number": "Plural",
        "Person": "1st"
    },
    "Pp2f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "2nd",
        "Number": "Plural",
    },
    "Pp2m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "2nd",
        "Number": "Plural",
    },
    "Pp3f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "3rd",
        "Number": "Plural",
    },
    "Pp3m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "3rd",
        "Number": "Plural",
    },
    "Prefix"    : {
        "Function": ""
    },
    "Prep"      : {
        "Function": "Preposition"
    },
    "Punct."    : {
        "Function": "Punctuation"
    },
    "Ps1c"      : {
        "Function": "Suffix",
        "Form": "Common",
        "Person": "1st",
        "Number": "Singular",
    },
    "Ps2f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "2nd",
        "Number": "Singular",
    },
    "Ps2m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "2nd",
        "Number": "Singular",
    },
    "Ps3f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "3rd",
        "Number": "Singular",
    },
    "Ps3m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "3rd",
        "Number": "Singular",
    },
    "RelP"      : {
        "Function": "Relative Pronoun"
    },
    "Sp1c"      : {
        "Function": "Suffix",
        "Form": "Common",
        "Person": "1st",
        "Number": "Plural",
    },
    "Sp2f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "2nd",
        "Number": "Plural",
    },
    "Sp2m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "2nd",
        "Number": "Plural",
    },
    "Sp3f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "3rd",
        "Number": "Plural",
    },
    "Sp3m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "3rd",
        "Number": "Plural",
    },
    "Ss1c"      : {
        "Function": "Suffix",
        "Form": "Common",
        "Person": "1st",
        "Number": "Singular",
    },
    "Ss2f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "2nd",
        "Number": "Singular",
    },
    "Ss2m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "2nd",
        "Number": "Singular",
    },
    "Ss3f"      : {
        "Function": "Suffix",
        "Gender": "Feminine",
        "Person": "3rd",
        "Number": "Singular",
    },
    "Ss3m"      : {
        "Function": "Suffix",
        "Gender": "Masculine",
        "Person": "3rd",
        "Number": "Singular",
    },
    "Suffix"    : {
        "Function": ""
    },
}

class TEBSH(LexiconBase):
    def __init__(self, manager, log):
        super().__init__(
            manager         = manager, 
            log             = log, 
            start_marker    = "eStrong#	dStrong	uStrong	Hebrew	Transliteration	Morph	Gloss	Meaning",
            codes           = CODES
        )

    def download_files(self):

        FILE = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Lexicons/TBESH%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Hebrew%20-%20STEPBible.org%20CC%20BY.txt",
            file_name           = "TEBSH.txt",
            description         = "TEBSH - Translators Brief lexicon of Extended Strongs for Hebrew",
            citation            = None
        )
        FILE.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TEBSH",
            source_name         = "TEBSH",
            version             = None,
            note                = "TEBSH - Translators Brief lexicon of Extended Strongs for Hebrew"
        )
        FILE.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )
        self.process_file(FILE)

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TEBSH(
        manager     = manager,
        log         = log,
    )