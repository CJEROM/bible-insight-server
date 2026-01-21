CREATE TABLE IF NOT EXISTS language.languages (
    id                  SERIAL PRIMARY KEY,
    iso                 TEXT UNIQUE, -- Follows ISO 639-3:2007 format? 
    name                TEXT,
    nameLocal           TEXT,
    scriptDirection     TEXT
);
CREATE INDEX idx_bible_languages_iso ON language.languages (iso);

CREATE TABLE IF NOT EXISTS language.language_letters (
    id              SERIAL PRIMARY KEY,
    letter          TEXT,  
    phoneme         TEXT, -- Whether 'vowel' or 'consonant'
    parent_letter   INTEGER,
    ancient_symbol  INTEGER,
    symbol_def      TEXT,
    language_id     INTEGER,
    FOREIGN KEY (parent_letter) REFERENCES language.language_letters (id),
    FOREIGN KEY (ancient_symbol) REFERENCES bible.files (id),
    FOREIGN KEY (language_id) REFERENCES language.languages (id)
);