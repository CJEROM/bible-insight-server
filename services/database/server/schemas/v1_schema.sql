CREATE EXTENSION pgcrypto;
CREATE SCHEMA bible;

-- ================================================== Reference Data ==================================================

CREATE TABLE IF NOT EXISTS bible.users (
    id                  SERIAL PRIMARY KEY,
    sud                 TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS bible.sources (
    id                  SERIAL PRIMARY KEY,
    url                 TEXT UNIQUE,
	note				TEXT,
	metadata			JSONB
);

CREATE TABLE IF NOT EXISTS bible.files (
    id              SERIAL PRIMARY KEY,
    etag            TEXT,
    type            TEXT,
	-- Update to include bucket id for this file
    file_path       TEXT, -- where this would be the file path inside said bucket
    bucket          TEXT, -- this would be ignored
    -- translation_id  INTEGER,
    source_id       INTEGER,
    FOREIGN KEY (source_id) REFERENCES bible.sources (id) ON DELETE SET NULL
);

-- Consider turning into unique instance for controlling bible.styles across all bible.translations instead, like default settings
CREATE TABLE IF NOT EXISTS bible.styles (
    id                  SERIAL PRIMARY KEY,
    style               TEXT,
    name                TEXT,
    description         TEXT,
    versetext           BOOLEAN,
    publishable         BOOLEAN,
    source_file_id      INTEGER,
    FOREIGN KEY (source_file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.properties (
    id                  SERIAL PRIMARY KEY,
    name                TEXT,
    value               TEXT,
    unit                TEXT,
    style_id            INTEGER,
    FOREIGN KEY (style_id) REFERENCES bible.styles (id) ON DELETE CASCADE
);

-- ================================================== Translation ==================================================

CREATE TABLE IF NOT EXISTS bible.languages (
    id                  SERIAL PRIMARY KEY,
    iso                 TEXT UNIQUE,
    name                TEXT,
    nameLocal           TEXT,
    scriptDirection     TEXT
);

CREATE TABLE IF NOT EXISTS bible.dblagreements (
    id                  INTEGER PRIMARY KEY,
	copyright           TEXT,
    promotion           TEXT,
    active              TIMESTAMP,
    expiry              TIMESTAMP,
    enabled             BOOLEAN
);

CREATE TABLE IF NOT EXISTS bible.translationinfo (
    dbl_id              TEXT PRIMARY KEY,
    medium              TEXT,
    name                TEXT,
    nameLocal           TEXT,
    description         TEXT,
    abbreviationLocal   TEXT,
    language_id         INTEGER,
    FOREIGN KEY (language_id) REFERENCES bible.languages (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.dblinfo (
    dbl_id              TEXT,
    agreement_id         INTEGER,
	-- revisions            INTEGER, -- Currently duplicated since its seems dbl_id and agreement_id make unique instance (revision) of a bible translation
	PRIMARY KEY(dbl_id, agreement_id),
    FOREIGN KEY (agreement_id) REFERENCES bible.dblagreements (id) ON DELETE CASCADE
    -- FOREIGN KEY (dbl_id) REFERENCES bible.translationinfo (dbl_id)
);

CREATE TABLE IF NOT EXISTS bible.translations (
    id                  SERIAL PRIMARY KEY,
    dbl_id              TEXT,
    agreement_id        TEXT,
	revision            INTEGER,
	revision_note		TEXT, -- For storing what has changed in the revision
    license_file        INTEGER,
    metadata_file       INTEGER,
    ldml_file           INTEGER,
    versification_file  INTEGER,
    style_file          INTEGER,
	UNIQUE(dbl_id, agreement_id, revision),
	FOREIGN KEY (dbl_id) REFERENCES bible.translationinfo (dbl_id) ON DELETE CASCADE,
    FOREIGN KEY (license_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (metadata_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (ldml_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (versification_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (style_file) REFERENCES bible.files (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bible.translationrelationships (
    id                  SERIAL PRIMARY KEY,
    from_translation    TEXT,
    from_revision       INTEGER,
    to_translation      INTEGER,
    to_revision         INTEGER,
    type                TEXT
    -- FOREIGN KEY (from_translation) REFERENCES bible.translationinfo (dbl_id) ON DELETE CASCADE
    -- FOREIGN KEY (to_translation) REFERENCES bible.translations (dbl_id)
);

-- ================================================== Label Studio Compatible Tables ==================================================

CREATE TABLE IF NOT EXISTS bible.labellingprojects (
    id                  INTEGER PRIMARY KEY,
    exports             INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bible.translationlabellingprojects (
    id                  SERIAL PRIMARY KEY,
    translation_id      INTEGER,
    project_id          INTEGER,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES bible.labellingprojects (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.labellingfiles (
    id                  SERIAL PRIMARY KEY,
    file_id             INTEGER,
    project_id          INTEGER,
    FOREIGN KEY (project_id) REFERENCES bible.labellingprojects (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

-- ================================================== bible.books ==================================================

CREATE TABLE IF NOT EXISTS bible.books (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE,
	total_chapters	INTEGER
);

CREATE TABLE IF NOT EXISTS bible.booktofile (
    id              SERIAL PRIMARY KEY,
    book_code       TEXT,
    translation_id  INTEGER,
    file_id         INTEGER,
    short           TEXT, -- Short Name for the book
    long            TEXT, -- Long Name for the book
    FOREIGN KEY (book_code) REFERENCES bible.books (code) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.bookgroups (
    id              SERIAL PRIMARY KEY,
    testament       BOOLEAN,
    level           INTEGER
);

CREATE TABLE IF NOT EXISTS bible.booktogroup (
    book_id         INTEGER,
    book_group_id   INTEGER,
    PRIMARY KEY (book_id, book_group_id),
    FOREIGN KEY (book_id) REFERENCES bible.books (id) ON DELETE CASCADE,
    FOREIGN KEY (book_group_id) REFERENCES bible.bookgroups (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.bookgroupnames (
    id              SERIAL PRIMARY KEY,
    book_group_id   INTEGER,
    language_id     INTEGER,
    name            TEXT,
    FOREIGN KEY (book_group_id) REFERENCES bible.bookgroups (id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES bible.languages (id) ON DELETE CASCADE
);

-- ================================================== bible.chapters ==================================================

CREATE TABLE IF NOT EXISTS bible.chapters (
    id                      SERIAL PRIMARY KEY,
    book_code               TEXT,
    chapter_num             INTEGER,
    chapter_ref             TEXT UNIQUE,
    standard                BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (book_code) REFERENCES bible.books (code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.chapteroccurences (
    id                      SERIAL PRIMARY KEY,
    chapter_ref             TEXT,
    file_id            		INTEGER,
    book_map_id             INTEGER,
    FOREIGN KEY (chapter_ref) REFERENCES bible.chapters (chapter_ref),
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);

-- ================================================== bible.paragraphs & bible.verses ==================================================

-- Consider Relative link into Chapter bible.occurences, for easier reference

CREATE TABLE IF NOT EXISTS bible.paragraphs (
    id              SERIAL PRIMARY KEY,
    chapter_occ_id  INTEGER,
    style_id        INTEGER,
    parent_para     INTEGER,
    xml             XML,
    versetext       TEXT,
    FOREIGN KEY (parent_para) REFERENCES bible.paragraphs (id) ON DELETE SET NULL,
    FOREIGN KEY (chapter_occ_id) REFERENCES bible.chapteroccurences (id) ON DELETE CASCADE,
    FOREIGN KEY (style_id) REFERENCES bible.styles (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.verses (
    id              SERIAL PRIMARY KEY,
    chapter_ref     TEXT,
    verse_ref       TEXT UNIQUE,
    standard        BOOLEAN DEFAULT TRUE, -- Whether this is standard verse or weird combo verse e.g. GEN 1:1-2
    FOREIGN KEY (chapter_ref) REFERENCES bible.chapters (chapter_ref) ON DELETE CASCADE
);

-- For linking non standard verses to their normal counter parts e.g. GEN 1:1-2 => GEN 1:1, GEN 1:2
CREATE TABLE IF NOT EXISTS bible.verse_correction (
    id                          SERIAL PRIMARY KEY,
    non_standard_verse_ref      TEXT,
    verse_ref                   TEXT,
    FOREIGN KEY (non_standard_verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.verseoccurences (
    id              SERIAL PRIMARY KEY,
    chapter_occ_id  INTEGER,
    verse_ref       TEXT,
    text	       	TEXT,
    xml             TEXT,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (chapter_occ_id) REFERENCES bible.chapteroccurences (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.versesToParagraphs (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    paragraph_id    INTEGER,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (paragraph_id) REFERENCES bible.paragraphs (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.excludedverses (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    translation_id  INTEGER,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE
);

-- ================================================== Cross References & Footnotes ==================================================

CREATE TABLE IF NOT EXISTS bible.translationfootnotes (
    id              SERIAL PRIMARY KEY,
	file_id			INTEGER,
    verse_ref       TEXT,
    xml             XML,
	text			TEXT,
	FOREIGN KEY (file_id) REFERENCES bible.files (id) ON DELETE CASCADE,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.translationrefnotes (
    id              SERIAL PRIMARY KEY,
	file_id			INTEGER,
    from_verse_ref  TEXT,
    to_verse_ref    TEXT,
    xml             XML,
	FOREIGN KEY (file_id) REFERENCES bible.files (id) ON DELETE CASCADE,
    FOREIGN KEY (from_verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (to_verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE
);

-- ================================================== Strongs Components ==================================================

CREATE TABLE IF NOT EXISTS bible.strongs (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE,
    language_id     INTEGER,
	-- Consider either storing bible.strongs Definition or api call to get it?
    FOREIGN KEY (language_id) REFERENCES bible.languages (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.strongsoccurence (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    translation_id  INTEGER,
    text            TEXT,
    xml             TEXT,
    strong_code     TEXT,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (strong_code) REFERENCES bible.strongs (code) ON DELETE CASCADE
);

-- ================================================== Text Based Information ==================================================

CREATE TABLE IF NOT EXISTS bible.occurences (
	id                  SERIAL PRIMARY KEY,
	text				TEXT,
	type				TEXT, -- [quote, enitity, location]
	verse_occ_id	    INTEGER,
	start_char			INTEGER, -- Relative to Verse (for search)
	end_char			INTEGER, -- Relative to Verse (for search)
	paragraph_id		INTEGER,
	FOREIGN KEY (verse_occ_id) REFERENCES bible.verseoccurences (id) ON DELETE CASCADE,
	FOREIGN KEY (paragraph_id) REFERENCES bible.paragraphs (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.quotes (
    id              SERIAL PRIMARY KEY,
    text            TEXT,
    quote_start     INTEGER,
    quote_end       INTEGER,
    parent_quote    INTEGER,
    speaker         TEXT,
    audience        TEXT,
    FOREIGN KEY (quote_start) REFERENCES bible.occurences (id) ON DELETE CASCADE,
    FOREIGN KEY (quote_end) REFERENCES bible.occurences (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_quote) REFERENCES bible.quotes (id) ON DELETE CASCADE
);

-- ================================================== Entities ==================================================

CREATE TABLE IF NOT EXISTS bible.entities (
    id              SERIAL PRIMARY KEY
);

-- This will also count as Entity Names to some degree since we are counting each occurence and mentions of them, but this could have start and end
CREATE TABLE IF NOT EXISTS bible.entityoccurence (
    id              SERIAL PRIMARY KEY,
	entity_id		INTEGER,
	occurence_id	INTEGER,
	FOREIGN KEY (entity_id) REFERENCES bible.entities (id) ON DELETE CASCADE,
	FOREIGN KEY (occurence_id) REFERENCES bible.occurences (id) ON DELETE CASCADE
);

-- Will act as lookup not so much as source of truth, tho it can, and definetly something to work on
CREATE TABLE IF NOT EXISTS bible.relationship_lookup (
    id              SERIAL PRIMARY KEY,
	relationship    TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS bible.relationship_map (
    id              SERIAL PRIMARY KEY,
	relationship    TEXT,
    FOREIGN KEY (relationship) REFERENCES bible.relationship_lookup (relationship) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bible.entityrelationships (
    id              SERIAL PRIMARY KEY,
	from_entity		INTEGER,
	to_entity	    INTEGER,
    relationship    TEXT,
	FOREIGN KEY (from_entity) REFERENCES bible.entities (id) ON DELETE CASCADE,
    FOREIGN KEY (to_entity) REFERENCES bible.entities (id) ON DELETE CASCADE,
	FOREIGN KEY (relationship) REFERENCES bible.relationship_lookup (relationship) ON DELETE CASCADE
);

-- 
-- CREATE VIEW bible.entity_aliases AS
-- SELECT DISTINCT
-- FROM table_name
-- WHERE conditions;

-- ================================================== [] ==================================================

-- Used to store unique list of words used for this bible translation to use as initial list to check against
CREATE TABLE IF NOT EXISTS bible.word_list (
    id          SERIAL PRIMARY KEY,
    text        TEXT NOT NULL UNIQUE,   -- unique word
    lemma_id    INTEGER,                    -- root/lemma (self-reference if needed)
    nlp         BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (lemma_id) REFERENCES bible.word_list (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bible.word_tags (
    id      SERIAL PRIMARY KEY,
    name    TEXT UNIQUE NOT NULL -- e.g. "Person", "Location", "Entity"
);

CREATE TABLE IF NOT EXISTS bible.word_frequencies (
    id              SERIAL PRIMARY KEY,
    word_id         INTEGER NOT NULL,
    translation_id  INTEGER NOT NULL,
    -- tag             TEXT,  -- OPTIONAL: could use a lookup table (Person, Location, etc.)
    FOREIGN KEY (word_id) REFERENCES bible.word_list (id) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE
);

-- Only storing important bible.tokens
CREATE TABLE IF NOT EXISTS bible.tokens (
    id                  SERIAL PRIMARY KEY,
    text                TEXT,
    llema_id            INTEGER,
    paragraph_id        INTEGER,
    verse_ref           TEXT,
    pos                 TEXT,
    tag                 TEXT,
    dep                 TEXT,
    head_token_id       INTEGER,
    trailing_space      BOOLEAN,
    is_alpha            BOOLEAN,
    is_punct            BOOLEAN,
    like_num            BOOLEAN,
    FOREIGN KEY (paragraph_id) REFERENCES bible.paragraphs (id),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (head_token_id) REFERENCES bible.tokens (id)
);

-- ================================================== Spacy Look up Tables ==================================================

CREATE TABLE public.pos_lookup (
    id SERIAL PRIMARY KEY,
    pos_tag VARCHAR(10) NOT NULL UNIQUE,  -- e.g. 'NOUN', 'VERB'
    description TEXT NOT NULL             -- e.g. 'Noun, a person, place, or thing'
);

CREATE TABLE public.tag_lookup (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(10) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE public.dep_lookup (
    id SERIAL PRIMARY KEY,
    dep VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

-- ================================================== User Based Data ==================================================

CREATE TABLE IF NOT EXISTS bible.usernotes (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMP,
    modified_at     TIMESTAMP,
    complete_at     TIMESTAMP,
    title           TEXT,
    content         TEXT,
    tags            TEXT,
	user_id			INTEGER,
	FOREIGN KEY (user_id) REFERENCES bible.users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bible.noterelationships (
    id              SERIAL PRIMARY KEY,
    note_from    	INTEGER,
    note_to         INTEGER, 
	type			TEXT,
    FOREIGN KEY (note_from) REFERENCES bible.usernotes (id),
	FOREIGN KEY (note_to) REFERENCES bible.usernotes (id)
);

CREATE TABLE IF NOT EXISTS bible.userhighlightsanchors (
    id              SERIAL PRIMARY KEY,
    book_map_id     INTEGER,
    verse_occ_id    INTEGER, 
	start_char		INTEGER,
	end_char		INTEGER,
	FOREIGN KEY (verse_occ_id) REFERENCES bible.verseoccurences (id)
);

CREATE TABLE IF NOT EXISTS bible.userhighlights (
    id              SERIAL PRIMARY KEY,
    start_anchor	INTEGER,
    end_anchor      INTEGER,
	color			TEXT,
    FOREIGN KEY (start_anchor) REFERENCES bible.userhighlightsanchors (id) ON DELETE CASCADE,
	FOREIGN KEY (end_anchor) REFERENCES bible.userhighlightsanchors (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.readhistory (
    history_id              SERIAL PRIMARY KEY,
    date_time               TEXT DEFAULT CURRENT_TIMESTAMP,
    book_map_id            INTEGER,
    scripture_reference     TEXT,
	user_id					INTEGER,
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES bible.users (id)
);

-- ================================================== Imported Location Data (OpenBible.info) ==================================================

-- Location data can be more complicate than this, as can treat these as location reference points (waypoints / landmarks)
--		 so will require rendering in context and showing waypoints relative to area being referred to e.g. for territory 

CREATE TABLE IF NOT EXISTS bible.locations (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT UNIQUE,
    friendly_id         TEXT,
    file_id             INTEGER,
    type                TEXT,
    info                JSON
);

-- Refers to linking a location to a particular verse, and creating all the entries for this.
CREATE TABLE IF NOT EXISTS bible.locationoccurence (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT,
    verse_ref           TEXT,
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);

CREATE TABLE IF NOT EXISTS bible.locationrelationships (
    id                  SERIAL PRIMARY KEY,
    from_location       TEXT,
    to_location         TEXT,
    type                TEXT,
    modifier            TEXT,
    info                TEXT,
    FOREIGN KEY (from_location) REFERENCES bible.locations (location_id),
    FOREIGN KEY (to_location) REFERENCES bible.locations (location_id)
);

CREATE TABLE IF NOT EXISTS bible.geosources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT UNIQUE,
    info                JSON
);

CREATE TABLE IF NOT EXISTS bible.locationdatasources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT,
    location_id         TEXT,
    type                TEXT,
    info                JSON,
    FOREIGN KEY (source_id) REFERENCES bible.geosources (source_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);

CREATE TABLE IF NOT EXISTS bible.images (
    id                  SERIAL PRIMARY KEY,
    image_id            TEXT UNIQUE,
    location_id         TEXT,
    file_id             INTEGER,
    info                JSON,
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

CREATE TABLE IF NOT EXISTS bible.locationimages (
    id                  SERIAL PRIMARY KEY,
    image_id            TEXT,
    location_id         TEXT,
    type                TEXT,
    info                JSON,
    FOREIGN KEY (image_id) REFERENCES bible.images (image_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);

-- Not storing it as a file, instead just as entries, due to 
CREATE TABLE IF NOT EXISTS bible.geometries (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT UNIQUE,
    file_id             INTEGER,
    geometries          TEXT,
    source              TEXT,
    surface             TEXT,
    info                JSON,
    FOREIGN KEY (geo_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

CREATE TABLE IF NOT EXISTS bible.locationgeometry (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT,
    location_id         TEXT,
    FOREIGN KEY (geo_id) REFERENCES bible.geometries (geo_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);

-- ================================================== Other Derived Data ==================================================

-- For parts of scripture talking about same period, and how it aligns e.g. Gospels
CREATE TABLE IF NOT EXISTS bible.harmonies (
    id                  SERIAL PRIMARY KEY,
	description			TEXT,
	order_num			INTEGER
);

CREATE TABLE IF NOT EXISTS bible.harmonymapping (
    harmony_id          INTEGER,
	verse_ref			TEXT,
	PRIMARY KEY (harmony_id, verse_ref),
	FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);

-- Order of all bible.verses in the bible, can also skip if concurrent sections are read as normal
CREATE TABLE IF NOT EXISTS bible.chronologyoccurence (
    id                  SERIAL PRIMARY KEY,
	chapter_ref			TEXT,
	verse_ref			TEXT
);

CREATE TABLE IF NOT EXISTS bible.chronology (
    id                  SERIAL PRIMARY KEY,
	prev_occurence		INTEGER,
	FOREIGN KEY (prev_occurence) REFERENCES bible.chronologyoccurence (id)
);