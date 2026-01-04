CREATE TABLE IF NOT EXISTS users.users (
    id                  SERIAL PRIMARY KEY,
    sud                 TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS bible.sources (
    id                  SERIAL PRIMARY KEY,
    url                 TEXT UNIQUE,
	note				TEXT,
	metadata			JSONB
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