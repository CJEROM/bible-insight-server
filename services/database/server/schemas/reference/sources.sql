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
    licence_id          INTEGER,
    is_deprecated       BOOLEAN DEFAULT FALSE,
	metadata			JSONB,
    FOREIGN KEY (parent_source) REFERENCES audit.sources(id),
    FOREIGN KEY (licence_id) REFERENCES audit.licences(id),
    FOREIGN KEY (source_type) REFERENCES lookup.source_types(code)
);