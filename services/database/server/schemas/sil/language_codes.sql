-- MODIFED FROM: https://iso639-3.sil.org/code_tables/download_tables

-- ============================================================================
-- ISO 639-3 Codes
-- ============================================================================

CREATE TABLE sil.iso_codes (
    id          char(3) NOT NULL,  -- The three-letter 639-3 identifier
    part2b      char(3) NULL,      -- Equivalent 639-2 identifier of the bibliographic applications (if there is one)
    part2t      char(3) NULL,      -- Equivalent 639-2 identifier of the terminology applications code (if there is one)
    part1       char(2) NULL,      -- Equivalent 639-1 identifier, (if there is one)
    scope       char(1) NOT NULL, 
    type        char(1) NOT NULL,
    ref_name    varchar(150) NOT NULL,   -- Reference language name 
    comment     varchar(150) NULL,       -- Comment relating to one or more of the columns
    FOREIGN KEY (scope) REFERENCES sil.iso_scopes (id),
    FOREIGN KEY (type) REFERENCES sil.iso_types (id)
);

CREATE TABLE sil.scopes (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);

INSERT VALUES INTO sil.iso_scopes (code, name, description)
VALUES 
    ('I', 'Individual', ''),
    ('M', 'Macrolanguage', ''),
    ('S', 'Special', '');

CREATE TABLE sil.iso_types (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);

INSERT VALUES INTO sil.types (code, name, description)
VALUES 
    ('A', 'Ancient', ''),
    ('C', 'Constructed', ''),
    ('E', 'Extinct', ''),
    ('H', 'Histrical', ''),
    ('L', 'Living', ''),
    ('S', 'Special', '');

-- ============================================================================
-- ISO 639-3 Code Language Names
-- ============================================================================

CREATE TABLE sil.iso_names (
    iso_code        char(3)     PRIMARY KEY,    -- The three-letter 639-3 identifier
    print_name      varchar(75) NOT NULL,       -- One of the names associated with this identifier 
    inverted_name   varchar(75) NOT NULL,       -- The inverted form of this Print_Name form   
    FOREIGN KEY (iso_code) REFERENCES sil.iso_codes (id)
); 

-- ============================================================================
-- ISO 639-3 Macrolanguage Codes
-- ============================================================================

CREATE TABLE sil.macrolanguages (
    macro_id            char(3) PRIMARY KEY,    -- The identifier for a macrolanguage
    iso_id              char(3) NOT NULL,       -- The identifier for an individual language that is a member of the macrolanguage
    iso_status          char(1) NOT NULL,       -- A (active) or R (retired) indicating the status of the individual code element
    FOREIGN KEY (iso_id) REFERENCES sil.iso_codes (id),
    FOREIGN KEY (iso_status) REFERENCES sil.macro_status (id)
);

CREATE TABLE sil.macro_status (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);

INSERT VALUES INTO sil.macro_status (code, name, description)
VALUES 
    ('A', 'Active', ''),
    ('R', 'Retired', '');

-- ============================================================================
-- ISO 639-3 Retirements (/Depracated)
-- ============================================================================

CREATE TABLE sil.retirements (
    id                  SERIAL PRIMARY KEY,
    iso_code            char(3)      NOT NULL,      -- The three-letter 639-3 identifier
    ref_name            varchar(150) NOT NULL,      -- reference name of language
    retired_reason      char(1)      NOT NULL,
    changed_to          char(3)      NULL,          -- in the cases of C, D, and M, the identifier to which all instances of this Id should be changed
    retired_remedy      varchar(300) NULL,          -- The instructions for updating an instance of the retired (split) identifier
    Effective           DATE        NOT NULL,       -- The date the retirement became effective
    FOREIGN KEY (iso_code) REFERENCES sil.iso_codes (id),
    FOREIGN KEY (retired_reason) REFERENCES sil.retirement_reasons (id),
    -- FOREIGN KEY (changed_to) REFERENCES sil.iso_codes (id),
);

CREATE TABLE lookup.retirement_reasons (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT
)

INSERT INTO sil.retirement_reasons (code, name, description)
VALUES
    -- Associated with Change_To
    ('C', 'Change', ''),
    ('D', 'Duplicate', ''),
    ('M', 'Merge', ''),
    -- Exists independently
    ('N', 'Non-existent', ''),
    ('S', 'Split', '');
