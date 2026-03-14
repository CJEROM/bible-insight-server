# Translators Amalgamated OT+NT/TAGNT Act-Rev - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt
# https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Act-Rev%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt

from itertools import count

from ingestor.stepbible.download_file import DownloadFile

from manager.managerhandler import ManagerHandler
from manager.logmanager import LogManager

from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

import re

class TAGNT():
    def __init__(self, 
            manager: ManagerHandler, 
            log: LogManager
        ):

        self.manager        = manager
        self.log            = log
        self.db             = self.manager.get_db()

        self.read           = StepBibleReadBoundary(self.db)
        self.write          = StepBibleWriteBoundary(self.db)

        self.process_file()

    def download_files(self):

        MAT_JHN = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
            file_name           = "TAGNT MAT-JHN.txt",
            description         = "Translators Amalgamated Greek NT",
            citation            = None
        )
        MAT_JHN.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAGNT",
            source_name         = "TAGNT",
            version             = None,
            note                = "Translators Amalgamated Greek NT"
        )
        MAT_JHN.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        ACT_REV = DownloadFile(
            main_manager        = self.manager,
            log                 = self.log,
            link                = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/refs/heads/master/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Act-Rev%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt",
            file_name           = "TAGNT ACT-REV.txt",
            description         = "Translators Amalgamated Greek NT",
            citation            = None
        )
        ACT_REV.create_source(
            parent_source_code  = "STEPBIBLE",
            source_code         = "TAGNT",
            source_name         = "TAGNT",
            version             = None,
            note                = "Translators Amalgamated Greek NT"
        )
        ACT_REV.map_license(
            license_code    = "CC BY 4.0",
            is_new_license  = False
        )

        return [MAT_JHN, ACT_REV]

    def process_file(self):
        downloaded_files = self.download_files()

        for file in downloaded_files:
            # Read one of downloaded files
            with open(file.this_file_path, "r", encoding="utf-8") as f:
                # Loop through file line by line
                count = 0
                valid = False

                for line in f:
                    # Check if line is divider (indicates where data to ingest starts)
                    if set(line.strip()) == {"="} and len(line.strip()) > 150:
                        print("Divider detected")

                    # We don't care about these lines, since less structured duplicate data
                    if line.startswith("#"):
                        # print("Comment line detected")
                        continue

                    if line.startswith("Word & Type"):
                        valid = True
                        continue

                    # count += 1
                    # if count > 120:
                    #     return

                    # Check if blank line (indicates where data to ingest ends)
                    only_line = line.rstrip('\n')
                    if only_line.strip('\t') == '':
                        print("Only tabs")
                        valid = False

                    if valid:
                        self.process_line(line)

    def process_line(self, 
            line: str
        ):
        print(line[0:10])
        data                = line.split("\t")

        # Process data from each column into separate values to be processed
        word_type           = self.process_word_type(
            word_type_data          = data[0]
        )
        greek               = self.process_greek(
            greek_data              = data[1]
        )
        english             = self.process_english(
            english_data            = data[2]
        )
        dStrong_grammar     = self.process_dStrong_grammar(
            dStrong_grammar_data    = data[3]
        )
        dictionary_gloss    = self.process_dictionary_gloss(
            dictionary_gloss_data   = data[4]
        )
        editions            = self.process_editions(
            editions_data           = data[5]
        )
        meaning_variants    = self.process_meaning_variants(
            meaning_variants_data   = data[6]
        )
        spelling_variants   = self.process_spelling_variants(
            spelling_variants_data  = data[7]
        )
        spanish             = self.process_spanish(
            spanish_data            = data[8]
        )
        sub_meanings        = self.process_sub_meanings(
            sub_meanings_data       = data[9]
        )
        conjoined_data      = self.process_conjoined_data(
            conjoined_data          = data[10]
        )
        sStrong_instance    = self.process_sStrong_instance(
            sStrong_instance_data   = data[11]
        )
        alt_strongs         = self.process_alt_strongs(
            alt_strongs_data        = data[12]
        )
        variant_notes       = self.process_variant_notes(
            variant_notes_data      = data[13]
        )

        # Write to database
        self.write.write_tagnt(
            # Word & Type - e.g. Act.1.3#01=NKO
            verse                   = data[0].split("#")[0],
            word_position           = data[0].split("#")[1].split("=")[0],
            word_type               = data[0].split("#")[1].split("=")[1],
            # Greek - e.g. ἔστησαν
            greek                   = data[1].split(" ")[0],
            transliteration         = re.search(r"\(([^)]*)\)", data[1]).group(1),
            # English
            english                 = data[2],
            # D-Strong's = Grammar
            dStrong                 = data[3].split("=")[0],
            grammar                 = data[3].split("=")[1],
            # Dictionary from = gloss
            dictionary_form         = data[4].split("=")[0],
            gloss                   = data[4].split("=")[1],
            # editions
            editions                = data[5],
            # Meaning variants
            meaning_variants        = data[6],
            # Spelling variants
            spelling_variants       = data[7],
            # Spanish
            spanish                 = data[8],
            # Sub meaing
            sub_meanings            = data[9],
            # Conjoined word
            conjoined_data          = data[10],
            # sStrong + instance
            sStrong                 = data[11].split("_")[0],
            instance                = data[11].split("_")[1] if len(data[11].split("_")) > 1 else None,
            # Alt Strongs
            alt_strongs             = data[12],
            # Variant notes
            variant_notes           = data[13]
        )

    # ========================================================================================================================
    #                           Methods to process each column of data into values to be written to database
    # ========================================================================================================================

    def process_word_type(self, 
            word_type_data  : str
        ):
        verse                   = word_type_data.split("#")[0],
        word_position           = word_type_data.split("#")[1].split("=")[0],
        word_type               = word_type_data.split("#")[1].split("=")[1],


    def process_greek(self, 
            greek_data      : str
        ):
        greek_word              = greek_data.split(" ")[0],
        transliteration         = re.search(r"\(([^)]*)\)", greek_data).group(1),

    def process_english(self, 
            english_data    : str
        ):
        pass

    def process_dStrong_grammar(self, 
            dStrong_grammar_data : str
        ):
        dStrong                 = dStrong_grammar_data.split("=")[0],
        grammar                 = dStrong_grammar_data.split("=")[1],
        pass

    def process_dictionary_gloss(self, 
            dictionary_gloss_data   : str
        ):
        dictionary_form         = dictionary_gloss_data.split("=")[0],
        gloss                   = dictionary_gloss_data.split("=")[1],
        pass

    def process_editions(self, 
            editions_data : str
        ):
        pass

    def process_meaning_variants(self, 
            meaning_variants_data : str
        ):
        pass

    def process_spelling_variants(self, 
            spelling_variants_data : str
        ):
        pass

    def process_spanish(self, 
            spanish_data : str
        ):
        pass

    def process_sub_meanings(self, 
            sub_meanings_data : str
        ):
        pass

    def process_conjoined_data(self, 
            conjoined_data : str
        ):
        pass

    def process_sStrong_instance(self, 
            sStrong_instance_data : str
        ):
        sStrong                 = sStrong_instance_data.split("_")[0],
        instance                = sStrong_instance_data.split("_")[1] if len(sStrong_instance_data.split("_")) > 1 else None,
        pass

    def process_alt_strongs(self, 
            alt_strongs_data : str
        ):
        pass

    def process_variant_notes(self, 
            variant_notes : str
        ):
        pass

if __name__ == "__main__":
    manager = ManagerHandler()
    log     = manager.create_log_in_folder(["logs", "ingestor", "stepbible"])

    TAGNT(
        manager     = manager,
        log         = log,
    )