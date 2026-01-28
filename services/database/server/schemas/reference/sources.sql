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