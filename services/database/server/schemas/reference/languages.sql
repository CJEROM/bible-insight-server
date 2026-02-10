
-- TO BE DEPRACATED
CREATE TABLE IF NOT EXISTS language.languages (
    id                  SERIAL PRIMARY KEY,
    iso                 TEXT UNIQUE, -- Follows ISO 639-3:2007 format? 
    name                TEXT,
    nameLocal           TEXT,
    scriptDirection     TEXT
);
CREATE INDEX idx_bible_languages_iso ON language.languages (iso);

CREATE TABLE IF NOT EXISTS language.scripts (
    id              SERIAL PRIMARY KEY,

    name            TEXT NOT NULL,        -- Paleo-Hebrew, Square Hebrew
    description     TEXT,
    period          TEXT,                 -- Optional textual period label
    script_type     TEXT,                 -- pictographic, abjad, alphabet
    
    language_id     INTEGER NOT NULL,
    source_id       INTEGER,
    is_default      BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (language_id) REFERENCES language.languages (id),
    FOREIGN KEY (source_id) REFERENCES audit.sources (id)
);

-- Potentially 
CREATE TABLE IF NOT EXISTS language.language_letters (
    id              SERIAL PRIMARY KEY,

    name            TEXT,
    description     TEXT,
    meaning         TEXT,       -- OR definition
    letter          TEXT,  

    ancient_symbol  INTEGER,    -- File ID to SVG of symbol
    phoneme         TEXT,       -- IPA representation (letter sound) -> Move to separate table for multiple phonemes?
    letter_type     TEXT,       -- 'vowel' or 'consonant'

    parent_letter   INTEGER,    -- For linking variants to main
    script_id       INTEGER NOT NULL,
    source_id       INTEGER,

    FOREIGN KEY (parent_letter) REFERENCES language.language_letters (id),
    FOREIGN KEY (ancient_symbol) REFERENCES audit.files (id),
    FOREIGN KEY (script_id) REFERENCES language.scripts (id),
    FOREIGN KEY (source_id) REFERENCES audit.sources (id)
);