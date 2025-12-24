from manager.managerhandler import ManagerHandler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tokeniser.strongs import Strongs

class Strongs():
    SQL = {
        "get_unique_strong_text": """
            WITH strongs_nodes AS (
                SELECT id
                FROM bible.nodes
                WHERE strong = %s AND translation_id = %s
            )
            SELECT
                n.node_text,
                COUNT(*) AS occurrence_count
            FROM bible.nodes n
            JOIN strongs_nodes sn
            ON n.parent_node_id = sn.id
            WHERE n.node_text IS NOT NULL
            AND n.node_text <> ''
            GROUP BY n.node_text
            ORDER BY occurrence_count DESC;
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
    
    def search_strongs(self):
        # Find all unique words that use this strong code
        unique_words = self.db.fetch_all_single(self.SQL.get("get_unique_strong_text"), (self.strong, self.translation_id))
        self.details["occurences"] = unique_words
        for word in unique_words:
            print(word)

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
    Strongs(ManagerHandler(), "H1254", 1)