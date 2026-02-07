from pathlib import Path

# They should take in a dbManager

# type hints have to be implemented e.g. id: int or tuple[int, int, str]

# Validation to be added in places where it is important

# Current prioirity is dealing with the ingestor, the assembler and search are 
#       more so prototypes that exist to test usability of my data, as well as
#       tryting to experiment with the output shape of my data

# ==================================================================================================================================================================

# strongsingestor.py (to be depraecated)
"create_strongs": """
    INSERT INTO bible.lexemes (source, strongs_code, language_id, lemma, raw_pos, transliteration, pronunciation, raw_gloss, native_word) VALUES %s
""",
"create_strongs_relation": """
    INSERT INTO bible.lexeme_relations (from_lexeme, to_lexeme, relation_type) VALUES %s
""",
"check_lexemes": """
    SELECT id FROM bible.lexemes WHERE strongs_code IS NOT NULL LIMIT 1
"""

language_id = self.db.fetch_clean_one("""
    SELECT id FROM language.languages WHERE name LIKE 'Hebrew%'
""")

language_id = self.db.fetch_clean_one("""
    SELECT id FROM language.languages WHERE name LIKE 'Greek%'
""")

self.db.bulk_insert(self.SQL.get("create_strongs"), self.strongs_data)

self.db.bulk_insert(self.SQL.get("create_strongs_relation"), self.strongs_relations)

# ==================================================================================================================================================================

# labelmanager.py
loaded_db_projects = self.db.fetch_all("""
    SELECT tlp.project_id, tlp.translation_id, lp.name, lp.description
    FROM nlp.translationlabellingprojects tlp
    JOIN nlp.labellingprojects lp ON tlp.project_id = lp.id;
""")

self.db.execute("""
    INSERT INTO nlp.labellingprojects (id, name, description) 
    VALUES (%s, %s, %s)
    RETURNING id;
""", (
    traslation_project_id,
    project_name,
    project_description
))

self.db.execute("""
    INSERT INTO nlp.translationlabellingprojects (translation_id, project_id) 
    VALUES (%s, %s)
    RETURNING id;
""", (
    translation_id,
    traslation_project_id
))

# objectmanager.py
file_object_name, file_bucket = self.db.fetch_one("""
    SELECT file_path AS object_name, bucket FROM audit.files WHERE id = %s
""", (file_id,))

# assembler.py

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

result = self.db.fetch_one(self.SQL.get("get_translation_name"), (self.details.get("translation"),))

book_details    = self.db.fetch_one(self.SQL.get("get_book_details"), (book_map_id,))

self.db.bulk_insert(self.SQL.get("update_node_offsets"), temp_offsets)

self.db.execute(self.SQL.get("update_chapter_occurence_text"), (self.text, self.details.get("chapter")))

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_book_tokenisable_nodes"), 
    (book_map_id,)
)

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_chapter_tokenisable_nodes"), 
    (occurence_id,)
)

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_verse_tokenisable_nodes"), 
    (occurence_id,)
)

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_book_for_node_id"), 
    (node_id,)
)

self.details["node_path"]   = self.db.fetch_clean_one(self.SQL.get("get_canonical_path_for_node"), (node_id,))

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_chapter_for_node_id"), 
    (node_id, node_id)
)

self.details["node_path"]   = self.db.fetch_clean_one(self.SQL.get("get_canonical_path_for_node"), (node_id,))

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_verse_for_node_id"), 
    (node_id, node_id)
)

self.details["node_path"]   = self.db.fetch_clean_one(self.SQL.get("get_canonical_path_for_node"), (node_id,))

self.details["node_path"]   = self.db.fetch_clean_one(self.SQL.get("get_canonical_path_for_node"), (node_id,))

self.details["node"]        = self.db.fetch_clean_one(self.SQL.get("get_node_id_for_canonical_path"), (canonical_path, translation_id))

self.details["node"]        = self.db.fetch_clean_one(self.SQL.get("get_node_id_for_canonical_path"), (canonical_path, translation_id))

self.details["node"]        = self.db.fetch_clean_one(self.SQL.get("get_node_id_for_canonical_path"), (canonical_path, translation_id))

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_verse_for_node_path"), 
    (canonical_path, translation_id)
)

