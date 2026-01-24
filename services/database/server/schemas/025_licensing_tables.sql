
CREATE TABLE audit.license_providers (
    provider_code   TEXT PRIMARY KEY,     -- CC, GNU, CUST 
    name            TEXT NOT NULL,
    description     TEXT
);

CREATE TABLE audit.license_attributes (
    provider_code TEXT NOT NULL,
    attribute_code TEXT NOT NULL,        -- BY, NC, SRC, SAME, etc.

    name        TEXT NOT NULL,
    description TEXT NOT NULL,

    attribute_type TEXT NOT NULL CHECK (
        attribute_type IN ('permission', 'obligation', 'restriction')
    ),

    PRIMARY KEY (provider_code, attribute_code),
    FOREIGN KEY (provider_code) REFERENCES audit.license_providers(provider_code)
);

CREATE TABLE audit.licenses (
    license_id SERIAL PRIMARY KEY,

    provider_code TEXT NOT NULL,          -- CC, GNU
    code          TEXT NOT NULL,           -- BY-NC-ND, GPL
    name          TEXT NOT NULL,
    version       TEXT,
    
    link          TEXT,
    summary       TEXT,

    valid_from    DATE,
    valid_until   DATE,

    notes         TEXT,

    UNIQUE (provider_code, code, version),
    FOREIGN KEY (provider_code) REFERENCES audit.license_providers(provider_code)
);

CREATE TABLE audit.license_attribute_mapping (
    mapping_id SERIAL PRIMARY KEY,

    license_id   INT,
    agreement_id INT,

    provider_code  TEXT NOT NULL,
    attribute_code TEXT NOT NULL,

    -- Enforce XOR: either license OR agreement
    CHECK (
        (license_id IS NOT NULL AND agreement_id IS NULL)
        OR
        (license_id IS NULL AND agreement_id IS NOT NULL)
    ),

    FOREIGN KEY (license_id)
        REFERENCES audit.licenses(license_id)
        ON DELETE CASCADE,

    FOREIGN KEY (agreement_id)
        REFERENCES audit.dbl_agreements(agreement_id)
        ON DELETE CASCADE,

    FOREIGN KEY (provider_code, attribute_code)
        REFERENCES audit.license_attributes(provider_code, attribute_code)
);