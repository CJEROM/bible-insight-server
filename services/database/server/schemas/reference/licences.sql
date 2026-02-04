CREATE TABLE audit.licence_providers (
    provider_code   TEXT PRIMARY KEY,     -- CC, GNU, CUST 
    name            TEXT NOT NULL,
    description     TEXT
);

CREATE TABLE audit.licence_attributes (
    provider_code TEXT NOT NULL,
    attribute_code TEXT NOT NULL,        -- BY, NC, SRC, SAME, etc.

    name        TEXT NOT NULL,
    description TEXT NOT NULL,

    attribute_type TEXT NOT NULL CHECK (
        attribute_type IN ('permission', 'obligation', 'restriction')
    ),

    PRIMARY KEY (provider_code, attribute_code),
    FOREIGN KEY (provider_code) REFERENCES audit.licence_providers(provider_code)
);

CREATE TABLE audit.licences (
    id SERIAL PRIMARY KEY,

    provider_code TEXT NOT NULL,          -- CC, GNU
    code          TEXT UNIQUE,           -- BY-NC-ND, GPL
    name          TEXT NOT NULL,
    version       TEXT,
    
    link          TEXT,
    summary       TEXT,

    valid_from    DATE,
    valid_until   DATE,

    notes         TEXT,

    UNIQUE (provider_code, code, version),
    FOREIGN KEY (provider_code) REFERENCES audit.licence_providers(provider_code)
);