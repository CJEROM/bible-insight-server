CREATE EXTENSION pgcrypto;
CREATE SCHEMA bible;
SET search_path TO bible;

-- ================================================== Reference Data ==================================================

-- DROP TABLE IF EXISTS Users;
CREATE TABLE IF NOT EXISTS Users (
    id                  SERIAL PRIMARY KEY,
    sud                 TEXT UNIQUE
);

-- DROP TABLE IF EXISTS Sources;
CREATE TABLE IF NOT EXISTS Sources (
    id                  SERIAL PRIMARY KEY,
    url                 TEXT,
	note				TEXT,
	metadata			JSONB
);

-- DROP TABLE IF EXISTS Files;
CREATE TABLE IF NOT EXISTS Files (
    id              SERIAL PRIMARY KEY,
    etag            TEXT,
    type            TEXT,
	-- Update to include bucket id for this file
    file_path       TEXT, -- where this would be the file path inside said bucket
    bucket          TEXT, -- this would be ignored
    translation_id  INT,
    source_id       INT,
    FOREIGN KEY (source_id) REFERENCES Sources (id)  
);

-- Consider turning into unique instance for controlling styles across all translations instead, like default settings
-- DROP TABLE IF EXISTS Styles;
CREATE TABLE IF NOT EXISTS Styles (
    id                  SERIAL PRIMARY KEY,
    style               TEXT,
    name                TEXT,
    description         TEXT,
    versetext           BOOLEAN,
    publishable         BOOLEAN,
    source_file_id      INT,
    FOREIGN KEY (source_file_id) REFERENCES Files (id) ON DELETE CASCADE
);

-- DROP TABLE IF EXISTS Properties;
CREATE TABLE IF NOT EXISTS Properties (
    id                  SERIAL PRIMARY KEY,
    name                TEXT,
    value               TEXT,
    unit                TEXT,
    style_id            INT,
    FOREIGN KEY (style_id) REFERENCES Styles(id)
);

-- ================================================== Translation ==================================================

-- DROP TABLE IF EXISTS Languages;
CREATE TABLE IF NOT EXISTS Languages (
    id                  SERIAL PRIMARY KEY,
    iso                 TEXT UNIQUE,
    name                TEXT,
    nameLocal           TEXT,
    scriptDirection     TEXT
);

-- DROP TABLE IF EXISTS DBLAgreements;
CREATE TABLE IF NOT EXISTS DBLAgreements (
    id                  INT PRIMARY KEY,
	copyright           TEXT,
    promotion           TEXT,
    active              TIMESTAMP,
    expiry              TIMESTAMP,
    enabled             BOOLEAN
);

-- DROP TABLE IF EXISTS TranslationInfo;
CREATE TABLE IF NOT EXISTS TranslationInfo (
    dbl_id              TEXT PRIMARY KEY,
    medium              TEXT,
    name                TEXT,
    nameLocal           TEXT,
    description         TEXT,
    abbreviationLocal   TEXT,
    language_id         INT,
    FOREIGN KEY (language_id) REFERENCES Languages (id)
);

-- DROP TABLE IF EXISTS DBLInfo;
CREATE TABLE IF NOT EXISTS DBLInfo (
    dbl_id              TEXT,
    agreement_id         INT,
	revisions            INT,
	PRIMARY KEY(dbl_id, agreement_id),
    FOREIGN KEY (agreement_id) REFERENCES DBLAgreements (id)
    -- FOREIGN KEY (dbl_id) REFERENCES TranslationInfo (dbl_id)
);

-- DROP TABLE IF EXISTS Translations;
CREATE TABLE IF NOT EXISTS Translations (
    id                  SERIAL PRIMARY KEY,
    dbl_id              TEXT,
    agreement_id        TEXT,
	revision            INT,
	revision_note		TEXT, -- For storing what has changed in the revision
    license_file        INT,
    metadata_file       INT,
    ldml_file           INT,
    versification_file  INT,
	UNIQUE(dbl_id, agreement_id, revision),
	FOREIGN KEY (dbl_id) REFERENCES TranslationInfo (dbl_id),
    FOREIGN KEY (license_file) REFERENCES Files (id),
    FOREIGN KEY (metadata_file) REFERENCES Files (id),
    FOREIGN KEY (ldml_file) REFERENCES Files (id),
    FOREIGN KEY (versification_file) REFERENCES Files (id)
);

