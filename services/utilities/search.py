from pathlib import Path
import os
import csv

from manager.managerhandler import ManagerHandler
from tokeniser.assembler import Assembler

class Search():
    SQL = {
        "get_languages": """
            SELECT id, iso, name, namelocal, scriptdirection 
            FROM language.languages;
        """,
        "get_translations": """
            SELECT DISTINCT ON (t.dbl_id)
                t.id,
                ti.language_id,
                ti.medium,
                ti.name,
                ti.namelocal,
                ti.abbreviationlocal
            FROM bible.translations t
            JOIN bible.translationinfo ti
            ON t.dbl_id = ti.dbl_id
            ORDER BY
                t.dbl_id,
                t.revision DESC,   -- highest revision first
                t.id ASC;          -- tie-breaker in case multiple agreements share the same revision
        """,
        "get_distinct_books": """
            SELECT DISTINCT ON (book_code)
                book_code, short
            FROM bible.booktofile
            ORDER BY
                book_code,
                id ASC;   -- choose the first row for that book_code
        """,
        "get_book": """
            SELECT id, book_code, translation_id, file_id, short
            FROM bible.booktofile
            WHERE book_code = %s AND translation_id = %s;
        """,
        #
        "get_word_nodes": """
            SELECT id
            FROM bible.nodes
            WHERE node_text LIKE %s
                AND is_tokenisable = TRUE;
        """,
        "get_strong_nodes": """
            SELECT id
            FROM bible.nodes
            WHERE strong = %s
        """,
        "get_strongs_occurences_per_translation" : """
            SELECT 
                sn.strong,
                LOWER(n.node_text) AS node_text,
                n.translation_id,
                COUNT(*) AS occurrences
            FROM bible.nodes sn
            JOIN bible.nodes n
                ON n.parent_node_id = sn.id
            WHERE sn.strong IS NOT NULL
            AND n.node_text IS NOT NULL
            AND n.node_text <> ''
            GROUP BY sn.strong, LOWER(n.node_text), n.translation_id
            ORDER BY sn.strong, occurrences DESC;
        """,
        "get_translation_books": """
            SELECT book_code FROM bible.booktofile WHERE translation_id = %s
        """
    }

    def __init__(self):
        self.manager = ManagerHandler()
        self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        self.db = self.manager.get_db()
        self.log = self.manager.create_log_in_folder(["logs", "search"])
        self.log.set_logging_level(1)

        self.filter = {
            "books": {},
            "translations": {},
            "languages": {}
        }

        self.results = []

        self.init_filter()

    def init_filter(self, is_active=True):
        languages       = self.db.fetch_all(self.SQL.get("get_languages"))
        for language in languages:
            language_id = str(language[0])
            self.filter["languages"][language_id] = {
                "code":              language[1],
                "name":             language[2],
                "namelocal":        language[3],
                "scriptdirection":  language[4],
                "active":           is_active
            }#(language, True)

        translations    = self.db.fetch_all(self.SQL.get("get_translations"))
        for translation in translations:
            translation_id = str(translation[0])
            self.filter["translations"][translation_id] = {
                "language_id":      translation[1],
                "medium":           translation[2],
                "name":             translation[3],
                "namelocal":        translation[4],
                "code":             translation[5],
                "active":           is_active
            }#(translation, True)

        books           = self.db.fetch_all(self.SQL.get("get_distinct_books"))
        for book in books:
            book_code = book[0]
            self.filter["books"][book_code] = {
                "name":             book[1],
                "active":           is_active
            }#(book, True)

        language_filter = self.filter["languages"]
        translation_filter = self.filter["translations"]
        book_filter = self.filter["books"]
        self.log.log_to_file(f"Initialised filters: [\n{language_filter}\n{translation_filter}\n{book_filter}\n]", "init_filter", "DEBUG")

    def get_filter(self, filter:str=None):
        if filter:
            return self.filter.get(filter, {})
        return self.filter

    def update_filter(self, type:str, key:str, is_active:bool):
        self.filter[type][key]["active"] = is_active
        self.log.log_to_file(f"Updating filter type: {type}, with key{key}, to {is_active}", "update_filter", "DEBUG")

        match type:
            case "languages":
                for translation in self.filter["translations"].keys():
                    if self.filter["translations"][translation]["language_id"] == key:
                        self.filter["translations"][translation]["active"] = is_active
            case "translations":
                translation_id = int(key)
                existing_books = self.db.fetch_all_single(self.SQL.get("get_translation_books"), (translation_id,))
                print(existing_books)
                for book_code in self.filter["books"].keys():
                    if book_code in existing_books:
                        self.filter["books"][book_code]["active"] = True
                    else:
                        self.filter["books"][book_code]["active"] = False
            case "books":
                pass

        language_filter = self.filter["languages"]
        translation_filter = self.filter["translations"]
        book_filter = self.filter["books"]
        self.log.log_to_file(f"Current filters: [\n{language_filter}\n{translation_filter}\n{book_filter}\n]", "update_filter", "DEBUG")
        
    def apply_filters(self, base_sql:str, filter_types:list):
        filters = self.filter
        where_clauses = []
        params = []
        self.log.log_to_file(f"Applying filters: {filter_types} to [\n{base_sql}\n]", "apply_filters", "DEBUG")

        if filters["translations"] and "translations" in filter_types:
            temp_list = []

            for key in filters["translations"].keys():
                if filters["translations"][key]["active"]:
                    temp_list.append(key)

            if len(temp_list) > 0:
                where_clauses.append("translation_id = ANY(%s)")
                params.append(temp_list)
            else:
                where_clauses.append("FALSE")

        # Languages affects translations
        if filters["languages"] and "languages" in filter_types:
            temp_list = []

            for key in filters["languages"].keys():
                if filters["languages"][key]["active"]:
                    temp_list.append(key)
                    
            if len(temp_list) > 0:
                where_clauses.append("""translation_id IN (
                    SELECT id FROM bible.translations WHERE language_id = ANY(%s)
                )""")
                params.append(temp_list)
            else:
                where_clauses.append("FALSE")

        # Translations affects books
        if filters["books"] and "books" in filter_types:
            temp_list = []

            for key in filters["books"].keys():
                if filters["books"][key]["active"]:
                    temp_list.append(key)

            if len(temp_list) > 0:
                where_clauses.append("""book_map_id IN (
                    SELECT id FROM bible.booktofile WHERE book_code = ANY(%s)
                )""")
                params.append(temp_list)
            else:
                where_clauses.append("FALSE")

        if where_clauses:
            new_query = base_sql + " AND " + " AND ".join(where_clauses)
            self.log.log_to_file(f"Modified query to [\n{new_query}\n] with params: {params}", "apply_filters", "DEBUG")
            return new_query, params
        return base_sql, params

    def modify_search_query(self, query:str, params:list = None, filter_types:list = None):
        new_query, temp_params = self.apply_filters(query.replace(";", ""), filter_types)
        params.extend(temp_params)
        return self.db.fetch_all(new_query, tuple(params))

    def search_results(self, nodes: list, config:list = ["full_ref", "text"]):
        csv_results = [config]

        final_results = []
        result_contexts = {} # Chapter context for verses

        for node_id in nodes:
            for translation_id in self.filter["translations"].keys():
                if self.filter["translations"][translation_id]["active"] == True:
                    new_result = Assembler(manager=self.manager, scope="verse", node_id=node_id, translation_id=translation_id)
                    final_results.append(new_result)

                result_chapter = new_result.get_details("chapter")
                if result_chapter not in result_contexts.keys():
                    result_contexts[result_chapter] = Assembler(manager=self.manager, scope="chapter", node_id=node_id, translation_id=translation_id)
            
            csv_line = []
            for item in config:
                csv_line.append(new_result.get_details(item))

            csv_results.append(csv_line)
        
        complete_results = {
            "csv": csv_results,
            "chapters": result_contexts,
            "verses": final_results
        }

        self.log.log_to_file(f"Search Results: {complete_results}, with config: {config}", "search_results", "DEBUG")

        return complete_results
    
    def search_word(self, word):
        query = self.SQL.get("get_word_nodes")

        nodes_found = self.modify_search_query(query, [f"%{word}%",], ["books", "translations"])

        results = self.search_results(nodes_found)

        self.create_csv_file(f"{word}", results["csv"])

    def search_strongs(self, strong):
        # Find strongs occurences
        nodes_found = self.db.fetch_all(self.SQL.get("get_strong_nodes"), (strong,))

        results = self.search_results(nodes_found, config=["full_ref", "translation", "text"])

        self.create_csv_file(f"{strong}", results["csv"])

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

    def create_csv_file(self, file_name, contents):
        file_folder = Path(__file__).parents[2] / "logs" / "search" / "csv"
        file_path = file_folder / f"{file_name}.tsv"

        try:
            os.makedirs(file_folder)
        except Exception as e:
            pass

        with open(file_path, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerows(contents)

if __name__ == "__main__":
    new_search = Search()
    # new_search.update_filter("translations", 1, False)
    new_search.search_word("fruit")

    # again_search = Search()
    # again_search.search_strongs("H7397")