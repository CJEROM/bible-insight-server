from manager.managerhandler import ManagerHandler
from tokeniser.assembler import Assembler

class Search():
    SQL = {
        "get_languages": """
            SELECT id, iso, name, namelocal, scriptdirection 
            FROM bible.languages;
        """,
        "get_translations_info": """
            SELECT dbl_id, medium, name, namelocal, abbreviationlocal, language_id
            FROM bible.translationinfo;
        """,
        "get_translations": """
            SELECT dbl_id, agreement_id
            FROM bible.translations;
        """,
        "get_books": """
            SELECT id, book_code, translation_id, file_id, short
            FROM bible.booktofile;
        """,
        #
        "get_word_nodes": """
            SELECT id
            FROM bible.nodes
            WHERE node_text LIKE %s
                AND translation_id = %s
                AND is_tokenisable = TRUE;
        """
    }

    def __init__(self):
        self.manager = ManagerHandler()
        self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        self.db = self.manager.get_db()
        self.log = self.manager.create_log("search")
        self.log.set_logging_level(2)

        # For setting context that we want to search in.
        self.languages          = {}
        self.translations       = {}
        self.scope              = "verse" # Book, Chapter, Verse
        self.books              = {}

        self.translation_id     = 1

        self.results = []

    def init_filters(self):
        languages       = self.db.fetch_all(self.SQL.get("get_languages"))
        translationinfo = self.db.fetch_all(self.SQL.get("get_translations_info"))
        translations    = self.db.fetch_all(self.SQL.get("get_translations"))
        books           = self.db.fetch_all(self.SQL.get("get_books"))

    def set_translation_context(self, translation_id=None):
        self.translation_id = translation_id

    def set_language_context(self, language_id=None, language_iso=None):
        # can set language from either id or iso
        self.language_id = language_id
    
    def search_word(self, word):
        result_nodes = self.db.fetch_all(self.SQL.get("get_word_nodes"), (f"%{word}%", self.translation_id))
        final_results = []
        for node_id in result_nodes:
            new_result = Assembler(manager=self.manager, scope=self.scope, node_id=node_id, translation_id=self.translation_id)
            final_results.append(new_result)
            print(new_result.get_details())

    def search_strongs(self, strongs):
        pass

    def strongs_autocorrect_suggestions(self, strongs):
        pass

    def search_tokens(self, token):
        pass

    def token_autocorrect_suggestions(self, token):
        pass

    def search_entities(self, entity_id):
        pass

    def compare_translations(self, ref):
        pass


if __name__ == "__main__":
    new_search = Search()
    new_search.search_word("fruit")