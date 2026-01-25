CREATE TABLE IF NOT EXISTS users.users (
    id                  SERIAL PRIMARY KEY,
    sud                 TEXT UNIQUE
);

-----------------------------------------------------------------

CREATE TABLE lookup.source_types (
    code            TEXT PRIMARY KEY, -- PUB, DAT, FILE
    name            TEXT,   -- Publisher, Dataset, File
    description     TEXT
);

CREATE TABLE IF NOT EXISTS audit.sources (
    id                  SERIAL PRIMARY KEY,
    source_type         TEXT,           -- publisher, dataset, file
    code                TEXT UNIQUE,    -- STEP, MorphGNT, OSHB
    name                TEXT,
    description         TEXT,
    version             TEXT,
    url                 TEXT,
	note				TEXT,
    parent_source       INTEGER,
    license_id          INTEGER,
    is_deprecated       BOOLEAN DEFAULT FALSE,
	metadata			JSONB,
    FOREIGN KEY (parent_source) REFERENCES audit.sources(id),
    FOREIGN KEY (license_id) REFERENCES audit.licenses(id),
    FOREIGN KEY (source_type) REFERENCES lookup.source_types(code)
);
-- CREATE INDEX idx_bible_sources_url ON audit.sources (url);

------------------------------------------------------------------

CREATE TABLE lookup.data_formats (
    code        TEXT PRIMARY KEY,     -- USX, TSV, XML, JSON
    mime_type   TEXT,
    extension   TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS audit.files (
    id              SERIAL PRIMARY KEY,
    etag            TEXT,
    type            TEXT,
	-- Update to include bucket id for this file
    object_path     TEXT, -- where this would be the file path inside said bucket
    bucket          TEXT, -- this would be ignored
    -- translation_id  INTEGER,
    source_id       INTEGER,
    data_formats    TEXT,
    version_id      TEXT, -- Object storage version id
    version_note    TEXT, -- e.g., for Git commit hash or similar
    active          BOOLEAN DEFAULT TRUE, -- the preferred/current version for this logical file
    FOREIGN KEY (source_id) REFERENCES audit.sources (id) ON DELETE SET NULL,
    FOREIGN KEY (data_formats) REFERENCES lookup.data_formats (code)
    UNIQUE (bucket, object_path, version_id)
);