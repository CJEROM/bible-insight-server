

CREATE TABLE IF NOT EXISTS language.morph_scheme (
    id        SERIAL PRIMARY KEY,
    source_id        INTEGER,
    code             TEXT,           -- e.g. STEP-GRK, Robinson-GRK
    name             TEXT,
    language         TEXT,           -- grc, heb
    description      TEXT,
    standard_ref     TEXT,           -- book/paper/spec
    UNIQUE (source_id, code),
    FOREIGN KEY (source_id) REFERENCES audit.sources(id),
    FOREIGN KEY (language) REFERENCES language.languages(iso)
);

CREATE TABLE IF NOT EXISTS language.morph_key (
    id           SERIAL PRIMARY KEY,
    scheme_id        INTEGER,
    key_code         TEXT,           -- tense, voice, gender
    label            TEXT,           -- Tense
    description      TEXT,
    data_type        TEXT,           -- enum, text, numeric
    sort_order       INT,
    UNIQUE (scheme_id, key_code),
    FOREIGN KEY (scheme_id) REFERENCES language.morph_scheme(id)
);

CREATE TABLE IF NOT EXISTS language.morph_value (
    id         SERIAL PRIMARY KEY,
    key_id           INTEGER,
    value_code       TEXT,           -- A, P, Qal, Niphal
    label            TEXT,           -- Aorist, Present, Qal
    description      TEXT,
    sort_order       INT,
    UNIQUE (key_id, value_code),
    FOREIGN KEY (key_id) REFERENCES language.morph_key(id)
);

CREATE TABLE IF NOT EXISTS language.token_morph_attr (
    token_anchor_id  INTEGER,
    scheme_id        INTEGER,
    key_id           INTEGER,
    value_id         INTEGER,
    value_text       TEXT,           -- fallback for unmapped cases
    PRIMARY KEY (token_anchor_id, scheme_id, key_id),
    -- FOREIGN KEY (token_anchor_id) REFERENCES bible.tokens (token_id),
    FOREIGN KEY (scheme_id) REFERENCES language.morph_scheme(scheme_id),
    FOREIGN KEY (key_id) REFERENCES language.morph_key(key_id),
    FOREIGN KEY (value_id) REFERENCES language.morph_value(id)
);