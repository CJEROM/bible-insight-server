DROP SCHEMA IF EXISTS lexicon CASCADE;
CREATE SCHEMA lexicon;

-- ==============================================================================================================================
-- LANGUAGE
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.language(
    id      TEXT PRIMARY KEY,
    name    TEXT,
    iso     CHAR(3),
    FOREIGN KEY (iso) REFERENCES standards.iso693_3_codes (id)
);

-- Language is A=Aramaic, H=Hebrew, G=Greek and N=Name (not language specific)
INSERT INTO lexicon.language (id, name, iso)
VALUES
    ('A', 'Aramaic' , 'arc'),
    ('H', 'Hebrew'  , 'hbo'), -- Ancient Hebrew
    ('G', 'Greek'   , 'grc'),
    ('N', 'Name'    , NULL);

-- ==============================================================================================================================
-- TYPE (PART OF SPEECH)
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.type(
    id      TEXT PRIMARY KEY,
    name    TEXT
);

-- Type is A=Adjective, Adv=Adverb, Art=Article, etc.
INSERT INTO lexicon.type (id, name)
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
-- GENDER
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.gender(
    id      TEXT PRIMARY KEY,
    name    TEXT
);

-- Gender is F=Female, M=Male, N=Neuter, C=Common, P=Plural, S=Singular
INSERT INTO lexicon.gender (id, name)
VALUES
    ('F', 'Female'),
    ('M', 'Male'),
    ('N', 'Neuter'),
    ('C', 'Common'),
    ('P', 'Plural'),
    ('S', 'Singular');

-- ==============================================================================================================================
-- EXTRA (FOR NAMES)
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.extra(
    id      TEXT PRIMARY KEY,
    name    TEXT
);

-- Extra for Names: L=Location, P=Person, LG/PG=Gentilic, T=Title  (i.e. any other capitalised nouns such as titles, months, gods, planets etc)
INSERT INTO lexicon.extra (id, name)
VALUES
    ('L'    , 'Location'),
    ('P'    , 'Person'),
    ('LG'   , 'Gentilic'),
    ('PG'   , 'Gentilic'),
    ('T'    , 'Title');

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
-- TRANSLATORS BRIEF LEXICON (HEBREW)
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.tbesh(
    id                  SERIAL PRIMARY KEY,
    e_strong            TEXT,
    d_strong            TEXT,
    d_u_relationship    TEXT,
    u_strong            TEXT,
    iso                 TEXT,
    text                TEXT,   -- Original Language -> Hebrew
    transliteration     TEXT,
    morph               TEXT,
    gloss               TEXT,
    meaning             TEXT
);

-- ==============================================================================================================================
-- TRANSLATORS BRIEF LEXICON (GREEK)
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.tbesg(
    id                  SERIAL PRIMARY KEY,
    e_strong            TEXT,
    d_strong            TEXT,
    d_u_relationship    TEXT,
    u_strong            TEXT,
    iso                 TEXT,
    text                TEXT,   -- Original Language -> Greek
    transliteration     TEXT,
    morph               TEXT,
    gloss               TEXT,
    meaning             TEXT,
    other_lexicon       TEXT    -- Abbot-Smith lexicon (AS), with gaps occassionally filled from edited versions of Middle LSJ
);

-- ==============================================================================================================================
-- TRANSLATORS FORMATTED LSJ
-- ==============================================================================================================================

CREATE TABLE IF NOT EXISTS lexicon.tflsj(
    id                  SERIAL PRIMARY KEY,
    e_strong            TEXT,
    d_strong            TEXT,
    d_u_relationship    TEXT,
    u_strong            TEXT,
    iso                 TEXT,
    text                TEXT,   -- Original Language -> Greek
    transliteration     TEXT,
    morph               TEXT,
    gloss               TEXT,
    meaning             TEXT    -- LSJ Meaning
);