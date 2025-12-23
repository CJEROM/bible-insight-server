from manager.managerhandler import ManagerHandler

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
            WITH target_lexeme AS (
                SELECT id
                FROM bible.lexemes
                WHERE strongs_code = %s
            )
            SELECT
                lr.relation_type,
                --lr.confidence,
                --lr.notes,

                l_from.id            AS from_id,
                l_from.strongs_code  AS from_strongs,
                l_from.lemma         AS from_lemma,

                l_to.id              AS to_id,
                l_to.strongs_code    AS to_strongs,
                l_to.lemma           AS to_lemma
            FROM bible.lexeme_relations lr
            JOIN target_lexeme t
            ON lr.from_lexeme = t.id
            OR lr.to_lexeme   = t.id
            JOIN bible.lexemes l_from ON l_from.id = lr.from_lexeme
            JOIN bible.lexemes l_to   ON l_to.id   = lr.to_lexeme;
        """
    }

    def __init__(self, manager: ManagerHandler, strong, translation_id, recursive_limit:int=3, recursive_depth:int=0):
        self.manager = manager
        self.db = manager.get_db()

        self.strong = strong
        self.translation_id = translation_id
        self.recursive_depth = recursive_depth
        self.recursive_limit = recursive_limit
        
        self.details = {
            
        }

        self.search_strongs()
        self.get_strong_data()
        self.strongs_recursion()

    def search_strongs(self):
        # Find all unique words that use this strong code
        unique_words = self.db.fetch_all(self.SQL.get("get_unique_strong_text"), (self.strong, self.translation_id))
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
        print(relations)
        print("===========================")
        all_relations = set()
        for relation_type, from_id, from_strongs, from_lemma, to_id, to_strongs, to_lemma in relations:
            if from_strongs != self.strong:
                all_relations.add(from_strongs)
            
            if to_strongs != self.strong:
                all_relations.add(to_strongs)
        
        for relation in all_relations:
            new_depth = self.recursive_depth+1
            if new_depth <= self.recursive_limit:
                Strongs(self.manager, relation, self.translation_id, self.recursive_limit, new_depth)

if __name__ == "__main__":
    Strongs(ManagerHandler(), "H1254", 1)