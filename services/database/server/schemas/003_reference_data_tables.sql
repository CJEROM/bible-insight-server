CREATE TABLE IF NOT EXISTS users.users (
    id                  SERIAL PRIMARY KEY,
    sud                 TEXT UNIQUE
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
	metadata			JSONB,
    FOREIGN KEY (parent_source) REFERENCES audit.sources(source_id)
);
-- CREATE INDEX idx_bible_sources_url ON audit.sources (url);

CREATE TABLE IF NOT EXISTS audit.files (
    id              SERIAL PRIMARY KEY,
    etag            TEXT,
    type            TEXT,
	-- Update to include bucket id for this file
    file_path       TEXT, -- where this would be the file path inside said bucket
    bucket          TEXT, -- this would be ignored
    -- translation_id  INTEGER,
    source_id       INTEGER,
    exists_flag     BOOLEAN DEFAULT TRUE,   -- if the file still exists in storage (for versioning if deleted, see only existing)
    FOREIGN KEY (source_id) REFERENCES audit.sources (id) ON DELETE SET NULL
);