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
        """
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
        self.get_strong_data()

    def search_strongs(self):
        # Find all unique words that use this strong code
        unique_words = self.db.fetch_all(self.SQL.get("get_unique_strong_text"), (self.strong, self.translation_id))
        for word in unique_words:
            print(word)

    def get_strong_data(self):
        info = self.db.fetch_all(self.SQL.get("get_strong_data"), (self.strong,))
        print(info)

if __name__ == "__main__":
    Strongs(ManagerHandler(), "H1254", 1)