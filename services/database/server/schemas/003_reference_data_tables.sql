CREATE TABLE IF NOT EXISTS users.users (
    id                  SERIAL PRIMARY KEY,
    sud                 TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS bible.sources (
    id                  SERIAL PRIMARY KEY,
    code                TEXT UNIQUE,   -- STEP, MorphGNT, OSHB
    name                TEXT,
    description         TEXT,
    version             TEXT,
    url                 TEXT,
	note				TEXT,
    dateAccessed        TIMESTAMP,
    parent_source       INTEGER,
	metadata			JSONB,
    FOREIGN KEY (parent_source) REFERENCES bible.sources(source_id)
);
CREATE INDEX idx_bible_sources_url ON bible.sources (url);

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