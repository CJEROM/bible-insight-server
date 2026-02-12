-- MODIFED FROM: https://iso639-3.sil.org/code_tables/download_tables

-- ============================================================================
-- ISO 639-3 Codes
-- ============================================================================

CREATE TABLE sil.iso_scopes (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

INSERT INTO sil.iso_scopes (id, name, description)
VALUES 
    ('I', 'Individual',     'Represents a single, distinct language'),
    ('M', 'Macrolanguage',  'Represents a macrolanguage rather than an individual language'),
    ('S', 'Special',        'Reserved for special purposes (e.g. undetermined)');

CREATE TABLE sil.iso_types (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

INSERT INTO sil.iso_types (id, name, description)
VALUES 
    ('A', 'Ancient',        'Known only from historical records'),
    ('C', 'Constructed',    'Artificially created language'),
    ('E', 'Extinct',        'No longer spoken'),
    ('H', 'Histrical',      'Earlier form of a modern language'),
    ('L', 'Living',         'Currently spoken'),
    ('S', 'Special',        'Special-use language code');

CREATE TABLE sil.iso_codes (
    id          char(3) PRIMARY KEY,    -- The three-letter 639-3 identifier
    part2b      char(3) NULL,           -- Equivalent 639-2 identifier of the bibliographic applications (if there is one)
    part2t      char(3) NULL,           -- Equivalent 639-2 identifier of the terminology applications code (if there is one)
    part1       char(2) NULL,           -- Equivalent 639-1 identifier, (if there is one)
    scope       char(1) NOT NULL, 
    type        char(1) NOT NULL,
    ref_name    varchar(150) NOT NULL,  -- Reference language name 
    comment     varchar(150),      -- Comment relating to one or more of the columns
    FOREIGN KEY (scope) REFERENCES sil.iso_scopes (id),
    FOREIGN KEY (type) REFERENCES sil.iso_types (id)
);

-- ============================================================================
-- ISO 639-3 Code Language Names
-- ============================================================================

CREATE TABLE sil.iso_names (
    id              SERIAL PRIMARY KEY,
    iso_code        char(3)     NOT NULL,   -- The three-letter 639-3 identifier
    print_name      varchar(75) NOT NULL,   -- One of the names associated with this identifier 
    inverted_name   varchar(75) NOT NULL,   -- The inverted form of this Print_Name form   
    FOREIGN KEY (iso_code) REFERENCES sil.iso_codes (id)
); 

-- ============================================================================
-- ISO 639-3 Retirements (A.K.A Depracated Codes)
-- ============================================================================

CREATE TABLE sil.retirement_reasons (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

INSERT INTO sil.retirement_reasons (id, name, description)
VALUES
    -- Associated with Change_To
    ('C', 'Change',         'Code replaced by another'),
    ('D', 'Duplicate',      'Code duplicated another'),
    ('M', 'Merge',          'Multiple codes merged'),
    -- Exists independently
    ('N', 'Non-existent',   'Language determined not to exist'),
    ('S', 'Split',          'Language split into multiple codes');
    
CREATE TABLE sil.retirements (
    id                  SERIAL PRIMARY KEY,
    iso_code            char(3)      NOT NULL,      -- The three-letter 639-3 identifier
    ref_name            varchar(150) NOT NULL,      -- reference name of language
    retired_reason      char(1)      NOT NULL,
    retired_remedy      varchar(300) NULL,          -- The instructions for updating an instance of the retired (split) identifier
    effective           DATE         NOT NULL,       -- The date the retirement became effective
    FOREIGN KEY (retired_reason) REFERENCES sil.retirement_reasons (id)
);

CREATE TABLE sil.retirement_changes (
    id                  SERIAL PRIMARY KEY,
    from_retirement     INTEGER NOT NULL,
    to_iso_code         char(3),          -- in the cases of C, D, and M (Retirement_Reason), the identifier to which all instances of this Id should be changed
    to_retirement       INTEGER,
    FOREIGN KEY (to_iso_code) REFERENCES sil.iso_codes (id),
    FOREIGN KEY (from_retirement) REFERENCES sil.retirements (id),
    FOREIGN KEY (to_retirement) REFERENCES sil.retirements (id)
);

-- ============================================================================
-- ISO 639-3 Macrolanguage Codes
-- ============================================================================

CREATE TABLE sil.iso_status (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

INSERT INTO sil.iso_status (id, name, description)
VALUES 
    ('A', 'Active',     'Code is currently valid'),
    ('R', 'Retired',    'Code has been retired');

CREATE TABLE sil.macrolanguages (
    id                  SERIAL PRIMARY KEY,
    macro_id            char(3) NOT NULL,   -- The identifier for a macrolanguage
    iso_id              char(3),   -- The identifier for an individual language that is a member of the macrolanguage
    retirement_id       INTEGER,
    iso_status          char(1) NOT NULL,   -- indicating the status of the individual code element
    FOREIGN KEY (macro_id) REFERENCES sil.iso_codes (id),
    FOREIGN KEY (iso_id) REFERENCES sil.iso_codes (id),
    FOREIGN KEY (retirement_id) REFERENCES sil.retirements(id),
    FOREIGN KEY (iso_status) REFERENCES sil.iso_status (id)
);