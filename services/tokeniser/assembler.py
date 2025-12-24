import traceback
import re
from bs4 import BeautifulSoup

# Responsible for helping me test token queries and trying to reassemble fragments in a way I might request it from the server

# This object works as a deribative of Tokenisation as tokenisation identifies nodes that are tokenisable, 
#       using that information, we can make use of this object either, to recontruct these up to a certain context (not chapter)
#       and then serve that to the user as a result, as well as information on where it sits.

# The idea is to anchor references to any information by either, verse, chapter, book, translation (the ones that make sense to users)

# This class should be discardable after creation, it won't be changed after its been initialised, you only access the data within instead

from manager.managerhandler import ManagerHandler

VERSE   = "verse"
CHAPTER = "chapter"
BOOK    = "book"

class Assembler:
    SQL = {
        # Reconstruct from OCCURENCE -> ID
        "get_chapter_tokenisable_nodes": """
            WITH chapter_bounds AS (
                SELECT start_node, end_node, chapter_ref, translation_id, book_map_id
                FROM bible.chapteroccurences
                WHERE id = %s
            )
            SELECT n.id, n.node_text, cb.chapter_ref, cb.translation_id, cb.book_map_id
            FROM chapter_bounds cb
            JOIN bible.nodes n 
                ON n.id BETWEEN cb.start_node AND cb.end_node
                AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_tokenisable_nodes": """
            WITH verse_bounds AS (
                SELECT start_node, end_node, verse_ref, translation_id, book_map_id, chapter_id
                FROM bible.verseoccurences
                WHERE id = %s
            )
            SELECT n.id, n.node_text, vb.verse_ref, vb.translation_id, vb.book_map_id, vb.chapter_id
            FROM verse_bounds vb
            JOIN bible.nodes n 
                ON n.id BETWEEN vb.start_node AND vb.end_node
                AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_book_tokenisable_nodes": """
            SELECT id, node_text, translation_id, book_code
            FROM bible.nodes n
            WHERE is_tokenisable = TRUE
                AND book_map_id = %s
            ORDER BY id;
        """,
        # Reconstruct from NODE -> ID
        "get_book_for_node_id": """
            SELECT n.id, n.node_text, n.translation_id, n.book_map_id
            FROM bible.nodes n
            WHERE n.book_map_id = (
                SELECT book_map_id
                FROM book.nodes
                WHERE id = %s
            )
            AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_chapter_for_node_id": """
            WITH chapter_found AS (
                SELECT id, start_node, end_node, chapter_ref, translation_id, book_map_id
                FROM bible.chapteroccurences
                WHERE start_node <= %s AND end_node >= %s
                LIMIT 1
            )
            SELECT n.id, n.node_text, cf.chapter_ref, cf.translation_id, cf.book_map_id, cf.id
            FROM bible.nodes n 
            JOIN chapter_found cf
                ON n.id BETWEEN cf.start_node AND cf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_for_node_id": """
            WITH verse_found AS (
                SELECT id, start_node, end_node, verse_ref, translation_id, book_map_id, chapter_id
                FROM bible.verseoccurences
                WHERE start_node <= %s AND end_node >= %s
                LIMIT 1
            )
            SELECT n.id, n.node_text, vf.verse_ref, vf.translation_id, vf.book_map_id, vf.chapter_id, vf.id
            FROM bible.nodes n 
            JOIN verse_found vf
                ON n.id BETWEEN vf.start_node AND vf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        # Reconstruct from NODE -> CANONICAL PATH
        "get_book_for_node_path": """
            SELECT n.id, n.node_text, n.translation_id, n.book_map_id
            FROM bible.nodes n
            WHERE n.book_map_id = (
                SELECT book_map_id
                FROM book.nodes
                WHERE canonical_path LIKE %s AND translation_id = %s
            )
            AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_chapter_for_node_path": """
            WITH node_found AS (
                SELECT id AS node_id
                FROM bible.nodes 
                WHERE canonical_path LIKE %s AND translation_id = %s
            ),
            chapter_found AS (
                SELECT id, start_node, end_node, chapter_ref, book_map_id
                FROM bible.chapteroccurences cf
                JOIN node_found nf
                  ON nf.node_id BETWEEN cf.start_node AND cf.end_node
                LIMIT 1
            )
            SELECT n.id, n.node_text, cf.chapter_ref, cf.book_map_id, cf.id
            FROM bible.nodes n 
            JOIN chapter_found cf
                ON n.id BETWEEN cf.start_node AND cf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_for_node_path": """
            WITH node_found AS (
                SELECT id AS node_id
                FROM bible.nodes 
                WHERE canonical_path LIKE %s AND translation_id = %s
            ),
            verse_found AS (
                SELECT id, start_node, end_node, verse_ref, book_map_id, chapter_id
                FROM bible.verseoccurences vf
                JOIN node_found nf
                  ON nf.node_id BETWEEN vf.start_node AND vf.end_node
                LIMIT 1
            )
            SELECT n.id, n.node_text, vf.verse_ref, vf.book_map_id, vf.chapter_id, vf.id
            FROM bible.nodes n 
            JOIN verse_found vf
                ON n.id BETWEEN vf.start_node AND vf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        # Reconstruct from REF
        "get_book_from_ref": """
            SELECT id, node_text, book_map_id
            FROM bible.nodes
            WHERE book_map_id = (
                SELECT id 
                FROM book.booktofile
                WHERE book_code = %s AND translation_id = %s
            )
            AND is_tokenisable = TRUE
            ORDER BY id;
        """,
        "get_chapter_from_ref": """
            WITH chapter_bounds AS (
                SELECT id, start_node, end_node, book_map_id
                FROM bible.chapteroccurences
                WHERE chapter_ref = %s AND translation_id = %s
            )
            SELECT n.id, n.node_text, cb.book_map_id, cb.id
            FROM chapter_bounds cb
            JOIN bible.nodes n 
                ON n.id BETWEEN cb.start_node AND cb.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_from_ref": """
            WITH verse_bounds AS (
                SELECT id, start_node, end_node, book_map_id, chapter_id
                FROM bible.verseoccurences
                WHERE verse_ref = %s AND translation_id = %s
            )
            SELECT n.id, n.node_text, vb.book_map_id, vb.chapter_id, vb.id
            FROM verse_bounds vb
            JOIN bible.nodes n 
                ON n.id BETWEEN vb.start_node AND vb.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_matched_verse_ref": """
            WITH input_ref AS (
                SELECT %s AS ref
            ),

            -- 1. Check if canonical verse exists e.g. GEN 3:1
            direct_match AS (
                SELECT vo.verse_ref
                FROM bible.verseoccurences vo
                JOIN input_ref i ON vo.verse_ref = i.ref
                WHERE vo.translation_id = %s
            ),

            -- 2. If not, find non-standard refs that map *to* the input canonical ref e.g. if exists GEN 3:1-2
            fallback_match AS (
                SELECT vc.non_standard_verse_ref AS verse_ref
                FROM bible.verse_correction vc
                JOIN bible.verseoccurences vo 
                    ON vo.verse_ref = vc.non_standard_verse_ref
                JOIN input_ref i ON vc.verse_ref = i.ref
                WHERE vo.translation_id = %s
            )

            -- 3. Prefer direct match; if none, return fallback
            SELECT verse_ref
            FROM direct_match

            UNION ALL

            SELECT verse_ref
            FROM fallback_match
            LIMIT 1;  -- return first match only              
        """,
        # NOT IN USE YET
        "get_ref_all_verseoccurences": """
            SELECT * 
            FROM bible.verseoccurences
            WHERE verse_ref = %s
        """,
        "get_ref_all_chapteroccurences": """
            SELECT * 
            FROM bible.chapteroccurences
            WHERE chapter_ref = %s
        """,
        # Get Book Details 
        "get_book_details": """
            SELECT book_code, short
            FROM bible.booktofile
            WHERE id = %s
        """,
        "get_canonical_path_for_node": """
            SELECT canonical_path
            FROM bible.nodes
            WHERE id = %s
        """,
        "get_node_id_for_canonical_path": """
            SELECT id
            FROM bible.nodes
            WHERE canonical_path = %s AND translation_id = %s
        """,
        # Helper Update Queries
        "update_node_offsets": """
            UPDATE bible.nodes 
            SET chapter_start_offset = %s, chapter_end_offset = %s
            WHERE id = %s;
        """,
        "update_chapter_occurence_text": """
            UPDATE bible.chapteroccurences 
            SET reconstructed_text = %s
            WHERE id = %s;
        """,
        # Base Classes that are extended
        "get_strongs_in_range": """
            SELECT DISTINCT strong
            FROM bible.nodes
            WHERE strong IS NOT NULL
        """,
        # Helper Classes
        "get_translation_name": """
            SELECT name, abbreviationLocal
            FROM bible.translations
            WHERE id = %s
        """,
    }

    def __init__(
            self, 
            manager: ManagerHandler = None, 
            occurence_id=None, node_id=None, canonical_path=None, ref=None, scope=None, translation_id=None, 
            is_nlp=False
        ):

        self.occurence_id   = occurence_id
        self.node_id        = node_id
        self.canonical_path = canonical_path
        self.ref            = ref
        self.scope          = scope

        self.translation_id = translation_id

        self.is_nlp         = is_nlp

        self.manager = manager
        if manager == None:
            self.manager = ManagerHandler()
            self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        self.db = self.manager.get_db()
        self.log = self.manager.create_log_in_folder(["logs", "assembler"], "assembler")
        self.log.set_logging_level(2)
        self.obj = self.manager.get_obj()

        self.nodes  = [] # Represents all (tokenisable) nodes used to reconstruct context
        self.text   = ""

        self.assembler_type = None

        self.valid_object = True
        # Commented out details init, so that only return what is relevant (no empty details returned on request)
        # ---> Kept type for better user feedback on Assembly failure
        self.details = {
            "type": "UNKNOWN",            # What type of assembly
            # "scope": None,              # Scope it tried to reconstruct BOOK, CHAPTER, VERSE
            # "nodes": None,              # Tokenisable Nodes used in reconstruction
            # "text": None,               # Reconstructed Text from Tokenisable Nodes

            # "ref": None,                # Ref for scope e.g. GEN, GEN 1, GEN 1:1
            # "full_ref": None,           # Full Ref e.g. Genesis, Genesis 1, Genesis 1:1
            # "translation": None,        # Translation this came from

            # "book": None,               # bible.booktofil -> book_map_id 
            # "chapter": None,            # bible.chapteroccurences -> id
            # "verse": None,              # bible.verseoccurences -> id

            # "node": None,               # bible.nodes -> id
            # "node_path": None           # bible.nodes -> canonical_path

            # "xml": None,                # Get from book_xml file
            # "strongs": None,            # bible.nodes -> strongs (unique set in range)
        }

        try:
            self.assemble()
        except Exception as e:
            self.log.log_to_file("No Tokenisable Nodes for assembly suspected!", "ASSEMBLER", "WARN")

            error_message = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            self.log.log_to_file(error_message, "ASSEMBLER", "ERROR")

            self.details["type"] = "ERROR"

        if self.details == {'type': 'INVALID'} or self.details == {'type': 'ERROR'}:
            self.valid_object = False

    def __eq__(self, other):
        return (
            isinstance(other, Assembler)
            and self.get_details("ref") != None
            and self.get_details("translation") != None
            and self.get_details("ref") == other.get_details("ref")
            and self.get_details("translation") == other.get_details("translation")
        )

    def __hash__(self):
        return hash((self.get_details("ref"), self.get_details("translation").get("id")))
    
    def get_details(self, detail=None):
        return self.details.get(detail)
            
    def get_parent_context(self):
        if self.valid_object:
            cur_ref = self.details.get("ref")
            if not cur_ref: return None # if we can't access ref from details, don't create parent

            local_verse = cur_ref.split("-")[0]
            local_chapter = local_verse.split(":")[0]
            local_book = local_chapter.split(" ")[0]

            if self.scope == "chapter":
                return Assembler(manager=self.manager, ref=local_book, translation_id=self.details.get("translation"))
            elif self.scope == "verse":
                return Assembler(manager=self.manager, ref=local_chapter, translation_id=self.details.get("translation"))

        return None
            
    def set_full_reference(self, book_map_id, is_book=False):
        book_details    = self.db.fetch_one(self.SQL.get("get_book_details"), (book_map_id,))
        book_code       = book_details[0]
        book_name       = book_details[1]

        if is_book:
            self.details["ref"] = book_code

        self.details["full_ref"] = book_name
    
    def assemble(self):
        # Attempt to automatically determine what reconstruction method to use
        if self.scope != None:
            if self.occurence_id != None:
                self.log.log_to_file("Assembling through Occurence", "ASSEMBLER", "INFO")
                self.reconstruct_occurence(self.scope, self.occurence_id)
                self.assembler_type = "occurence"
            elif self.node_id != None:
                self.log.log_to_file("Assembling from Node ID", "ASSEMBLER", "INFO")
                self.reconstruct_from_node_id(self.scope, self.node_id)
                self.assembler_type = "node_id"
            elif self.canonical_path != None and self.translation_id != None:
                self.log.log_to_file("Assembling through Node Canonical Path", "ASSEMBLER", "INFO")
                self.reconstruct_from_node_path(self.scope, self.translation_id, self.canonical_path)
                self.assembler_type = "canonical_path"
            else:
                self.log.log_to_file("Assembling failed! Insufficient parameters provided for reconstruction. Scope Defined, but no occurence, node_id or canonical_path!", "ASSEMBLER", "ERROR")
                self.details["type"]    = "INVALID"
                # raise ValueError("Insufficient parameters provided for reconstruction.")
        elif self.ref != None and self.translation_id != None:
            self.log.log_to_file("Assembling through Ref", "ASSEMBLER", "INFO")
            self.reconstruct_from_ref(self.translation_id, self.ref)
            self.assembler_type = "ref"
        else:
            self.log.log_to_file("Assembling failed! Insufficient parameters provided for reconstruction. No Scope or Ref Defined!", "ASSEMBLER", "ERROR")
            self.details["type"]    = "INVALID"
            # raise ValueError("Insufficient parameters provided for reconstruction.")

        if self.details.get("type") == "UNKNOWN": # Check if something forced value early
            self.details["type"]    = self.assembler_type
        self.details["scope"]   = self.scope
        self.details["text"]    = self.text
        self.details["nodes"]   = self.nodes

        result = self.db.fetch_one(self.SQL.get("get_translation_name"), (self.details.get("translation"),))

        self.details["translation"] = {
            "name": result[0],
            "id": self.details.get("translation"),
            "abbreviation": result[1]
        }
        
        # Log the resulted reconstruction - if it was successful (no error flagged)
        self.log.log_to_file(f"Reconstruction: [\n{self.text}\n]", "OCCURENCE", "DEBUG")

    def assemble_text(self, source: str, tokenisable_nodes: list, update_offsets:bool = False):
        self.log.log_to_file(f"Tokens for Reconstruction: f{tokenisable_nodes}", source, "DEBUG")

        temp_offsets = []

        for node in tokenisable_nodes:
            node_id = node[0]
            node_text = node[1]
            self.nodes.append(node_id)

            start = len(self.text)
            self.text += node_text
            end = len(self.text)

            temp_offsets.append((start, end, node_id))

        if update_offsets:
            # Update start, end offsets for node
            self.db.bulk_insert(self.SQL.get("update_node_offsets"), temp_offsets)

            if self.details.get("scope") == "chapter":
                self.db.execute(self.SQL.get("update_chapter_occurence_text"), (self.text, self.details.get("chapter")))
    
    def reconstruct_occurence(self, scope, occurence_id):
        valid_nodes = None
        match scope:
            case "book":
                book_map_id = occurence_id
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_book_tokenisable_nodes"), 
                    (book_map_id,)
                )
                sample_node = valid_nodes[0]

                translation_id      = sample_node[2]
                book_code           = sample_node[3]
                
                self.details["ref"]         = book_code
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id

                self.set_full_reference(book_map_id)
                        
            case "chapter":
                chapter_occurence_id = occurence_id
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_chapter_tokenisable_nodes"), 
                    (occurence_id,)
                )
                sample_node = valid_nodes[0]

                chapter_ref         = sample_node[2]
                translation_id      = sample_node[3]
                book_map_id         = sample_node[4]
                
                self.details["ref"]         = chapter_ref
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + chapter_ref.split(" ")[1]

            case "verse":
                verse_occurence_id = occurence_id
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_verse_tokenisable_nodes"), 
                    (occurence_id,)
                )
                sample_node = valid_nodes[0]

                verse_ref           = sample_node[2]
                translation_id      = sample_node[3]
                book_map_id         = sample_node[4]
                chapter_occurence_id= sample_node[5]
                
                self.details["ref"]         = verse_ref
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id
                self.details["verse"]       = verse_occurence_id

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + verse_ref.split(" ")[1]
        
        self.assemble_text("OCCURENCE", valid_nodes, self.is_nlp)

    def reconstruct_from_node_id(self, scope, node_id):
        valid_nodes = None
        match scope:
            case "book":
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_book_for_node_id"), 
                    (node_id,)
                )
                sample_node = valid_nodes[0]

                translation_id      = sample_node[2]
                book_map_id         = sample_node[3]
                
                self.details["translation"] = translation_id
                
                self.details["book"]        = book_map_id

                self.details["node"]        = node_id
                self.details["node_path"]   = self.db.fetch_clean_one(self.SQL.get("get_canonical_path_for_node"), (node_id,))

                self.set_full_reference(book_map_id, True)

            case "chapter":
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_chapter_for_node_id"), 
                    (node_id, node_id)
                )
                sample_node = valid_nodes[0]

                chapter_ref         = sample_node[2]
                translation_id      = sample_node[3]
                book_map_id         = sample_node[4]
                chapter_occurence_id= sample_node[5]

                self.details["ref"]         = chapter_ref
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id

                self.details["node"]        = node_id
                self.details["node_path"]   = self.db.fetch_clean_one(self.SQL.get("get_canonical_path_for_node"), (node_id,))

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + chapter_ref.split(" ")[1]

            case "verse":
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_verse_for_node_id"), 
                    (node_id, node_id)
                )
                sample_node = valid_nodes[0]

                verse_ref           = sample_node[2]
                translation_id      = sample_node[3]
                book_map_id         = sample_node[4]
                chapter_occurence_id= sample_node[5]
                verse_occurence_id  = sample_node[6]
                
                self.details["ref"]         = verse_ref
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id
                self.details["verse"]       = verse_occurence_id

                self.details["node"]        = node_id
                self.details["node_path"]   = self.db.fetch_clean_one(self.SQL.get("get_canonical_path_for_node"), (node_id,))

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + verse_ref.split(" ")[1]

        self.assemble_text("NODE_ID", valid_nodes, self.is_nlp)

    def reconstruct_from_node_path(self, scope, translation_id, canonical_path):
        valid_nodes = None
        match scope:
            case "book":
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_book_for_node_path"), 
                    (canonical_path, translation_id)
                )
                sample_node = valid_nodes[0]

                translation_id      = sample_node[2]
                book_map_id         = sample_node[3]
                
                self.details["translation"] = translation_id
                
                self.details["book"]        = book_map_id

                self.details["node"]        = self.db.fetch_clean_one(self.SQL.get("get_node_id_for_canonical_path"), (canonical_path, translation_id))
                self.details["node_path"]   = canonical_path

                self.set_full_reference(book_map_id, True)
                
            case "chapter":
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_chapter_for_node_path"), 
                    (canonical_path, translation_id)
                )
                sample_node = valid_nodes[0]

                chapter_ref         = sample_node[2]
                book_map_id         = sample_node[3]
                chapter_occurence_id= sample_node[4]

                self.details["ref"]         = chapter_ref
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id

                self.details["node"]        = self.db.fetch_clean_one(self.SQL.get("get_node_id_for_canonical_path"), (canonical_path, translation_id))
                self.details["node_path"]   = canonical_path

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + chapter_ref.split(" ")[1]

            case "verse":
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_verse_for_node_path"), 
                    (canonical_path, translation_id)
                )
                sample_node = valid_nodes[0]

                verse_ref           = sample_node[2]
                book_map_id         = sample_node[3]
                chapter_occurence_id= sample_node[4]
                verse_occurence_id  = sample_node[5]

                self.details["ref"]         = verse_ref
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id
                self.details["verse"]       = verse_occurence_id

                self.details["node"]        = self.db.fetch_clean_one(self.SQL.get("get_node_id_for_canonical_path"), (canonical_path, translation_id))
                self.details["node_path"]   = canonical_path

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + verse_ref.split(" ")[1]

        self.assemble_text("CANONICAL_PATH", valid_nodes, self.is_nlp)

    def reconstruct_from_ref(self, translation_id, ref:str):
        # Find if GEN, GEN 1, GEN 1:1 => Based on that change query
        scope = None
        if len(ref.split(" ")) == 1: # No space so book
            scope = "book"
        elif len(ref.split(":")) == 1: # no verse so chapter
            scope = "chapter"
        else:
            scope = "verse"
        self.scope = scope

        valid_nodes = None
        match scope:
            case "book":
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_book_from_ref"), 
                    (ref, translation_id)
                )
                sample_node = valid_nodes[0]

                book_map_id         = sample_node[2]
                
                self.details["translation"] = translation_id
                self.details["book"]        = book_map_id

                self.set_full_reference(book_map_id, True)

            case "chapter":
                chapter_ref = ref
                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_chapter_from_ref"), 
                    (ref, translation_id)
                )
                sample_node = valid_nodes[0]

                book_map_id         = sample_node[2]
                chapter_occurence_id= sample_node[3]

                self.details["ref"]         = chapter_ref
                
                self.details["translation"] = translation_id
                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + chapter_ref.split(" ")[1]
                
            case "verse":
                verse_ref = self.db.fetch_clean_one(self.SQL.get("get_matched_verse_ref"), (ref, translation_id, translation_id))

                valid_nodes = self.db.fetch_all(
                    self.SQL.get("get_verse_from_ref"), 
                    (verse_ref, translation_id)
                )

                sample_node = valid_nodes[0]

                book_map_id         = sample_node[2]
                chapter_occurence_id= sample_node[3]
                verse_occurence_id  = sample_node[4]

                self.details["ref"]         = verse_ref
                self.details["translation"] = translation_id

                self.details["book"]        = book_map_id
                self.details["chapter"]     = chapter_occurence_id
                self.details["verse"]       = verse_occurence_id

                self.set_full_reference(book_map_id)
                self.details["full_ref"] += " " + verse_ref.split(" ")[1]

        self.assemble_text("REF", valid_nodes, self.is_nlp)
    
    def add_detail(self):
        if self.valid_object and self.details != {'type': 'UNKNOWN'}:
            self.set_xml()
            self.get_strongs()

            self.get_entities()
            self.get_llema()
            self.get_quotes()
            self.get_cross_refs()
            self.get_foot_notes()
            self.get_user_notes()

    def get_file_id(self):
        if self.valid_object:
            book_map_id = self.details["book"]
            file_id = self.db.fetch_clean_one("""
                SELECT file_id FROM bible.booktofile WHERE id = %s;
            """, (book_map_id,))
            self.details["file"] = file_id
            return file_id

    # Perhaps function to help build on nodes, to display strongs if available?
    def set_xml(self):
        book_xml = BeautifulSoup(self.obj.stream_file_from_file_id(self.get_file_id()), "xml")

        ref_text = None

        if self.scope != "book":
            ref = self.details["ref"]

            start_tag = book_xml.find(self.scope, sid=ref)
            end_tag = book_xml.find(self.scope, eid=ref)

            search_string = f"{start_tag}.*{end_tag}"
            ref_found = re.search(search_string, str(book_xml), re.DOTALL)

            # In case of WLC for example, Malachi 4 doesn't exist, so skip over chapter
            #       if it doesn't exist for this book.
            # Should also account for upper range increased due to non standard chapters (skip over them)
            if ref_found == None:
                self.log.log_to_file(f"{ref} XML Not Found...", f"XML", "DEBUG")
                return

            # Have to add encapsulating tags, since otherwise only first chapter tag, 
            #       will be included when parsed as xml, ignoring the rest of the text
            ref_text = """<usx version="3.0">\n"""

            if self.scope == "verse":
                closing = ""
                for node in start_tag.parents:
                    closing += f"\n</{node.name}>"
                    ref_text += f"{start_tag.parent}\n"
                    if node.name == "para" or node.name == "table":
                        break
                    else: 
                        ref_text += start_tag.parent 

                ref_text += ref_found.group(0)

                ref_text += closing

            else:
                ref_text += ref_found.group(0)
            ref_text += "\n</usx>"
        else: 
            ref_text = book_xml

        if ref_text != None:
            self.details["xml"] = ref_text

    def get_strongs(self):
        soup = BeautifulSoup(self.get_details("xml"), "xml")

        # Get all nodes with a 'strong' attribute
        nodes = soup.find_all(attrs={"strong": True})

        # Extract their strong values
        strong_values = [node.get("strong") for node in nodes]

        # Make them unique
        unique_strongs = set(strong_values)

        if len(unique_strongs) > 0:
            self.details["strongs"] = list(unique_strongs)
    
    def get_entities(self):
        pass
    
    def get_llema(self):
        pass
    
    def get_quotes(self):
        pass
    
    def get_cross_refs(self):
        # All cross reference in and out
        pass
    
    def get_foot_notes(self):
        # Only for this translation
        pass
    
    def get_user_notes(self):
        pass

# Used for TESTING
if __name__ == "__main__":
    test_translation = 1
    test_occurence = 1
    test_node_id = 22
    test_node_path = "/usx:0/para:13/verse:1"
    test_scope = "verse"
    # test_scope = "chapter"
    # test_scope = "verse"

    # ======= OCCURENCE =======
    # REQUIRED: scope, occurence_id
    # temp = Assembler(scope=test_scope, occurence_id=test_occurence) # GEN
    # print(temp.get_details())

    # # ======= NODE ID =======
    # # REQUIRED: scope, node_id
    # temp = Assembler(scope=test_scope, node_id=test_node_id) # GEN
    # print(temp.get_details())

    # # ======= NODE PATH =======
    # # REQUIRED: scope, canonical_path, translation_id
    # temp = Assembler(scope=test_scope, canonical_path=test_node_path, translation_id=test_translation)
    # print(temp.get_details())

    # ======= REF =======
    # REQUIRED: ref, translation_id
    test_book       = "GEN"
    test_chapter    = 1
    test_verse      = 1
    test_ref        = ""
    match test_scope:
        case "book":
            test_ref = test_book
        case "chapter":
            test_ref = f"{test_book} {test_chapter}"
        case "verse":
            test_ref = f"{test_book} {test_chapter}:{test_verse}"

    print(test_ref)

    temp = Assembler(ref=test_ref, translation_id=test_translation)
    
    print(temp.get_details())
    # print(temp.get_parent_context().get_details())
    temp.add_detail()
    print(temp.get_details())