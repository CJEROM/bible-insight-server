-- MODIFED FROM: https://iso639-3.sil.org/code_tables/download_tables

-- ============================================================================
-- ISO 639-3 Codes
-- ============================================================================

CREATE TABLE standards.iso693_3_scopes (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

-- https://iso639-3.sil.org/about/scope
INSERT INTO standards.iso693_3_scopes (id, name, description)
VALUES 
    ('I', 'Individual',     'Represents a single, distinct language'),
    ('M', 'Macrolanguage',  'Represents a macrolanguage rather than an individual language'),
    ('S', 'Special',        'Reserved for special purposes (e.g. undetermined)');

CREATE TABLE standards.iso693_3_types (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

-- https://iso639-3.sil.org/about/types
INSERT INTO standards.iso693_3_types (id, name, description)
VALUES 
    ('A', 'Ancient',        'Known only from historical records'),
    ('C', 'Constructed',    'This part of ISO 639 also includes identifiers that denote constructed (or artificial) languages. In order to qualify for inclusion the language must have a literature and it must be designed for the purpose of human communication. It must be a complete language, and be in use for human communication by some community long enough to be passed to a second generation of users. Specifically excluded are reconstructed languages and computer programming languages.'),
    ('E', 'Extinct',        'A language is listed as extinct if it has gone extinct in recent times. (e.g. in the last few centuries). The criteria for identifying distinct languages in these cases are based on intelligibility (as defined for individual languages).'),
    ('H', 'Histrical',      'A language is listed as historic when it is considered to be distinct from any modern languages that are descended from it: for instance, Old English and Middle English. In these cases, the language did not become extinct; rather, it changed into a different language over time. Here, too, the criterion is that the language have a literature that is treated distinctly by the scholarly community.'),
    ('L', 'Living',         'A language is listed as living when there are people still living who learned it as a first language. This part of ISO 639 also includes identifiers for languages that are no longer living.'),
    ('S', 'Special',        'Special-use language code');

CREATE TABLE standards.iso693_3_codes (
    id          char(3) PRIMARY KEY,    -- The three-letter 639-3 identifier
    part2b      char(3) NULL,           -- Equivalent 639-2 identifier of the bibliographic applications (if there is one)
    part2t      char(3) NULL,           -- Equivalent 639-2 identifier of the terminology applications code (if there is one)
    part1       char(2) NULL,           -- Equivalent 639-1 identifier, (if there is one)
    scope       char(1) NOT NULL, 
    type        char(1) NOT NULL,
    ref_name    varchar(150) NOT NULL,  -- Reference language name 
    comment     varchar(150),      -- Comment relating to one or more of the columns
    FOREIGN KEY (scope) REFERENCES standards.iso693_3_scopes (id),
    FOREIGN KEY (type) REFERENCES standards.iso693_3_types (id)
);

-- ============================================================================
-- ISO 639-3 Code Language Names
-- ============================================================================

CREATE TABLE standards.iso693_3_names (
    id              SERIAL PRIMARY KEY,
    iso_code        char(3)     NOT NULL,   -- The three-letter 639-3 identifier
    print_name      varchar(75) NOT NULL,   -- One of the names associated with this identifier 
    inverted_name   varchar(75) NOT NULL,   -- The inverted form of this Print_Name form   
    FOREIGN KEY (iso_code) REFERENCES standards.iso693_3_codes (id)
); 

-- ============================================================================
-- ISO 639-3 Retirements (A.K.A Depracated Codes)
-- ============================================================================

CREATE TABLE standards.iso693_3_retirement_reasons (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

INSERT INTO standards.iso693_3_retirement_reasons (id, name, description)
VALUES
    -- Associated with Change_To
    ('C', 'Change',         'Code replaced by another'),
    ('D', 'Duplicate',      'Code duplicated another'),
    ('M', 'Merge',          'Multiple codes merged'),
    -- Exists independently
    ('N', 'Non-existent',   'Language determined not to exist'),
    ('S', 'Split',          'Language split into multiple codes');
    
CREATE TABLE standards.iso693_3_retirements (
    id                  SERIAL PRIMARY KEY,
    iso_code            char(3)      NOT NULL,      -- The three-letter 639-3 identifier
    ref_name            varchar(150) NOT NULL,      -- reference name of language
    retired_reason      char(1)      NOT NULL,
    retired_remedy      varchar(300) NULL,          -- The instructions for updating an instance of the retired (split) identifier
    effective           DATE         NOT NULL,       -- The date the retirement became effective
    FOREIGN KEY (retired_reason) REFERENCES standards.iso693_3_retirement_reasons (id)
);

CREATE TABLE standards.iso693_3_retirement_changes (
    id                  SERIAL PRIMARY KEY,
    from_retirement     INTEGER NOT NULL,
    to_iso_code         char(3),          -- in the cases of C, D, and M (Retirement_Reason), the identifier to which all instances of this Id should be changed
    to_retirement       INTEGER,
    FOREIGN KEY (to_iso_code) REFERENCES standards.iso693_3_codes (id),
    FOREIGN KEY (from_retirement) REFERENCES standards.iso693_3_retirements (id),
    FOREIGN KEY (to_retirement) REFERENCES standards.iso693_3_retirements (id)
);

-- ============================================================================
-- ISO 639-3 Macrolanguage Codes
-- ============================================================================

CREATE TABLE standards.iso693_3_status (
    id              char(1) PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT NOT NULL
);

INSERT INTO standards.iso693_3_status (id, name, description)
VALUES 
    ('A', 'Active',     'Code is currently valid'),
    ('R', 'Retired',    'Code has been retired');

CREATE TABLE standards.iso693_3_macrolanguages (
    id                  SERIAL PRIMARY KEY,
    macro_id            char(3) NOT NULL,   -- The identifier for a macrolanguage
    iso_id              char(3),   -- The identifier for an individual language that is a member of the macrolanguage
    retirement_id       INTEGER,
    iso_status          char(1) NOT NULL,   -- indicating the status of the individual code element
    FOREIGN KEY (macro_id) REFERENCES standards.iso693_3_codes (id),
    FOREIGN KEY (iso_id) REFERENCES standards.iso693_3_codes (id),
    FOREIGN KEY (retirement_id) REFERENCES standards.iso693_3_retirements(id),
    FOREIGN KEY (iso_status) REFERENCES standards.iso693_3_status (id)
);