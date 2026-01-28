CREATE TABLE IF NOT EXISTS bible.lexemes (
    id              SERIAL PRIMARY KEY,
    source          TEXT,   -- 'strongs', 'bdb', 'manual'
    source_version  TEXT,
    strongs_code    TEXT UNIQUE, 
    -- EXAMPLES of different sources:
    -- BDB          (Brown–Driver–Briggs)
    -- HALOT        (Hebrew and Aramaic Lexicon of the Old Testament))
    -- TDOT         (Theological Dictionary of the Old Testament)
    -- BDAG         (A Greek–English Lexicon of the New Testament and Other Early Christian Literature)
    -- LSJ          (Liddell–Scott–Jones)
    -- TDNT         (The Theological Dictionary of the New Testament)
    -- Louw-Nida    (The Louw–Nida Greek-English Lexicon of the New Testament Based on Semantic Domains)
    -- Manual       (I can add some lexemes manually?)
    -- Wiktionary
    -- NLP? -> through tokens table
    language_id     INTEGER,
    native_word     TEXT,
    lemma           TEXT,
    raw_pos         TEXT,
    transliteration TEXT,
    pronunciation   TEXT,
    audio_file      INTEGER, -- Pronounciation audio file link
    raw_gloss       TEXT,
    FOREIGN KEY (language_id) REFERENCES language.languages (id) ON DELETE CASCADE,
    FOREIGN KEY (audio_file) REFERENCES audit.files (id)
);
CREATE INDEX idx_bible_lexemes_strongs_code ON bible.lexemes (strongs_code) WHERE strongs_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS bible.lexeme_relations (
    id              SERIAL PRIMARY KEY,
    from_lexeme     INTEGER,
    to_lexeme       INTEGER,
    relation_type   TEXT,
    confidence      TEXT, -- Scholarly honesty? Don't need to use yet
    notes           TEXT,
    FOREIGN KEY (from_lexeme) REFERENCES bible.lexemes (id) ON DELETE CASCADE,
    FOREIGN KEY (to_lexeme) REFERENCES bible.lexemes (id) ON DELETE CASCADE,
    UNIQUE (from_lexeme, to_lexeme, relation_type)
);