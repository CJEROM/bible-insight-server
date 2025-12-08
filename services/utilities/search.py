from manager.managerhandler import ManagerHandler
from tokeniser.assembler import Assembler

class Search():
    SQL = {

    }

    def __init__(self):
        self.manager = ManagerHandler()
        self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        self.db = self.manager.get_db()
        self.log = self.manager.create_log("search")
        self.log.set_logging_level(2)

        # For setting context that we want to search in.
        self.language_id    = None
        self.translation_id = None
        self.scope          = None # Book, Chapter, Verse
        self.book           = None
        self.chapter        = None
        self.verse          = None

        self.results = []

    def set_translation_context(self, translation_id=None):
        self.translation_id = translation_id

    def set_language_context(self, language_id=None, language_iso=None):
        # can set language from either id or iso
        self.language_id = language_id
    
    def search_word(self, word):
        pass

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
    pass