from manager.managerhandler import ManagerHandler

class Strongs():
    SQL = {
        "get_unique_strong_text": """
            WITH strongs_nodes AS (
                SELECT id
                FROM bible.nodes
                WHERE strong = %s
            )
            SELECT DISTINCT n.node_text
            FROM bible.nodes n
            JOIN strongs_nodes sn
            ON n.parent_node_id = sn.id
            WHERE n.node_text IS NOT NULL
            AND n.node_text <> '';
        """,
    }

    def __init__(self, manager: ManagerHandler, strong, translation_id):
        self.manager = manager
        self.db = manager.get_db()

        self.strong = strong
        self.translation_id = translation_id
        
        self.details = {
            #
        }

        self.search_strongs()

    def search_strongs(self):
        # Find all unique words that use this strong code
        unique_words = self.db.fetch_all(self.SQL.get("get_unique_strong_text"), (self.strong,))
        for word in unique_words:
            print(word)

if __name__ == "__main":
    Strongs(ManagerHandler())