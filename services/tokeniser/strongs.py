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
        "get_strongs_relation": """
            WITH target AS (
                SELECT id
                FROM bible.lexemes
                WHERE strongs_code = %s
            ),
            edges AS (
                SELECT
                    lr.relation_type,
                    lr.from_lexeme AS source_id,
                    lr.to_lexeme   AS target_id
                FROM bible.lexeme_relations lr
                JOIN target t ON lr.from_lexeme = t.id

                UNION ALL

                SELECT
                    lr.relation_type,
                    lr.to_lexeme   AS source_id,
                    lr.from_lexeme AS target_id
                FROM bible.lexeme_relations lr
                JOIN target t ON lr.to_lexeme = t.id
            )
            SELECT DISTINCT
                e.relation_type,

                lf.id           AS from_id,
                lf.strongs_code AS from_strongs,
                lf.lemma        AS from_lemma,

                lt.id           AS to_id,
                lt.strongs_code AS to_strongs,
                lt.lemma        AS to_lemma
            FROM edges e
            JOIN bible.lexemes lf ON lf.id = e.source_id
            JOIN bible.lexemes lt ON lt.id = e.target_id;
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
        relations = self.db.fetch_all(self.SQL.get("get_strongs_relation"), (self.strong,))
        # print(relations)
        # print("===========================")

        all_relations = set()
        
        for relation_type, from_id, from_strongs, from_lemma, to_id, to_strongs, to_lemma in relations:
            if from_strongs != self.strong:
                all_relations.add(from_strongs)
            
            if to_strongs != self.strong:
                all_relations.add(to_strongs)

        self.connected_relations = all_relations

if __name__ == "__main__":
    Strongs(ManagerHandler(), "H1254", 1)