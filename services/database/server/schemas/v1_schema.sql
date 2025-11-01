CREATE EXTENSION pgcrypto;
CREATE SCHEMA bible;
SET search_path TO bible;

-- ================================================== Reference Data ==================================================

-- DROP TABLE IF EXISTS bible.users;
CREATE TABLE IF NOT EXISTS bible.users (
    id                  SERIAL PRIMARY KEY,
    sud                 TEXT UNIQUE
);

-- DROP TABLE IF EXISTS bible.sources;
CREATE TABLE IF NOT EXISTS bible.sources (
    id                  SERIAL PRIMARY KEY,
    url                 TEXT UNIQUE,
	note				TEXT,
	metadata			JSONB
);

-- DROP TABLE IF EXISTS bible.files;
CREATE TABLE IF NOT EXISTS bible.files (
    id              SERIAL PRIMARY KEY,
    etag            TEXT,
    type            TEXT,
	-- Update to include bucket id for this file
    file_path       TEXT, -- where this would be the file path inside said bucket
    bucket          TEXT, -- this would be ignored
    -- translation_id  INT,
    source_id       INT,
    FOREIGN KEY (source_id) REFERENCES bible.sources (id)  
);

-- Consider turning into unique instance for controlling bible.styles across all bible.translations instead, like default settings
-- DROP TABLE IF EXISTS bible.styles;
CREATE TABLE IF NOT EXISTS bible.styles (
    id                  SERIAL PRIMARY KEY,
    style               TEXT,
    name                TEXT,
    description         TEXT,
    versetext           BOOLEAN,
    publishable         BOOLEAN,
    source_file_id      INT,
    FOREIGN KEY (source_file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);

-- DROP TABLE IF EXISTS bible.properties;
CREATE TABLE IF NOT EXISTS bible.properties (
    id                  SERIAL PRIMARY KEY,
    name                TEXT,
    value               TEXT,
    unit                TEXT,
    style_id            INT,
    FOREIGN KEY (style_id) REFERENCES bible.styles (id)
);

-- ================================================== Translation ==================================================

-- DROP TABLE IF EXISTS bible.languages;
CREATE TABLE IF NOT EXISTS bible.languages (
    id                  SERIAL PRIMARY KEY,
    iso                 TEXT UNIQUE,
    name                TEXT,
    nameLocal           TEXT,
    scriptDirection     TEXT
);

-- DROP TABLE IF EXISTS bible.dblagreements;
CREATE TABLE IF NOT EXISTS bible.dblagreements (
    id                  INT PRIMARY KEY,
	copyright           TEXT,
    promotion           TEXT,
    active              TIMESTAMP,
    expiry              TIMESTAMP,
    enabled             BOOLEAN
);

-- DROP TABLE IF EXISTS bible.translationinfo;
CREATE TABLE IF NOT EXISTS bible.translationinfo (
    dbl_id              TEXT PRIMARY KEY,
    medium              TEXT,
    name                TEXT,
    nameLocal           TEXT,
    description         TEXT,
    abbreviationLocal   TEXT,
    language_id         INT,
    FOREIGN KEY (language_id) REFERENCES bible.languages (id)
);

-- DROP TABLE IF EXISTS bible.dblinfo;
CREATE TABLE IF NOT EXISTS bible.dblinfo (
    dbl_id              TEXT,
    agreement_id         INT,
	-- revisions            INT, -- Currently duplicated since its seems dbl_id and agreement_id make unique instance (revision) of a bible translation
	PRIMARY KEY(dbl_id, agreement_id),
    FOREIGN KEY (agreement_id) REFERENCES bible.dblagreements (id)
    -- FOREIGN KEY (dbl_id) REFERENCES bible.translationinfo (dbl_id)
);

-- DROP TABLE IF EXISTS bible.translations;
CREATE TABLE IF NOT EXISTS bible.translations (
    id                  SERIAL PRIMARY KEY,
    dbl_id              TEXT,
    agreement_id        TEXT,
	revision            INT,
	revision_note		TEXT, -- For storing what has changed in the revision
    license_file        INT,
    metadata_file       INT,
    ldml_file           INT,
    versification_file  INT,
    style_file          INT,
	UNIQUE(dbl_id, agreement_id, revision),
	FOREIGN KEY (dbl_id) REFERENCES bible.translationinfo (dbl_id),
    FOREIGN KEY (license_file) REFERENCES bible.files (id),
    FOREIGN KEY (metadata_file) REFERENCES bible.files (id),
    FOREIGN KEY (ldml_file) REFERENCES bible.files (id),
    FOREIGN KEY (versification_file) REFERENCES bible.files (id),
    FOREIGN KEY (style_file) REFERENCES bible.files (id)
);

-- DROP TABLE IF EXISTS bible.translationrelationships;
CREATE TABLE IF NOT EXISTS bible.translationrelationships (
    id                  SERIAL PRIMARY KEY,
    from_translation    TEXT,
    from_revision       INT,
    to_translation      INT,
    to_revision         INT,
    type                TEXT,
    FOREIGN KEY (from_translation) REFERENCES bible.translationinfo (dbl_id) ON DELETE CASCADE
    -- FOREIGN KEY (to_translation) REFERENCES bible.translations (dbl_id)
);

-- ================================================== Label Studio Compatible Tables ==================================================

-- DROP TABLE IF EXISTS bible.labellingprojects;
CREATE TABLE IF NOT EXISTS bible.labellingprojects (
    id                  INT PRIMARY KEY,
    label_config        XML
);

-- DROP TABLE IF EXISTS bible.translationlabellingprojects;
CREATE TABLE IF NOT EXISTS bible.translationlabellingprojects (
    id                  SERIAL PRIMARY KEY,
    translation_id      INT,
    project_id          INT,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id),
    FOREIGN KEY (project_id) REFERENCES bible.labelingprojects (id)
);


