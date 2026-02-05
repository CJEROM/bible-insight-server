CREATE TABLE lookup.source_types (
    code            TEXT PRIMARY KEY, -- PUB, DAT, FILE, DIST, CONT
    name            TEXT,   -- Publisher, Dataset, File
    description     TEXT
);

CREATE TABLE IF NOT EXISTS audit.sources (
    id                  SERIAL PRIMARY KEY,
    source_type         TEXT NOT NULL,           -- publisher, dataset, file, contributor
    code                TEXT UNIQUE NOT NULL,    -- STEP, MorphGNT, OSHB
    name                TEXT NOT NULL,
    description         TEXT,
    version             TEXT,
    url                 TEXT,
	note				TEXT,
    parent_source       INTEGER,
    official_citation   TEXT,  -- How to cite this source in scholarly work
    date_published      DATE,  -- When originally published/released
    deprecated_at       TIMESTAMP,  -- when it was deprecated
    metadata			JSONB,
    FOREIGN KEY (parent_source) REFERENCES audit.sources(id),
    FOREIGN KEY (source_type) REFERENCES lookup.source_types(code),
    CONSTRAINT no_self_parent CHECK (parent_source IS NULL OR parent_source != id),
);

-- For mapping extra sources to each other, which can help build dependency graph
CREATE TABLE IF NOT EXISTS audit.source_mappings (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL,
    related_source_id   INTEGER NOT NULL,
    relationship_type   TEXT NOT NULL,  -- 'contributes_to', 'distributes', 'derived_from', 'supplements', etc.
    role_description    TEXT,           -- e.g., "Primary translator", "Morphological annotation"
    is_primary          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES audit.sources(id),
    FOREIGN KEY (related_source_id) REFERENCES audit.sources(id),
    FOREIGN KEY (relationship_type) REFERENCES lookup.relationship_types(code),
    UNIQUE(source_id, related_source_id, relationship_type)
);