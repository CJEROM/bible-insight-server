-- Is this translation + revision supported by Bible Insight Ingestion. Why or why not?
CREATE TABLE IF NOT EXISTS audit.dbl_info (
    dbl_id                  TEXT NOT NULL,
	revision                INTEGER NOT NULL,   -- >0 = revision, 0 = translation
    supported               BOOLEAN DEFAULT TRUE,
    test_import             BOOLEAN DEFAULT FALSE, -- Change Default in future?
    reason_not_supported    TEXT,
    PRIMARY KEY (dbl_id, revision),
    CHECK (revision >= 0)
);

CREATE TABLE IF NOT EXISTS bible.translations (
    id                  SERIAL PRIMARY KEY,
    dbl_id              TEXT,
	revision            INTEGER,
	revision_note		TEXT, -- For storing what has changed in the revision
    revision_date       TIMESTAMP,
    language_id         INTEGER,
    medium              TEXT,
    name                TEXT,
    nameLocal           TEXT,
    description         TEXT,
    abbreviation        TEXT,
    abbreviationLocal   TEXT,
    copyright           TEXT,
    promotion           TEXT,
	UNIQUE(dbl_id, revision),
    FOREIGN KEY (dbl_id, revision) REFERENCES audit.dbl_info (dbl_id, revision) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES language.languages (id) ON DELETE CASCADE
);
CREATE INDEX idx_bible_translations_dbl_id ON bible.translations (dbl_id);
CREATE INDEX idx_bible_translations_revision ON bible.translations (revision);

-- Keeps a separate version of the files e.g. Metadata version (tailored to format instead of content)
CREATE TABLE IF NOT EXISTS bible.translation_files (
    id                  SERIAL PRIMARY KEY,
    translation_id      INTEGER,
    file_id             INTEGER,
    type                TEXT, -- e.g. Metadata, LDML, Versification, Style, License
    version             TEXT,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES audit.files (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.translationrelationships (
    id                  SERIAL PRIMARY KEY,
    from_translation    TEXT,       -- dbl_id
    from_revision       INTEGER,
    to_translation      TEXT,       -- dbl_id
    to_revision         INTEGER,
    type                TEXT
    -- FOREIGN KEY (from_translation) REFERENCES bible.translationinfo (dbl_id) ON DELETE CASCADE
    -- FOREIGN KEY (to_translation) REFERENCES bible.translations (dbl_id)
);