self.details["node"]        = self.db.fetch_clean_one(self.SQL.get("get_node_id_for_canonical_path"), (canonical_path, translation_id))

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_book_from_ref"), 
    (ref, translation_id)
)

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_chapter_from_ref"), 
    (ref, translation_id)
)

verse_ref = self.db.fetch_clean_one(self.SQL.get("get_matched_verse_ref"), (ref, translation_id, translation_id))

valid_nodes = self.db.fetch_all(
    self.SQL.get("get_verse_from_ref"), 
    (verse_ref, translation_id)
)

file_id = self.db.fetch_clean_one("""
    SELECT file_id FROM bible.booktofile WHERE id = %s;
""", (book_map_id,))

# strongs.py
"get_unique_strong_text": """
    SELECT
        p.id        AS strong_node_id,
        c.id        AS text_node_id,
        c.node_text AS text
    FROM bible.nodes p
    JOIN bible.nodes c
        ON c.parent_node_id = p.id
    WHERE p.strong = %s
    AND p.translation_id = %s
    AND c.node_text IS NOT NULL
    AND c.node_text <> ''
    ORDER BY p.id ASC;
""",
"get_strong_data": """
    SELECT id, source, source_version, strongs_code, language_id, lemma, raw_pos, transliteration, pronunciation, audio_file, raw_gloss FROM bible.lexemes WHERE strongs_code = %s
""",
"get_strongs_to_relation": """
    SELECT 
        lr.to_lexeme, 
        l.strongs_code,
        l.native_word,
        l.lemma,
        l.raw_pos,
        l.transliteration,
        l.pronunciation,
        l.raw_gloss
    FROM bible.lexemes l
    JOIN bible.lexeme_relations lr ON l.id = lr.to_lexeme
    WHERE lr.from_lexeme = %s
""",
"get_strongs_from_relation": """
    SELECT 
        lr.from_lexeme, 
        l.strongs_code,
        l.native_word,
        l.lemma,
        l.raw_pos,
        l.transliteration,
        l.pronunciation,
        l.raw_gloss
    FROM bible.lexemes l
    JOIN bible.lexeme_relations lr ON l.id = lr.from_lexeme
    WHERE lr.to_lexeme = %s
""",

all_occurences = self.db.fetch_all(self.SQL.get("get_unique_strong_text"), (self.strong, self.translation_id))

info = self.db.fetch_one(self.SQL.get("get_strong_data"), (self.strong,))

to_relations = self.db.fetch_all(self.SQL.get("get_strongs_to_relation"), (lexeme_id,))

from_relations = self.db.fetch_all(self.SQL.get("get_strongs_from_relation"), (lexeme_id,))

# tokenisation.py



self.language_id = self.db.fetch_clean_one(self.SQL.get("get_language"), (self.translation_id,))

all_books = self.db.fetch_all(self.SQL.get("get_translation_books"), (self.translation_id,))

all_chapters = self.db.fetch_all(self.SQL.get("get_book_chapters"), (book_map_id,))

all_books = self.db.fetch_all(self.SQL.get("get_translation_books"), (self.translation_id,))

token_id_offset = self.db.fetch_clean_one(self.SQL.get("max_token_count"))

all_chapters = self.db.fetch_all(self.SQL.get("get_book_chapters"), (book_map_id,))

self.db.set_chunks(20000)  # ideal for execute_values

self.db.bulk_insert(self.SQL.get("create_pos_lookup"), unique_pos)
self.db.bulk_insert(self.SQL.get("create_tag_lookup"), unique_tag)
self.db.bulk_insert(self.SQL.get("create_dep_lookup"), unique_dep)

self.db.bulk_insert(self.SQL.get("create_token"), all_new_tokens)

# search.py
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

languages       = self.db.fetch_all(self.SQL.get("get_languages"))

translations    = self.db.fetch_all(self.SQL.get("get_translations"))

books           = self.db.fetch_all(self.SQL.get("get_distinct_books"))

existing_books = self.db.fetch_all_single(self.SQL.get("get_translation_books"), (translation_id,))

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

nodes_found = self.db.fetch_all(self.SQL.get("get_strong_nodes"), (strong,))