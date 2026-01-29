-- Is this translation + revision supported by Bible Insight Ingestion. Why or why not?
CREATE TABLE IF NOT EXISTS audit.dbl_info (
    dbl_id                  TEXT PRIMARY KEY,
	revision                INTEGER, -- Optional: Either specific revision not supported or entire translation
    is_translation          BOOLEAN, -- TRUE = translation, FALSE = revision
    supported               BOOLEAN DEFAULT TRUE,
    test_import             BOOLEAN DEFAULT FALSE, -- Change Default in future?
    reason_not_supported    TEXT
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
    abbreviationLocal   TEXT,
    copyright           TEXT,
    promotion           TEXT,
	UNIQUE(dbl_id, revision),
    FOREIGN KEY (dbl_id) REFERENCES audit.dbl_info (dbl_id) ON DELETE CASCADE,
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

CREATE TABLE IF NOT EXISTS audit.dbl_agreements (
    agreement_id        INTEGER PRIMARY KEY,
    dbl_id              TEXT, --
    licence_id          INTEGER,
    dateLicense         TIMESTAMP,
    dateLicenseExpiry   TIMESTAMP,
    file_id             INTEGER,    -- Secondary Link to License File
    active              BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (dbl_id) REFERENCES audit.dbl_info(dbl_id),
    FOREIGN KEY (licence_id) REFERENCES audit.licences(id),
    FOREIGN KEY (file_id) REFERENCES audit.files(id)
);

-- Link agreements to specific revisions (some may overlap, the latter agreement applies)
CREATE TABLE IF NOT EXISTS audit.dbl_revision_agreements (
    agreement_id        INTEGER,
    revision            INTEGER,
    active              BOOLEAN DEFAULT TRUE, -- If multiple terms exist for same revision -> FALSE
    PRIMARY KEY (agreement_id, revision),
    FOREIGN KEY (agreement_id) REFERENCES audit.dbl_agreements(agreement_id) ON DELETE CASCADE
);