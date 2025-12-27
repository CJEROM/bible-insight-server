from manager.managerhandler import ManagerHandler

from tokeniser.assembler import Assembler
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tokeniser.strongs import Strongs

class Strongs():
    SQL = {
        "get_unique_strong_text": """
            SELECT
                p.id        AS strong_node_id,
                c.id        AS text_node_id,
                c.node_text AS text
            FROM bible.nodes p
            JOIN bible.nodes c
                ON c.parent_node_id = p.id
            WHERE p.strong = %s
            AND p.translation_id = %s
            AND c.node_text IS NOT NULL
            AND c.node_text <> ''
            ORDER BY p.id ASC;
        """,
        "get_strong_data": """
            SELECT id, source, source_version, strongs_code, language_id, lemma, raw_pos, transliteration, pronunciation, audio_file, raw_gloss FROM bible.lexemes WHERE strongs_code = %s
        """,
        "get_strongs_to_relation": """
            SELECT 
                lr.to_lexeme, 
                l.strongs_code,
                l.native_word,
                l.lemma,
                l.raw_pos,
                l.transliteration,
                l.pronunciation,
                l.raw_gloss
            FROM bible.lexemes l
            JOIN bible.lexeme_relations lr ON l.id = lr.to_lexeme
            WHERE lr.from_lexeme = %s
        """,
        "get_strongs_from_relation": """
            SELECT 
                lr.from_lexeme, 
                l.strongs_code,
                l.native_word,
                l.lemma,
                l.raw_pos,
                l.transliteration,
                l.pronunciation,
                l.raw_gloss
            FROM bible.lexemes l
            JOIN bible.lexeme_relations lr ON l.id = lr.from_lexeme
            WHERE lr.to_lexeme = %s
        """,
        "": """"

        """
    }

    def __init__(self, manager: ManagerHandler, strong, translation_id):
        self.strong = strong
        self.translation_id = translation_id

        self.manager = manager
        self.db = manager.get_db()
        self.log = manager.create_log_in_folder(["logs", "strongs"], self.strong)
        
        self.details = {}

        self.search_strongs()
        self.get_strong_data()

        self.connected_relations = set()
        # Create local version for this object, where you link the object if its already been created.

        self.strongs_recursion()
    
    def get_strong(self):
        return self.strong
    
    def get_details(self, key:str = None):
        if key:
            return self.details.get(key)
        
        return self.details
    
    def get_connected_relations(self):
        return self.connected_relations
    
    def get_occurences(self, key:str=None, display=False, count=False, verses=False, words=False):
        # Combinations (priority order):

        # Key => Unique word

        #   - words             =>  Unique Word Occurences
        #   - count + key       =>  Number of unique occurences for specified Unique Word
        #   - display           -> Print Each occurence to console (MODIFY IN FUTURE TO EXPORT TO MARKDOWN IN OBSIDIAN), EXCEPTIONS: [words, count + key]
        #   - count + words     =>  Unique Word Occurences + Number of occurences for each unique word
        #   - verses            =>  Unique Verses with Occurences
        #   - verses + key      =>  Unique Verses with specified Unique Word
        #   - display + verses  -> To see specifically the unique verses included
        #   - NONE              =>  Unique Word Occurences with their Unique Verse Occurences (one verse can be mentioned multiple times across unique words)

        if not self.details.get("occurences"): return None
        if key and words: return None
        if verses and words: return None

        valid = True
        unique_counts = []
        unique_verses = set()

        #  =>  Unique Word Occurences
        all_keys = self.details["occurences"].keys()
        sorted_keys = sorted(all_keys, key=str.lower)
        if words and not count: 
            return sorted_keys

        for this_key in sorted_keys:
            results = self.details["occurences"].get(this_key)

            if key:
                if key == this_key:
                    valid = True
                else:
                    valid = False

                #  =>  Number of unique occurences for specified Unique Word
                if count: 
                    return len(self.details["occurences"].get(key))

            if valid:
                #  -> Print Each occurence to console
                if display and not verses:
                    for assembled_verse in results:
                        full_ref = assembled_verse.get_details("full_ref")
                        text = assembled_verse.get_details("text")
                        print(f"\n{full_ref} => [{this_key}] => [{text}]\n")

                #  =>  Unique Word Occurences + Number of occurences for each unique word
                if count and words: 
                    unique_counts.append([this_key, len(results)])
                
                # ONE OF:
                #        =>  Unique Verses with Occurences
                # [key]  =>  Unique Verses with specified Unique Word
                elif verses:
                    for assembled_verse in results:
                        unique_verses.add(assembled_verse)

        if verses:
            sorted_unqiue_verses = sorted(unique_verses, key=lambda v: (v.get_details("book"), v.get_details("chapter"), v.get_details("verse")))
            if display:
                for verse in sorted_unqiue_verses:
                    print(verse.get_details("full_ref"))
            return sorted_unqiue_verses

        if count and words:
            return sorted(unique_counts, key=lambda c: c[0].lower())
        
        return results
    
    def search_strongs(self):
        # Find all unique words that use this strong code
        all_occurences = self.db.fetch_all(self.SQL.get("get_unique_strong_text"), (self.strong, self.translation_id))
        
        cleaned_occurences = {}

        for strong_node_id, text_node_id, strongs_text in all_occurences:
            if cleaned_occurences.get(strongs_text):
                cleaned_occurences[strongs_text].add(Assembler(manager=self.manager, node_id=strong_node_id, scope="verse"))
            else:
                cleaned_occurences[strongs_text] = set()
                cleaned_occurences[strongs_text].add(Assembler(manager=self.manager, node_id=strong_node_id, scope="verse"))
        
        self.details["occurences"] = cleaned_occurences

    def get_strong_data(self):
        info = self.db.fetch_one(self.SQL.get("get_strong_data"), (self.strong,))

        # Mirror SELECT DB Query
        id, source, source_version, strongs_code, language_id, lemma, raw_pos, transliteration, pronunciation, audio_file, raw_gloss = info

        self.details["id"] = id # Lexeme_id
        self.details["code"] = self.strong # or strongs_code
        self.details["pos"] = raw_pos
        self.details["gloss"] = raw_gloss

    def strongs_recursion(self):
        lexeme_id = self.details["id"]
        to_relations = self.db.fetch_all(self.SQL.get("get_strongs_to_relation"), (lexeme_id,))
        from_relations = self.db.fetch_all(self.SQL.get("get_strongs_from_relation"), (lexeme_id,))
        relations = to_relations + from_relations

        all_relations = set()

        for relation_lexeme_id, strongs_code, native_word, lemma, raw_pos, transliteration, pronunciation, raw_gloss in relations:
            if strongs_code != self.strong:
                all_relations.add(strongs_code)

    def write_to_obsidian(self):
        pass

