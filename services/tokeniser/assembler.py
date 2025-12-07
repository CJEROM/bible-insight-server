

# Responsible for helping me test token queries and trying to reassemble fragments in a way I might request it from the server

# This object works as a deribative of Tokenisation as tokenisation identifies nodes that are tokenisable, 
#       using that information, we can make use of this object either, to recontruct these up to a certain context (not chapter)
#       and then serve that to the user as a result, as well as information on where it sits.

# The idea is to anchor references to any information by either, verse, chapter, book, translation (the ones that make sense to users)

from manager.managerhandler import ManagerHandler

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
                SELECT start_node, end_node, verse_ref, translation_id, book_map_id
                FROM bible.verseoccurences
                WHERE id = %s
            )
            SELECT n.id, n.node_text, vb.verse_ref, vb.translation_id, vb.book_map_id
            FROM verse_bounds vb
            JOIN bible.nodes n 
                ON n.id BETWEEN vb.start_node AND vb.end_node
                AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_book_tokenisable_nodes": """
            SELECT id, node_text, book_code, translation_id
            FROM bible.nodes n
            WHERE is_tokenisable = TRUE
                AND book_map_id = %s
            ORDER BY id;
        """,
        # Reconstruct from NODE -> ID
        "get_book_for_node_id": """
            SELECT n.id, n.node_text, n.book_map_id
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
            SELECT n.id, n.node_text, cf.chapter_ref, cf.translation_id, cf.book_map_id
            FROM bible.nodes n 
            JOIN chapter_found cf
                ON n.id BETWEEN cf.start_node AND cf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_for_node_id": """
            WITH verse_found AS (
                SELECT id, start_node, end_node, verse_ref, translation_id, book_map_id
                FROM bible.verseoccurences
                WHERE start_node <= %s AND end_node >= %s
                LIMIT 1
            )
            SELECT n.id, n.node_text, vf.verse_ref, vf.translation_id, vf.book_map_id
            FROM bible.nodes n 
            JOIN verse_found vf
                ON n.id BETWEEN vf.start_node AND vf.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        # Reconstruct from NODE -> CANONICAL PATH
        "get_book_for_node_path": """
            SELECT n.id, n.node_text, n.book_map_id
            FROM bible.nodes n
            WHERE n.book_map_id = (
                SELECT book_map_id
                FROM book.nodes
                WHERE canonical_path = %s AND translation_id = %s
            )
            AND n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_chapter_for_node_path": """
            WITH node_found AS (
                SELECT id AS node_id
                FROM bible.nodes 
                WHERE canonical_path = %s AND translation_id = %s
            ),
            chapter_found AS (
                SELECT id, start_node, end_node, chapter_ref, translation_id, book_map_id
                FROM bible.chapteroccurences cf
                JOIN node_found nf
                  ON nf.node_id BETWEEN cf.start_node AND cf.end_node
                LIMIT 1
            )
            SELECT n.id, n.node_text, cf.chapter_ref, cf.translation_id, cf.book_map_id
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
                WHERE canonical_path = %s AND translation_id = %s
            ),
            verse_found AS (
                SELECT id, start_node, end_node, verse_ref, translation_id, book_map_id
                FROM bible.verseoccurences vf
                JOIN node_found nf
                  ON nf.node_id BETWEEN vf.start_node AND vf.end_node
                LIMIT 1
            )
            SELECT n.id, n.node_text, vf.verse_ref, vf.translation_id, vf.book_map_id
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
                SELECT start_node, end_node, chapter_ref, translation_id, book_map_id
                FROM bible.chapteroccurences
                WHERE chapter_ref = %s AND translation_id = %s
            )
            SELECT n.id, n.node_text, cb.chapter_ref, cb.translation_id, cb.book_map_id
            FROM chapter_bounds cb
            JOIN bible.nodes n 
                ON n.id BETWEEN cb.start_node AND cb.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
        """,
        "get_verse_from_ref": """
            WITH verse_bounds AS (
                SELECT start_node, end_node, verse_ref, translation_id, book_map_id
                FROM bible.verseoccurences
                WHERE verse_ref = %s AND translation_id = %s
            )
            SELECT n.id, n.node_text, vb.verse_ref, vb.translation_id, vb.book_map_id
            FROM verse_bounds vb
            JOIN bible.nodes n 
                ON n.id BETWEEN vb.start_node AND vb.end_node
            WHERE n.is_tokenisable = TRUE
            ORDER BY n.id;
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
            SELECT book_code, translation_id, short
            FROM bible.booktofile
            WHERE id = %s
        """,
    }

    def __init__(self, occurence_id=None, node_id=None, canonical_path=None, ref=None, scope=None, translation_id=None):
        self.occurence_id = occurence_id
        self.node_id = node_id
        self.canonical_path = canonical_path
        self.ref = ref
        self.scope = scope

        self.translation_id = translation_id

        self.manager = ManagerHandler()
        self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        self.db = self.manager.get_db()
        self.log = self.manager.create_log("assembler")
        self.log.set_logging_level(2)

        self.nodes = [] # Represents all (tokenisable) nodes used to reconstruct context
        self.text = ""

        self.assembler_type = None

        self.assemble()

    def get_nodes(self):
        return self.nodes
    
    def get_reconstructed_text(self):
        return self.text
    
    def get_translation_id(self):
        return self.translation_id
    
    def get_occurence_id(self):
        return (self.scope, self.occurence_id)
    
    def get_node_id(self):
        return self.node_id
    
    def get_canonical_path(self):
        return (self.canonical_path)
    
    def get_scope(self):
        return self.scope
    
    def get_assembler_type(self):
        return self.assembler_type
    
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
                # raise ValueError("Insufficient parameters provided for reconstruction.")
        elif self.ref != None:
            self.log.log_to_file("Assembling through Ref", "ASSEMBLER", "INFO")
            self.reconstruct_from_ref(self.translation_id, self.ref)
            self.assembler_type = "ref"
        else:
            self.log.log_to_file("Assembling failed! Insufficient parameters provided for reconstruction. No Scope or Ref Defined!", "ASSEMBLER", "ERROR")
            # raise ValueError("Insufficient parameters provided for reconstruction.")
        
        # Log the resulted reconstruction - if it was successful (no error flagged)
        self.log.log_to_file(f"Reconstruction: [\n{self.text}\n]", "OCCURENCE", "DEBUG")
    
    def reconstruct_occurence(self, scope, occurence_id):
        query = ""
        match scope:
            case "book":
                query = self.SQL.get("get_book_tokenisable_nodes")
            case "chapter":
                query = self.SQL.get("get_chapter_tokenisable_nodes")
            case "verse":
                query = self.SQL.get("get_verse_tokenisable_nodes")

        tokenisable_nodes_results = self.db.fetch_all(query, (occurence_id,))
        self.log.log_to_file(f"Tokens for Reconstruction: {tokenisable_nodes_results}", "OCCURENCE", "DEBUG")
        for node in tokenisable_nodes_results:
            node_id = node[0]
            node_text = node [1]
            self.nodes.append(node_id)
            self.text += node_text

    def reconstruct_from_node_id(self, scope, node_id):
        query = ""
        match scope:
            case "book":
                query = self.SQL.get("get_book_for_node_id")
                self.db.execute(query, (node_id,))
            case "chapter":
                query = self.SQL.get("get_chapter_for_node_id")
                self.db.execute(query, (node_id,node_id))
            case "verse":
                query = self.SQL.get("get_verse_for_node_id")
                self.db.execute(query, (node_id,node_id))
        
        tokenisable_nodes_results = self.db.get_cursor().fetchall()
        self.log.log_to_file(f"Tokens for Reconstruction: {tokenisable_nodes_results}", "NODE_ID", "DEBUG")
        for node in tokenisable_nodes_results:
            node_id = node[0]
            node_text = node [1]
            self.nodes.append(node_id)
            self.text += node_text

    def reconstruct_from_node_path(self, scope, translation_id, canonical_path):
        query = ""
        match scope:
            case "book":
                query = self.SQL.get("get_book_for_node_path")
            case "chapter":
                query = self.SQL.get("get_chapter_for_node_path")
            case "verse":
                query = self.SQL.get("get_verse_for_node_path")

        tokenisable_nodes_results = self.db.fetch_all(query, (canonical_path,translation_id))
        self.log.log_to_file(f"Tokens for Reconstruction: {tokenisable_nodes_results}", "CANONICAL_PATH", "DEBUG")
        for node in tokenisable_nodes_results:
            node_id = node[0]
            node_text = node [1]
            self.nodes.append(node_id)
            self.text += node_text

    def reconstruct_from_ref(self, translation_id, ref):
        # Find if GEN, GEN 1, GEN 1:1 => Based on that change query
        scope = None
        if len(ref.split(" ")) == 1: # No space so book
            scope = "book"
        elif len(ref.split(":")) == 1: # no verse so chapter
            scope = "chapter"
        else:
            scope = "verse"

        query = ""
        match scope:
            case "book":
                query = self.SQL.get("get_book_from_ref")
            case "chapter":
                query = self.SQL.get("get_chapter_from_ref")
            case "verse":
                query = self.SQL.get("get_verse_from_ref")

        tokenisable_nodes_results = self.db.fetch_all(query, (ref, translation_id))
        self.log.log_to_file(f"Tokens for Reconstruction: f{tokenisable_nodes_results}", "REF", "DEBUG")
        for node in tokenisable_nodes_results:
            node_id = node[0]
            node_text = node [1]
            self.nodes.append(node_id)
            self.text += node_text
    
    # Perhaps function to help build on nodes, to display strongs if available?

if __name__ == "__main__":
    chapter = Assembler(scope="chapter", occurence_id=1)
    print(chapter.get_nodes())
    print(chapter.get_reconstructed_text())