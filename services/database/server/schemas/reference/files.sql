CREATE TABLE IF NOT EXISTS bible.files (
    id              SERIAL PRIMARY KEY,
    etag            TEXT,
    type            TEXT,
	-- Update to include bucket id for this file
    file_path       TEXT, -- where this would be the file path inside said bucket
    bucket          TEXT, -- this would be ignored
    -- translation_id  INTEGER,
    source_id       INTEGER,
    FOREIGN KEY (source_id) REFERENCES audit.sources (id) ON DELETE SET NULL
);