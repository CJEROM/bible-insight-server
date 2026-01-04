CREATE TABLE IF NOT EXISTS bible.languages (
    id                  SERIAL PRIMARY KEY,
    iso                 TEXT UNIQUE, -- Follows ISO 639-3:2007 format? 
    name                TEXT,
    nameLocal           TEXT,
    scriptDirection     TEXT
);
CREATE INDEX idx_bible_languages_iso ON bible.languages (iso);

CREATE TABLE IF NOT EXISTS bible.language_letters (
    id              SERIAL PRIMARY KEY,
    letter          TEXT,  
    phoneme         TEXT, -- Whether 'vowel' or 'consonant'
    parent_letter   INTEGER,
    ancient_symbol  INTEGER,
    symbol_def      TEXT,
    language_id     INTEGER,
    FOREIGN KEY (parent_letter) REFERENCES bible.language_letters (id),
    FOREIGN KEY (ancient_symbol) REFERENCES bible.files (id),
    FOREIGN KEY (language_id) REFERENCES bible.languages (id)
);