-- DROP TABLE IF EXISTS bible.labellingprojects;
CREATE TABLE IF NOT EXISTS bible.labellingfiles (
    id                  SERIAL PRIMARY KEY,
    file_id             INT,
    project_id          INT,
    FOREIGN KEY (project_id) REFERENCES bible.labellingprojects (id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

-- ================================================== bible.books ==================================================

-- DROP TABLE IF EXISTS bible.books;
CREATE TABLE IF NOT EXISTS bible.books (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE,
	total_chapters	INT
);

-- DROP TABLE IF EXISTS bible.booktofile;
CREATE TABLE IF NOT EXISTS bible.booktofile (
    id              SERIAL PRIMARY KEY,
    book_code       TEXT,
    translation_id  INT,
    file_id         INT,
    short           TEXT, -- Short Name for the book
    long            TEXT, -- Long Name for the book
    FOREIGN KEY (book_code) REFERENCES bible.books (code),
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);

-- DROP TABLE IF EXISTS bible.bookgroups;
CREATE TABLE IF NOT EXISTS bible.bookgroups (
    id              SERIAL PRIMARY KEY,
    testament       BOOLEAN,
    level           INT
);

-- DROP TABLE IF EXISTS bible.booktogroup;
CREATE TABLE IF NOT EXISTS bible.booktogroup (
    book_id         INT,
    book_group_id   INT,
    PRIMARY KEY (book_id, book_group_id),
    FOREIGN KEY (book_id) REFERENCES bible.books (id),
    FOREIGN KEY (book_group_id) REFERENCES bible.bookgroups (id)
);

-- DROP TABLE IF EXISTS bible.bookgroupnames;
CREATE TABLE IF NOT EXISTS bible.bookgroupnames (
    id              SERIAL PRIMARY KEY,
    book_group_id   INT,
    language_id     INT,
    name            TEXT,
    FOREIGN KEY (book_group_id) REFERENCES bible.bookgroups (id),
    FOREIGN KEY (language_id) REFERENCES bible.languages (id)
);

-- ================================================== bible.chapters ==================================================

-- DROP TABLE IF EXISTS bible.chapters;
CREATE TABLE IF NOT EXISTS bible.chapters (
    id                      SERIAL PRIMARY KEY,
    book_code               TEXT,
    chapter_num             INT,
    chapter_ref             TEXT UNIQUE,
    standard                BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (book_code) REFERENCES bible.books (code)
);

-- DROP TABLE IF EXISTS bible.chapteroccurences;
CREATE TABLE IF NOT EXISTS bible.chapteroccurences (
    id                      SERIAL PRIMARY KEY,
    chapter_ref             TEXT,
    file_id            		INT,
    book_map_id             INT,
    FOREIGN KEY (chapter_ref) REFERENCES bible.chapters (chapter_ref),
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);

-- ================================================== bible.paragraphs & bible.verses ==================================================

-- Consider Relative link into Chapter bible.occurences, for easier reference

-- DROP TABLE IF EXISTS bible.paragraphs;
CREATE TABLE IF NOT EXISTS bible.paragraphs (
    id              SERIAL PRIMARY KEY,
    chapter_occ_id  INTEGER,
    style_id        INTEGER,
    parent_para     INTEGER,
    xml             XML,
    versetext       TEXT,
    FOREIGN KEY (parent_para) REFERENCES bible.paragraphs (id),
    FOREIGN KEY (chapter_occ_id) REFERENCES bible.chapteroccurences (id),
    FOREIGN KEY (style_id) REFERENCES bible.styles (id)
);

-- DROP TABLE IF EXISTS bible.verses;
CREATE TABLE IF NOT EXISTS bible.verses (
    id              SERIAL PRIMARY KEY,
    chapter_ref     TEXT,
    verse_ref       TEXT UNIQUE,
    standard        BOOLEAN DEFAULT TRUE, -- Whether this is standard verse or weird combo verse e.g. GEN 1:1-2
    FOREIGN KEY (chapter_ref) REFERENCES bible.chapters (chapter_ref)
);

-- For linking non standard verses to their normal counter parts e.g. GEN 1:1-2 => GEN 1:1, GEN 1:2
CREATE TABLE IF NOT EXISTS bible.verses (
    id                          SERIAL PRIMARY KEY,
    non_standard_verse_ref      TEXT,
    verse_ref                   TEXT,
    FOREIGN KEY (non_standard_verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);

-- DROP TABLE IF EXISTS bible.verseoccurences;
CREATE TABLE IF NOT EXISTS bible.verseoccurences (
    id              SERIAL PRIMARY KEY,
    chapter_occ_id  INT,
    verse_ref       TEXT,
    text	       	TEXT,
    xml             TEXT,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (chapter_occ_id) REFERENCES bible.chapteroccurences (id)
);

-- DROP TABLE IF EXISTS bible.versesToParagraphs;
CREATE TABLE IF NOT EXISTS bible.versesToParagraphs (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    paragraph_id    INTEGER,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (paragraph_id) REFERENCES bible.paragraphs (id)
);

-- DROP TABLE IF EXISTS bible.excludedverses;
CREATE TABLE IF NOT EXISTS bible.excludedverses (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    translation_id  INT,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE
);

-- ================================================== Cross References & Footnotes ==================================================

-- DROP TABLE IF EXISTS bible.translationfootnotes;
CREATE TABLE IF NOT EXISTS bible.translationfootnotes (
    id              SERIAL PRIMARY KEY,
	file_id			INT,
    verse_ref       TEXT,
    xml             XML,
	text			TEXT,
	FOREIGN KEY (file_id) REFERENCES bible.files (id),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);

-- DROP TABLE IF EXISTS bible.translationrefnotes;
CREATE TABLE IF NOT EXISTS bible.translationrefnotes (
    id              SERIAL PRIMARY KEY,
	file_id			INT,
    from_verse_ref  TEXT,
    to_verse_start  TEXT,
    to_verse_end    TEXT,
    xml             XML,
	FOREIGN KEY (file_id) REFERENCES bible.files (id),
    FOREIGN KEY (from_verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (to_verse_start) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (to_verse_end) REFERENCES bible.verses (verse_ref)
);

-- ================================================== Linked Components ==================================================

-- DROP TABLE IF EXISTS bible.strongs;
CREATE TABLE IF NOT EXISTS bible.strongs (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE,
    language_id     INT,
	-- Consider either storing bible.strongs Definition or api call to get it?
    FOREIGN KEY (language_id) REFERENCES bible.languages (id)
);

-- DROP TABLE IF EXISTS bible.strongsoccurence;
CREATE TABLE IF NOT EXISTS bible.strongsoccurence (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    translation_id  INT,
    text            TEXT,
    xml             TEXT,
    strong_code     TEXT,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (strong_code) REFERENCES bible.strongs (code)
);

-- DROP TABLE IF EXISTS bible.entities;
CREATE TABLE IF NOT EXISTS bible.entities (
    id              SERIAL PRIMARY KEY
);

-- ================================================== Text Based Information ==================================================

-- DROP TABLE IF EXISTS bible.occurences;
CREATE TABLE IF NOT EXISTS bible.occurences (
	id                  SERIAL PRIMARY KEY,
	text				TEXT,
	type				TEXT, -- [quote, enitity, location]
	verse_occ_id	    INT,
	start_char			INT, -- Relative to Verse (for search)
	end_char			INT, -- Relative to Verse (for search)
	paragraph_id		INT,
	FOREIGN KEY (verse_occ_id) REFERENCES bible.verseoccurences (id),
	FOREIGN KEY (paragraph_id) REFERENCES bible.paragraphs (id)
);

-- DROP TABLE IF EXISTS bible.quotes;
CREATE TABLE IF NOT EXISTS bible.quotes (
    id              SERIAL PRIMARY KEY,
    text            TEXT,
    quote_start     INT,
    quote_end       INT,
    parent_quote    INT,
    speaker         TEXT,
    audience        TEXT,
    FOREIGN KEY (quote_start) REFERENCES bible.occurences (id),
    FOREIGN KEY (quote_end) REFERENCES bible.occurences (id),
    FOREIGN KEY (parent_quote) REFERENCES bible.quotes (id)
);

-- This will also count as Entity Names to some degree since we are counting each occurence and mentions of them, but this could have start and end
-- DROP TABLE IF EXISTS bible.entityoccurence;
CREATE TABLE IF NOT EXISTS bible.entityoccurence (
    id              SERIAL PRIMARY KEY,
	entity_id		INT,
	occurence_id	INT,
	FOREIGN KEY (entity_id) REFERENCES bible.entities (id),
	FOREIGN KEY (occurence_id) REFERENCES bible.occurences (id)
);

-- ================================================== [] ==================================================

CREATE TABLE pos_lookup (
    id SERIAL PRIMARY KEY,
    pos_tag VARCHAR(10) NOT NULL UNIQUE,  -- e.g. 'NOUN', 'VERB'
    description TEXT NOT NULL             -- e.g. 'Noun, a person, place, or thing'
);

CREATE TABLE tag_lookup (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(10) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE dep_lookup (
    id SERIAL PRIMARY KEY,
    dep VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

-- Only storing important bible.tokens
-- DROP TABLE IF EXISTS bible.tokens;
CREATE TABLE IF NOT EXISTS bible.tokens (
    id                  SERIAL PRIMARY KEY,
    text                TEXT,
    llema_id            INTEGER,
    paragraph_id        INT,
    verse_ref           TEXT,
    pos                 TEXT,
    tag                 TEXT,
    dep                 TEXT,
    head_token_id       INT,
    trailing_space      BOOLEAN,
    is_alpha            BOOLEAN,
    is_punct            BOOLEAN,
    like_num            BOOLEAN,
    FOREIGN KEY (paragraph_id) REFERENCES bible.paragraphs (id),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref),
    FOREIGN KEY (head_token_id) REFERENCES bible.tokens (id)
);


-- ================================================== User Based Data ==================================================

-- DROP TABLE IF EXISTS bible.usernotes;
CREATE TABLE IF NOT EXISTS bible.usernotes (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMP,
    modified_at     TIMESTAMP,
    complete_at     TIMESTAMP,
    title           TEXT,
    content         TEXT,
    tags            TEXT,
	user_id			INT,
	FOREIGN KEY (user_id) REFERENCES bible.users (id)
);

-- DROP TABLE IF EXISTS bible.noterelationships;
CREATE TABLE IF NOT EXISTS bible.noterelationships (
    id              SERIAL PRIMARY KEY,
    note_from    	INT,
    note_to         INT, 
	type			TEXT,
    FOREIGN KEY (note_from) REFERENCES bible.usernotes (id),
	FOREIGN KEY (note_to) REFERENCES bible.usernotes (id)
);

-- DROP TABLE IF EXISTS bible.userhighlightsanchors;
CREATE TABLE IF NOT EXISTS bible.userhighlightsanchors (
    id              SERIAL PRIMARY KEY,
    book_map_id     INT,
    verse_occ_id    INT, 
	start_char		INT,
	end_char		INT,
	FOREIGN KEY (verse_occ_id) REFERENCES bible.verseoccurences (id)
);

-- DROP TABLE IF EXISTS bible.userhighlights;
CREATE TABLE IF NOT EXISTS bible.userhighlights (
    id              SERIAL PRIMARY KEY,
    start_anchor	INT,
    end_anchor      INT,
	color			TEXT,
    FOREIGN KEY (start_anchor) REFERENCES bible.userhighlightsanchors (id) ON DELETE CASCADE,
	FOREIGN KEY (end_anchor) REFERENCES bible.userhighlightsanchors (id) ON DELETE CASCADE
);

-- DROP TABLE IF EXISTS bible.readhistory;
CREATE TABLE IF NOT EXISTS bible.readhistory (
    history_id              SERIAL PRIMARY KEY,
    date_time               TEXT DEFAULT CURRENT_TIMESTAMP,
    book_map_id            INT,
    scripture_reference     TEXT,
	user_id					INT,
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES bible.users (id)
);

-- ================================================== Imported Location Data (OpenBible.info) ==================================================

-- Location data can be more complicate than this, as can treat these as location reference points (waypoints / landmarks)
--		 so will require rendering in context and showing waypoints relative to area being referred to e.g. for territory 

-- DROP TABLE IF EXISTS bible.locations;
CREATE TABLE IF NOT EXISTS bible.locations (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT UNIQUE,
    friendly_id         TEXT,
    file_id             INT,
    type                TEXT,
    info                JSON
);

-- Refers to linking a location to a particular verse, and creating all the entries for this.
-- DROP TABLE IF EXISTS bible.locationoccurence;
CREATE TABLE IF NOT EXISTS bible.locationoccurence (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT,
    verse_ref           TEXT,
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);

-- DROP TABLE IF EXISTS bible.locationrelationships;
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

-- DROP TABLE IF EXISTS bible.geosources;
CREATE TABLE IF NOT EXISTS bible.geosources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT UNIQUE,
    info                JSON
);

-- DROP TABLE IF EXISTS bible.locationdatasources;
CREATE TABLE IF NOT EXISTS bible.locationdatasources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT,
    location_id         TEXT,
    type                TEXT,
    info                JSON,
    FOREIGN KEY (source_id) REFERENCES bible.geosources (source_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);

-- DROP TABLE IF EXISTS bible.images;
CREATE TABLE IF NOT EXISTS bible.images (
    id                  SERIAL PRIMARY KEY,
    image_id            TEXT UNIQUE,
    location_id         TEXT,
    file_id             INT,
    info                JSON,
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

-- DROP TABLE IF EXISTS bible.locationimages;
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
-- DROP TABLE IF EXISTS bible.geometries;
CREATE TABLE IF NOT EXISTS bible.geometries (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT UNIQUE,
    file_id             INT,
    geometries          TEXT,
    source              TEXT,
    surface             TEXT,
    info                JSON,
    FOREIGN KEY (geo_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

-- DROP TABLE IF EXISTS bible.locationgeometry;
CREATE TABLE IF NOT EXISTS bible.locationgeometry (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT,
    location_id         TEXT,
    FOREIGN KEY (geo_id) REFERENCES bible.geometries (geo_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);

-- ================================================== Other Derived Data ==================================================

-- For parts of scripture talking about same period, and how it aligns e.g. Gospels
-- DROP TABLE IF EXISTS bible.harmonies;
CREATE TABLE IF NOT EXISTS bible.harmonies (
    id                  SERIAL PRIMARY KEY,
	description			TEXT,
	order_num			INT
);

-- DROP TABLE IF EXISTS bible.harmonymapping;
CREATE TABLE IF NOT EXISTS bible.harmonymapping (
    harmony_id          INT,
	verse_ref			TEXT,
	PRIMARY KEY (harmony_id, verse_ref),
	FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);

-- Order of all bible.verses in the bible, can also skip if concurrent sections are read as normal
-- DROP TABLE IF EXISTS bible.chronologyoccurence;
CREATE TABLE IF NOT EXISTS bible.chronologyoccurence (
    id                  SERIAL PRIMARY KEY,
	chapter_ref			TEXT,
	verse_ref			TEXT
);

-- DROP TABLE IF EXISTS bible.chronology;
CREATE TABLE IF NOT EXISTS bible.chronology (
    id                  SERIAL PRIMARY KEY,
	prev_occurence		INT,
	FOREIGN KEY (prev_occurence) REFERENCES bible.chronologyoccurence (id)
);