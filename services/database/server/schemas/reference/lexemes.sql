
CREATE TABLE IF NOT EXISTS language.lexicon (
    id      SERIAL PRIMARY KEY,
    source_id       INTEGER,
    language        TEXT,      -- grc, heb
    code            TEXT,      -- Strong, BDB, STEP
    long_name       TEXT,      -- Exhaustive Strong's Concordance, 
    description     TEXT,
    FOREIGN KEY (source_id) REFERENCES audit.sources (id),
    FOREIGN KEY (language) REFERENCES language.languages (iso)
);

CREATE TABLE IF NOT EXISTS language.lexeme (
    id       SERIAL PRIMARY KEY,
    lexicon_id      INTEGER,
    lemma           TEXT,
    lemma_norm      TEXT,
    strong_code     TEXT,
    gloss           TEXT,
    description     TEXT,
    UNIQUE (lexicon_id, lemma, strong_code),
    FOREIGN KEY (lexicon_id) REFERENCES language.lexicon (id)
);

CREATE TABLE IF NOT EXISTS language.token_lexeme (
    token_anchor_id  INTEGER,
    lexeme_id        INTEGER,
    confidence       NUMERIC,   -- optional (for NLP)
    PRIMARY KEY (token_anchor_id, lexeme_id),
    -- FOREIGN KEY (token_anchor_id) REFERENCES bible.tokens (id),
    FOREIGN KEY (lexeme_id) REFERENCES language.lexeme (id)
);
