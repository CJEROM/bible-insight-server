CREATE TABLE audit.licence_attributes (
    attribute_code  TEXT PRIMARY KEY,        -- BY, NC, SRC, SAME, etc.
    name            TEXT NOT NULL,
    description     TEXT NOT NULL,
    attribute_type  TEXT NOT NULL CHECK (
        attribute_type IN ('PERMISSION', 'OBLIGATION', 'RESTRICTION')
    )
);

CREATE TABLE audit.licences (
    id              SERIAL PRIMARY KEY,

    source_id       INTEGER,                -- Example: Source ID for 'CC'
    code            TEXT UNIQUE NOT NULL,          -- Example: 'CC BY 4.0'
    name            TEXT NOT NULL,
    version         TEXT,
    
    link            TEXT,                   -- If there is one link to licence
    summary         TEXT,

    valid_from      DATE,
    valid_until     DATE,

    notes           TEXT
);

CREATE TABLE audit.licence_attribute_mapping (
    licence_id      INTEGER NOT NULL,
    attribute_code  TEXT NOT NULL,
    
    -- Optional: customize the standard attribute for this licence
    custom_note     TEXT,
    
    PRIMARY KEY (licence_id, attribute_code),
    FOREIGN KEY (licence_id) REFERENCES audit.licences(id) ON DELETE CASCADE,
    FOREIGN KEY (attribute_code) REFERENCES audit.licence_attributes(attribute_code)
);

CREATE TABLE audit.source_licences (
    source_id       INTEGER NOT NULL,
    licence_id      INTEGER NOT NULL,
    
    PRIMARY KEY (source_id, licence_id),
    FOREIGN KEY (source_id) REFERENCES audit.sources(id) ON DELETE CASCADE,
    FOREIGN KEY (licence_id) REFERENCES audit.licences(id) ON DELETE CASCADE
);