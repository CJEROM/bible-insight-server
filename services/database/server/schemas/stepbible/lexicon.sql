DROP SCHEMA IF EXISTS lexicon CASCADE;
CREATE SCHEMA lexicon;

-- ==============================================================================================================================
-- LANGUAGE
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.language(
    id              TEXT PRIMARY KEY,
    name            TEXT,
    iso             CHAR(3),
    feature_value   INTEGER,
    FOREIGN KEY (iso) REFERENCES standards.iso693_3_codes (id),
    FOREIGN KEY (feature_value) REFERENCES morphology.feature_values (id)
);

-- Language is A=Aramaic, H=Hebrew, G=Greek and N=Name (not language specific)
INSERT INTO lexicon.language (id, name, iso)
VALUES
    ('A', 'Aramaic' , 'arc'),
    ('H', 'Hebrew'  , 'hbo'), -- Ancient Hebrew
    ('G', 'Greek'   , 'grc'),
    ('N', 'Noun'    , NULL);

-- ==============================================================================================================================
-- TYPE (PART OF SPEECH)
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.type(
    id              TEXT PRIMARY KEY,
    code            TEXT,
    name            TEXT,
    feature_value   INTEGER,
    FOREIGN KEY (feature_value) REFERENCES morphology.feature_values (id)
);

-- Type is A=Adjective, Adv=Adverb, Art=Article, etc.
INSERT INTO lexicon.type (code, name)
VALUES
    ('A'    , 'Adjective'),
    ('Adv'  , 'Adverb'),
    ('Art'  , 'Article'),
    ('Cond' , 'Conditional'),
    ('Conj' , 'Conjunction'),
    ('Cor'  , 'Correlative'),
    ('DemP' , 'Demonstrative Pronoun'),
    ('ImpP' , 'Impersonal Pronoun'),
    ('Intg' , 'Interrogative'),
    ('Intj' , 'Interjection'),
    ('N'    , 'Noun'),
    ('Neg'  , 'Negative'),
    ('Part' , 'Particle'),
    ('Prep' , 'Preposition'),
    ('PerP' , 'Personal Pronoun'),
    ('PosP' , 'Possessive Pronoun'),
    ('RefP' , 'Reflexive Pronoun'),
    ('RelP' , 'Relative Pronoun'),
    ('V'    , 'Verb');

-- ==============================================================================================================================
-- LEXICON SOURCES
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.entry(
    id          TEXT PRIMARY KEY,
    name        TEXT,
    description TEXT
);

INSERT INTO lexicon.entry (id, name, description)
VALUES
    ('AS', 'Abbott Smith',
        'from https://github.com/translatable-exegetical-tools/Abbott-Smith, with corrections and adapted by Tyndale Scholars.'),

    ('ML', 'Middle Liddell',
        'from Perseus - used for meaning in the Brief lexicon when there is no entry by Abbott-Smith (AS)'),

    ('LSJ', 'Liddell-Scott-Jones',
        'from Perseus, with additional features and corrections by Tyndale House, Cambridge.'),

    ('MT', 'Mounce''s Teknia Greek Dictionary',
        'from www.billmounce.com/greek-dictionary (with permission). Used when there is no entry by AS or ML.'),

    ('ABDB', 'Abridged BDB by Online Bible',
        '© Larry Pierce of OnlineBible.net. Permission should be obtained before applying in projects.'),

    ('BDB', 'Brown–Driver–Briggs',
        NULL),

    ('BADG', 'Bauer–Danker–Arndt–Gingrich',
        NULL),

    ('CLBL', 'J. Green''s A Concise Lexicon of the Biblical Languages',
        'Definitions refer to J. Green''s lexicon.'),

    ('TWOT', 'Harris, Archer & Waltke''s Theological Wordbook of the Old Testament',
        'Definitions refer to TWOT.'),

    ('OPEN', 'OpenScripture''s Extended Strong''s',
        'Edited to conform with OpenScripture''s extended Strong''s by Tyndale House Cambridge.');

-- ==============================================================================================================================
-- TRANSLATORS BRIEF LEXICONS
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.data(
    id                  SERIAL PRIMARY KEY,
    e_strong            TEXT,
    d_strong            TEXT UNIQUE,
    d_u_relationship    TEXT,
    u_strong            TEXT,
    text                TEXT,   -- Original Language -> Hebrew or Greek
    transliteration     TEXT,
    morph               TEXT,
    gloss               TEXT,
    meaning             TEXT,
    source_id           INTEGER,
    FOREIGN KEY (source_id) REFERENCES audit.sources (id)
    -- FOREIGN KEY (morph) REFERENCES lexicon.morph_codes (id)
);

-- ==============================================================================================================================
-- LEXICONS -> MORPH CODE MAPPING
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.morph_mapping (
    id              SERIAL PRIMARY KEY,
    data_id         INTEGER,
    position        INTEGER,
    relation_type   TEXT,
    language        CHAR(1),
    sub_code        TEXT,
    FOREIGN KEY (language)  REFERENCES lexicon.language (id),
    FOREIGN KEY (data_id) REFERENCES lexicon.data (id)
    -- FOREIGN KEY (sub_code)  REFERENCES morphology.code (id),
)