def test_Strongs(object: Strongs, test_case, excluded=[]):
    if test_case in excluded:
        print("EXCLUDED! Skipping...")
        return
       
    match test_case:
        # ==================================================== SUCCESS Test Cases ====================================================
        case 0: #   - words             =>  Unique Word Occurences
            print(object.get_occurences(
                key=None, 
                count=False, 
                verses=False, 
                words=True,
                display=False
            ))
        case 1: #   - count + key       =>  Number of unique occurences for specified Unique Word
            print(object.get_occurences(
                key="created", 
                count=True, 
                verses=False, 
                words=False,
                display=False
            ))
        case 2: #   - display           -> Print Each occurence to console (MODIFY IN FUTURE TO EXPORT TO MARKDOWN IN OBSIDIAN), EXCEPTIONS: [words, count + key]
            print(object.get_occurences(
                key=None, 
                count=False, 
                verses=False, 
                words=False,
                display=True
            ))
        case 3: #   - count + words     =>  Unique Word Occurences + Number of occurences for each unique word
            print(object.get_occurences(
                key=None, 
                count=True, 
                verses=False, 
                words=True,
                display=False
            ))
        case 4: #   - verses            =>  Unique Verses with Occurences
            print(object.get_occurences(
                key=None, 
                count=False, 
                verses=True, 
                words=False,
                display=False
            ))
        case 5: #   - verses + key      =>  Unique Verses with specified Unique Word
            print(object.get_occurences(
                key="created", 
                count=False, 
                verses=True, 
                words=False,
                display=False
            ))
        case 6: #   - display + verses  -> To see specifically the unique verses included
            print(object.get_occurences(
                key=None, 
                count=False, 
                verses=True, 
                words=False,
                display=True
            ))
        case 7: #   - NONE              =>  Unique Word Occurences with their Unique Verse Occurences (one verse can be mentioned multiple times across unique words)
            print(object.get_occurences(
                key=None, 
                count=False, 
                verses=False, 
                words=False,
                display=False
            ))
    
    # match test_case:
        # ==================================================== EDGE Test Cases ====================================================
        # I considered setting these up, but too cumbersome to validate, so will set to return null if conflicting configs set

    match test_case:
        # ==================================================== FAILED Test Cases ====================================================
        case 8: #   - verses + words
            print(object.get_occurences(
                key=None, 
                count=False, 
                verses=True, 
                words=True,
                display=False
            ))
        case 9: #   - key + words
            print(object.get_occurences(
                key=None, 
                count=False, 
                verses=True, 
                words=True,
                display=False
            ))
        
if __name__ == "__main__":
    temp = Strongs(ManagerHandler(), "H1254", 1)
    test_case = -1

    for test_case in range(0, 10):
        print(f"\n==================================================== TEST: {test_case} ====================================================\n")
        test_Strongs(temp, test_case, [2])