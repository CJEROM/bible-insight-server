CREATE TABLE IF NOT EXISTS bible.dblinfo (
    dbl_id                  TEXT,
    agreement_id            INTEGER, 
	latest_revision         BOOLEAN,                -- If this is last revision of this translation (based on dbl_id)
    supported               BOOLEAN DEFAULT TRUE,   -- Is this translation supported by Bible Insight Ingestion.
    reason_not_supported    TEXT,                   -- Reason why not supported if applicable  
    import_time             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(dbl_id, agreement_id)
);

CREATE TABLE IF NOT EXISTS bible.translations (
    id                  SERIAL PRIMARY KEY,
    dbl_id              TEXT,
    agreement_id        INTEGER,
	revision            INTEGER,
	revision_note		TEXT, -- For storing what has changed in the revision
    license_file        INTEGER,
    metadata_file       INTEGER,
    ldml_file           INTEGER,
    versification_file  INTEGER,
    style_file          INTEGER,
    medium              TEXT,
    name                TEXT,
    nameLocal           TEXT,
    description         TEXT,
    abbreviationLocal   TEXT,
    language_id         INTEGER,
    copyright           TEXT,
    promotion           TEXT,
    license_type        TEXT,       -- Extracted from website
    active              TIMESTAMP,
    expiry              TIMESTAMP,
	UNIQUE(dbl_id, agreement_id),
    FOREIGN KEY (dbl_id, agreement_id) REFERENCES bible.dblinfo (dbl_id, agreement_id) ON DELETE CASCADE,
    FOREIGN KEY (license_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (metadata_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (ldml_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (versification_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (style_file) REFERENCES bible.files (id) ON DELETE SET NULL,
    FOREIGN KEY (language_id) REFERENCES bible.languages (id) ON DELETE CASCADE
);
CREATE INDEX idx_bible_translations_dbl_id ON bible.translations (dbl_id);
CREATE INDEX idx_bible_translations_agreement_id ON bible.translations (agreement_id);
CREATE INDEX idx_bible_translations_revision ON bible.translations (revision);

CREATE TABLE IF NOT EXISTS bible.translationrelationships (
    id                  SERIAL PRIMARY KEY,
    from_translation    TEXT,
    from_revision       INTEGER,
    to_translation      TEXT,
    to_revision         INTEGER,
    type                TEXT
    -- FOREIGN KEY (from_translation) REFERENCES bible.translationinfo (dbl_id) ON DELETE CASCADE
    -- FOREIGN KEY (to_translation) REFERENCES bible.translations (dbl_id)
);