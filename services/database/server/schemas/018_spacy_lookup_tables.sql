CREATE TABLE lookup.nlp_pos_types (
    id SERIAL PRIMARY KEY,
    pos_tag VARCHAR(10) NOT NULL UNIQUE,    -- e.g. 'NOUN', 'VERB'
    description TEXT                        -- e.g. 'Noun, a person, place, or thing'
);

CREATE TABLE lookup.nlp_tag_types (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(10) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE lookup.nlp_dep_types (
    id SERIAL PRIMARY KEY,
    dep VARCHAR(20) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS nlp.spacy_modules (
    id                  SERIAL PRIMARY KEY,
    language_iso        TEXT,               -- The code I use for language (iso)
    spacy_code          TEXT,                  -- The code spacy uses for a language
    spacy_model         TEXT,                  -- en_core_web_sm
    supports_pos        BOOLEAN DEFAULT FALSE, -- Model capabilities supported?
    supports_ner        BOOLEAN DEFAULT FALSE,
    supports_dep        BOOLEAN DEFAULT FALSE,
    supports_vectors    BOOLEAN DEFAULT FALSE,
    supports_lemma      BOOLEAN DEFAULT FALSE,
    version             TEXT,
    notes               TEXT,
    FOREIGN KEY (language_iso) REFERENCES bible.languages (iso)
);