-- DROP TABLE IF EXISTS TranslationRelationships;
CREATE TABLE IF NOT EXISTS TranslationRelationships (
    id                  SERIAL PRIMARY KEY,
    from_translation    TEXT,
    from_revision       INT,
    to_translation      INT,
    to_revision         INT,
    type                TEXT,
    FOREIGN KEY (from_translation) REFERENCES TranslationInfo (dbl_id) ON DELETE CASCADE
    -- FOREIGN KEY (to_translation) REFERENCES Translations (dbl_id)
);

-- ================================================== Books ==================================================

-- DROP TABLE IF EXISTS Books;
CREATE TABLE IF NOT EXISTS Books (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE,
	total_chapters	INT
);

-- DROP TABLE IF EXISTS BookToFile;
CREATE TABLE IF NOT EXISTS BookToFile (
    id              SERIAL PRIMARY KEY,
    book_code       TEXT,
    translation_id  INT,
    file_id         INT,
    short           TEXT, -- Short Name for the book
    long            TEXT, -- Long Name for the book
    FOREIGN KEY (book_code) REFERENCES Books (code),
    FOREIGN KEY (translation_id) REFERENCES Translations (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES Files (id) ON DELETE CASCADE
);

-- DROP TABLE IF EXISTS BookGroups;
CREATE TABLE IF NOT EXISTS BookGroups (
    id              SERIAL PRIMARY KEY,
    testament       BOOLEAN,
    level           INT
);

-- DROP TABLE IF EXISTS BookToGroup;
CREATE TABLE IF NOT EXISTS BookToGroup (
    book_id         INT,
    book_group_id   INT,
    PRIMARY KEY (book_id, book_group_id),
    FOREIGN KEY (book_id) REFERENCES Books (id),
    FOREIGN KEY (book_group_id) REFERENCES BookGroups (id)
);

-- DROP TABLE IF EXISTS BookGroupNames;
CREATE TABLE IF NOT EXISTS BookGroupNames (
    id              SERIAL PRIMARY KEY,
    book_group_id   INT,
    language_id     INT,
    name            TEXT,
    FOREIGN KEY (book_group_id) REFERENCES BookGroups (id),
    FOREIGN KEY (language_id) REFERENCES Languages (id)
);

-- ================================================== Chapters ==================================================

-- DROP TABLE IF EXISTS Chapters;
CREATE TABLE IF NOT EXISTS Chapters (
    id                      SERIAL PRIMARY KEY,
    book_code               TEXT,
    chapter_num             INT,
    chapter_ref             TEXT UNIQUE,
    FOREIGN KEY (book_code) REFERENCES Books(code)
);

-- DROP TABLE IF EXISTS ChapterOccurences;
CREATE TABLE IF NOT EXISTS ChapterOccurences (
    chapter_ref             TEXT,
    file_id            		INT,
	PRIMARY KEY (chapter_ref, file_id),
    FOREIGN KEY (chapter_ref) REFERENCES Chapters (chapter_ref),
    FOREIGN KEY (file_id) REFERENCES Files (id) ON DELETE CASCADE
);

-- ================================================== Paragraphs & Verses ==================================================

-- Consider Relative link into Chapter Occurences, for easier reference

-- DROP TABLE IF EXISTS Paragraphs;
CREATE TABLE IF NOT EXISTS Paragraphs (
    id              SERIAL PRIMARY KEY,
    book_file_id    INT,
    chapter_id      INTEGER,
    style_id        INTEGER,
    parent_para     INTEGER,
    xml             XML,
    versetext       TEXT,
    FOREIGN KEY (parent_para) REFERENCES Paragraphs (id),
    FOREIGN KEY (book_file_id) REFERENCES Files (id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES Chapters (id),
    FOREIGN KEY (style_id) REFERENCES Styles(id)
);

-- DROP TABLE IF EXISTS Verses;
CREATE TABLE IF NOT EXISTS Verses (
    id              SERIAL PRIMARY KEY,
    chapter_ref     TEXT,
    verse_ref       TEXT UNIQUE,
    FOREIGN KEY (chapter_ref) REFERENCES Chapters (chapter_ref)
);

-- DROP TABLE IF EXISTS VerseOccurences;
CREATE TABLE IF NOT EXISTS VerseOccurences (
    verse_ref       TEXT,
    book_file_id    INT,
    text	       	TEXT,
	PRIMARY KEY (verse_ref, book_file_id),
    FOREIGN KEY (verse_ref) REFERENCES Verses (verse_ref),
    FOREIGN KEY (book_file_id) REFERENCES Files (id) ON DELETE CASCADE
);

-- DROP TABLE IF EXISTS VersesToParagraphs;
CREATE TABLE IF NOT EXISTS VersesToParagraphs (
    verse_ref       INTEGER,
    paragraph_id    INTEGER,
    PRIMARY KEY (verse_ref, paragraph_id),
    FOREIGN KEY (verse_ref) REFERENCES Verses (id),
    FOREIGN KEY (paragraph_id) REFERENCES Paragraphs (id)
);

-- DROP TABLE IF EXISTS ExcludedVerses;
CREATE TABLE IF NOT EXISTS ExcludedVerses (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    translation_id  INT,
    FOREIGN KEY (verse_ref) REFERENCES Verses (verse_ref),
    FOREIGN KEY (translation_id) REFERENCES Translations (id) ON DELETE CASCADE
);

-- ================================================== Cross References & Footnotes ==================================================

-- DROP TABLE IF EXISTS TranslationFootNotes;
CREATE TABLE IF NOT EXISTS TranslationFootNotes (
    id              SERIAL PRIMARY KEY,
	file_id			INT,
    verse_ref       TEXT,
    xml             XML,
	text			TEXT,
	FOREIGN KEY (file_id) REFERENCES Files (id),
    FOREIGN KEY (verse_ref) REFERENCES Verses (verse_ref)
);

-- DROP TABLE IF EXISTS TranslationRefNotes;
CREATE TABLE IF NOT EXISTS TranslationRefNotes (
    id              SERIAL PRIMARY KEY,
	file_id			INT,
    from_verse_ref  TEXT,
    to_verse_start  TEXT,
    to_verse_end    TEXT,
    xml             XML,
	FOREIGN KEY (file_id) REFERENCES Files (id),
    FOREIGN KEY (from_verse_ref) REFERENCES Verses (verse_ref),
    FOREIGN KEY (to_verse_start) REFERENCES Verses (verse_ref),
    FOREIGN KEY (to_verse_end) REFERENCES Verses (verse_ref)
);

-- ================================================== Linked Components ==================================================

-- DROP TABLE IF EXISTS Strongs;
CREATE TABLE IF NOT EXISTS Strongs (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE,
    language_id     INT,
	-- Consider either storing Strongs Definition or api call to get it?
    FOREIGN KEY (language_id) REFERENCES Languages (id)
);

-- DROP TABLE IF EXISTS Entities;
CREATE TABLE IF NOT EXISTS Entities (
    id              SERIAL PRIMARY KEY
);

-- ================================================== Text Based Information ==================================================

-- DROP TABLE IF EXISTS Occurences;
CREATE TABLE IF NOT EXISTS Occurences (
	id                  SERIAL PRIMARY KEY,
	text				TEXT,
	type				TEXT, -- [quote, enitity, location]
	book_file_id		INT,
	verse_ref			TEXT,
	start_char			INT, -- Relative to Verse (for search)
	end_char			INT, -- Relative to Verse (for search)
	paragraph_id		INT,
	FOREIGN KEY (book_file_id) REFERENCES Files (id) ON DELETE CASCADE,
	FOREIGN KEY (verse_ref, book_file_id) REFERENCES VerseOccurences (verse_ref, book_file_id),
	FOREIGN KEY (paragraph_id) REFERENCES Paragraphs (id)
);

-- DROP TABLE IF EXISTS Quotes;
CREATE TABLE IF NOT EXISTS Quotes (
    id              SERIAL PRIMARY KEY,
    text            TEXT,
    quote_start     INT,
    quote_end       INT,
    parent_quote    INT,
    speaker         TEXT,
    audience        TEXT,
    FOREIGN KEY (quote_start) REFERENCES Occurences (id),
    FOREIGN KEY (quote_end) REFERENCES Occurences (id),
    FOREIGN KEY (parent_quote) REFERENCES Quotes (id)
);

-- This will also count as Entity Names to some degree since we are counting each occurence and mentions of them, but this could have start and end
-- DROP TABLE IF EXISTS EntityOccurence;
CREATE TABLE IF NOT EXISTS EntityOccurence (
    id              SERIAL PRIMARY KEY,
	entity_id		INT,
	occurence_id	INT,
	FOREIGN KEY (entity_id) REFERENCES Entities (id),
	FOREIGN KEY (occurence_id) REFERENCES Occurences (id)
);

-- DROP TABLE IF EXISTS StrongsOccurence;
CREATE TABLE IF NOT EXISTS StrongsOccurence (
    id              SERIAL PRIMARY KEY,
	occurence_id	INT,
    strong_code     TEXT,
    FOREIGN KEY (occurence_id) REFERENCES Occurences (id) ON DELETE CASCADE,
    FOREIGN KEY (strong_code) REFERENCES Strongs (code)
);

-- ================================================== [] ==================================================

-- Only storing important tokens
-- DROP TABLE IF EXISTS Tokens;
CREATE TABLE IF NOT EXISTS Tokens (
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
    FOREIGN KEY (paragraph_id) REFERENCES Paragraphs (id),
    FOREIGN KEY (verse_ref) REFERENCES Verses (verse_ref),
    FOREIGN KEY (head_token_id) REFERENCES Tokens (id)
);


-- ================================================== User Based Data ==================================================

-- DROP TABLE IF EXISTS UserNotes;
CREATE TABLE IF NOT EXISTS UserNotes (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMP,
    modified_at     TIMESTAMP,
    complete_at     TIMESTAMP,
    title           TEXT,
    content         TEXT,
    tags            TEXT,
	user_id			INT,
	FOREIGN KEY (user_id) REFERENCES Users (id)
);

-- DROP TABLE IF EXISTS NoteRelationships;
CREATE TABLE IF NOT EXISTS NoteRelationships (
    id              SERIAL PRIMARY KEY,
    note_from    	INT,
    note_to         INT, 
	type			TEXT,
    FOREIGN KEY (note_from) REFERENCES UserNotes (id),
	FOREIGN KEY (note_to) REFERENCES UserNotes (id)
);

-- DROP TABLE IF EXISTS UserHighlightsAnchors;
CREATE TABLE IF NOT EXISTS UserHighlightsAnchors (
    id              SERIAL PRIMARY KEY,
    book_file_id    INT,
    verse_ref       TEXT, 
	start_char		INT,
	end_char		INT,
	FOREIGN KEY (verse_ref, book_file_id) REFERENCES VerseOccurences (verse_ref, book_file_id)
);

-- DROP TABLE IF EXISTS UserHighlights;
CREATE TABLE IF NOT EXISTS UserHighlights (
    id              SERIAL PRIMARY KEY,
    start_anchor	INT,
    end_anchor      INT,
	color			TEXT,
    FOREIGN KEY (start_anchor) REFERENCES UserHighlightsAnchors (id) ON DELETE CASCADE,
	FOREIGN KEY (end_anchor) REFERENCES UserHighlightsAnchors (id) ON DELETE CASCADE
);

-- DROP TABLE IF EXISTS ReadHistory;
CREATE TABLE IF NOT EXISTS ReadHistory (
    history_id              SERIAL PRIMARY KEY,
    date_time               TEXT DEFAULT CURRENT_TIMESTAMP,
    book_file_id            INT,
    scripture_reference     TEXT,
	user_id					INT,
    FOREIGN KEY (book_file_id) REFERENCES Files (id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES Users (id)
);

-- ================================================== Imported Location Data (OpenBible.info) ==================================================

-- Location data can be more complicate than this, as can treat these as location reference points (waypoints / landmarks)
--		 so will require rendering in context and showing waypoints relative to area being referred to e.g. for territory 

-- DROP TABLE IF EXISTS Locations;
CREATE TABLE IF NOT EXISTS Locations (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT UNIQUE,
    friendly_id         TEXT,
    file_id             INT,
    type                TEXT,
    info                JSON
);

-- Refers to linking a location to a particular verse, and creating all the entries for this.
-- DROP TABLE IF EXISTS LocationOccurence;
CREATE TABLE IF NOT EXISTS LocationOccurence (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT,
    verse_ref           TEXT,
    FOREIGN KEY (location_id) REFERENCES Locations (location_id),
    FOREIGN KEY (verse_ref) REFERENCES Verses (verse_ref)
);

-- DROP TABLE IF EXISTS LocationRelationships;
CREATE TABLE IF NOT EXISTS LocationRelationships (
    id                  SERIAL PRIMARY KEY,
    from_location       TEXT,
    to_location         TEXT,
    type                TEXT,
    modifier            TEXT,
    info                TEXT,
    FOREIGN KEY (from_location) REFERENCES Locations (location_id),
    FOREIGN KEY (to_location) REFERENCES Locations (location_id)
);

-- DROP TABLE IF EXISTS GeoSources;
CREATE TABLE IF NOT EXISTS GeoSources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT UNIQUE,
    info                JSON
);

-- DROP TABLE IF EXISTS LocationDataSources;
CREATE TABLE IF NOT EXISTS LocationDataSources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT,
    location_id         TEXT,
    type                TEXT,
    info                JSON,
    FOREIGN KEY (source_id) REFERENCES GeoSources (source_id),
    FOREIGN KEY (location_id) REFERENCES Locations (location_id)
);

-- DROP TABLE IF EXISTS Images;
CREATE TABLE IF NOT EXISTS Images (
    id                  SERIAL PRIMARY KEY,
    image_id            TEXT UNIQUE,
    location_id         TEXT,
    file_id             INT,
    info                JSON,
    FOREIGN KEY (location_id) REFERENCES Locations (location_id),
    FOREIGN KEY (file_id) REFERENCES Files (id)
);

-- DROP TABLE IF EXISTS LocationImages;
CREATE TABLE IF NOT EXISTS LocationImages (
    id                  SERIAL PRIMARY KEY,
    image_id            TEXT,
    location_id         TEXT,
    type                TEXT,
    info                JSON,
    FOREIGN KEY (image_id) REFERENCES Images (image_id),
    FOREIGN KEY (location_id) REFERENCES Locations (location_id)
);

-- Not storing it as a file, instead just as entries, due to 
-- DROP TABLE IF EXISTS Geometries;
CREATE TABLE IF NOT EXISTS Geometries (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT UNIQUE,
    file_id             INT,
    geometries          TEXT,
    source              TEXT,
    surface             TEXT,
    info                JSON,
    FOREIGN KEY (geo_id) REFERENCES Locations (location_id),
    FOREIGN KEY (file_id) REFERENCES Files (id)
);

-- DROP TABLE IF EXISTS LocationGeometry;
CREATE TABLE IF NOT EXISTS LocationGeometry (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT,
    location_id         TEXT,
    FOREIGN KEY (geo_id) REFERENCES Geometries (geo_id),
    FOREIGN KEY (location_id) REFERENCES Locations (location_id)
);

-- ================================================== Other Derived Data ==================================================

-- For parts of scripture talking about same period, and how it aligns e.g. Gospels
-- DROP TABLE IF EXISTS Harmonies;
CREATE TABLE IF NOT EXISTS Harmonies (
    id                  SERIAL PRIMARY KEY,
	description			TEXT,
	order_num			INT
);

-- DROP TABLE IF EXISTS HarmonyMapping;
CREATE TABLE IF NOT EXISTS HarmonyMapping (
    harmony_id          INT,
	verse_ref			TEXT,
	PRIMARY KEY (harmony_id, verse_ref),
	FOREIGN KEY (verse_ref) REFERENCES Verses (verse_ref)
);

-- Order of all verses in the bible, can also skip if concurrent sections are read as normal
-- DROP TABLE IF EXISTS ChronologyOccurence;
CREATE TABLE IF NOT EXISTS ChronologyOccurence (
    id                  SERIAL PRIMARY KEY,
	chapter_ref			TEXT,
	verse_ref			TEXT
);

-- DROP TABLE IF EXISTS Chronology;
CREATE TABLE IF NOT EXISTS Chronology (
    id                  SERIAL PRIMARY KEY,
	prev_occurence		INT,
	FOREIGN KEY (prev_occurence) REFERENCES ChronologyOccurence (id)
);