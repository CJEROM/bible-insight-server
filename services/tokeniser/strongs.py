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
            AND c.node_text <> '';
        """,
        "get_strong_data": """
            SELECT * FROM bible.lexemes WHERE strongs_code = %s
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
        self.manager = manager
        self.db = manager.get_db()

        self.strong = strong
        self.translation_id = translation_id
        
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
    
    def get_occurences(self, key:str=None, display=False, count=False, unique=False):
        if not self.details.get("occurences"): return None
        
        valid = True
        unique_counts = []
        for this_key in self.details["occurences"].keys():
            if key:
                if key == this_key:
                    valid = True
                else:
                    valid = False

            if valid:
                results = self.details["occurences"].get(this_key)
                # if count and unique active, return the count of each unique occurence
                if count and unique:
                    unique_counts.append([this_key, len(results)])

                # Can only properly return count of occurence when selecting specific one
                elif count and key: 
                    return len(results)
                
                # Returns all unique text occurences
                elif unique:
                    return results.keys()
                
                # If display enable, will print results to console for viewing
                if display:
                    for assembled_verse in results:
                        full_ref = assembled_verse.get_details("full_ref")
                        text = assembled_verse.get_details("text")
                        print(f"\n{full_ref} => [{text}]\n")

        if count and unique:
            return 
        
        return results
    
    def search_strongs(self):
        # Find all unique words that use this strong code
        all_occurences = self.db.fetch_all(self.SQL.get("get_unique_strong_text"), (self.strong, self.translation_id))
        
        cleaned_occurences = {}

        for strong_node_id, text_node_id, strongs_text in all_occurences:
            if cleaned_occurences.get(strongs_text):
                cleaned_occurences[strongs_text].append(Assembler(manager=self.manager, node_id=strong_node_id, scope="verse"))
            else:
                cleaned_occurences[strongs_text] = [Assembler(manager=self.manager, node_id=strong_node_id, scope="verse")]
        
        self.details["occurences"] = cleaned_occurences

    def get_strong_data(self):
        info = self.db.fetch_one(self.SQL.get("get_strong_data"), (self.strong,))
        print(info)
        self.details["id"] = info[0] # Lexeme_id
        self.details["code"] = self.strong
        self.details["pos"] = info[7]
        self.details["gloss"] = info[11]

    def strongs_recursion(self):
        lexeme_id = self.details["id"]
        to_relations = self.db.fetch_all(self.SQL.get("get_strongs_to_relation"), (lexeme_id,))
        from_relations = self.db.fetch_all(self.SQL.get("get_strongs_from_relation"), (lexeme_id,))
        relations = to_relations + from_relations
        print(relations)
        # print("===========================")

        all_relations = set()

        for relation_lexeme_id, strongs_code, native_word, lemma, raw_pos, transliteration, pronunciation, raw_gloss in relations:
            if strongs_code != self.strong:
                all_relations.add(strongs_code)

    def write_to_obsidian(self):
        pass
        
if __name__ == "__main__":
    temp = Strongs(ManagerHandler(), "H1254", 1)
    # print(temp.get_details())
    temp.get_occurences(display=True)