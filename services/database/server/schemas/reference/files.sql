CREATE TABLE lookup.data_formats (
    code        TEXT PRIMARY KEY,     -- USX, TSV, XML, JSON
    mime_type   TEXT,
    extension   TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS audit.files (
    id              SERIAL PRIMARY KEY,
    etag            TEXT NOT NULL,
    type            TEXT NOT NULL,
	-- Update to include bucket id for this file
    object_path     TEXT, -- where this would be the file path inside said bucket
    bucket          TEXT, -- this would be ignored
    -- translation_id  INTEGER,
    source_id       INTEGER,
    data_format     TEXT NOT NULL,
    version_id      TEXT, -- Object storage version id
    version_note    TEXT, -- e.g., for Git commit hash or similar
    active          BOOLEAN DEFAULT TRUE, -- the preferred/current version for this logical file

    content_hash    TEXT NOT NULL,

    FOREIGN KEY (source_id) REFERENCES audit.sources (id) ON DELETE SET NULL,
    FOREIGN KEY (data_format) REFERENCES lookup.data_formats (code)
    -- UNIQUE (bucket, object_path, version_id)
);