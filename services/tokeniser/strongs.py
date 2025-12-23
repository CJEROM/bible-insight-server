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

    def __init__(self, manager: ManagerHandler, strong, translation_id, recursive_limit:int=3, recursive_depth:int=0, parent_object: "Strongs" = None):
        self.manager = manager
        self.db = manager.get_db()

        self.parent_object = parent_object

        self.strong = strong
        self.translation_id = translation_id
        self.recursive_depth = recursive_depth
        self.recursive_limit = recursive_limit
        
        self.details = {}
        self.all_objects = {}

        self.search_strongs()
        self.get_strong_data()

        self.root = False
        if recursive_depth == 0:
            self.root = True
            self.set_new_child_object(self.strong, self)
        else:
            self.get_root().set_new_child_object(self.strong, self)

        self.connected_relations = {}
        # Create local version for this object, where you link the object if its already been created.

        self.strongs_recursion()

    def get_root(self):
        strong_object = self
        while not strong_object.is_root():
            strong_object = strong_object.get_parent_object()

        return strong_object
    
    def get_object_in_root(self, strongs_code):
        if self.root:
            return self.all_objects.get(strongs_code)
        
        return None

    def get_parent_object(self):
        return self.parent_object

    def is_root(self):
        return self.root
    
    def get_strong(self):
        return self.strong
    
    def get_details(self):
        return self.details
    
    def get_connected_relations(self):
        return self.connected_relations
    
    def set_new_child_object(self, strongs_code:str, object:"Strongs"):
        # Basically add all created child roots, but only if already exists
        if self.root:
            self.all_objects[strongs_code]

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

        self.all_objects[self.strong] = self

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
        
        # Before creating a new object find out whether it's already been created in the recursive stack by someone else
        for relation in all_relations:
            new_depth = self.recursive_depth+1
            if new_depth <= self.recursive_limit:
                existing_object = self.get_root().get_object_in_root(relation)
                if existing_object:
                    self.connected_relations[relation] = existing_object
                else:
                    self.connected_relations[relation] = Strongs(self.manager, relation, self.translation_id, self.recursive_limit, new_depth)

if __name__ == "__main__":
    Strongs(ManagerHandler(), "H1254", 1)