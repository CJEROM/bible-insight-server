
DROP SCHEMA stepbible CASCADE;
CREATE SCHEMA stepbible;

CREATE TABLE stepbible.tagnt (
        id                      SERIAL PRIMARY KEY,
        verse                   TEXT,
        word_position           TEXT,
        word_type               TEXT,
        greek                   TEXT,
        transliteration         TEXT,
        english                 TEXT,
        d_strong                TEXT,
        grammar                 TEXT,
        dictionary_form         TEXT,
        gloss                   TEXT,
        editions                TEXT,
        meaning_variants        TEXT,
        spelling_variants       TEXT,
        spanish                 TEXT,
        sub_meanings            TEXT,
        conjoined_data          TEXT,
        s_strong                TEXT,
        instance                TEXT,
        alt_strongs             TEXT,
        variant_notes           TEXT
);

-- SELECT DISTINCT word_type
-- FROM stepbible.tagnt;

-- SELECT DISTINCT instance
-- FROM stepbible.tagnt
-- WHERE instance LIKE '%\_%' ESCAPE '\';

-- POTENTIALLY RECREATE EACH ENTRY PER TRANSLATION

-- MAPPING TABLE WITH POTENTIAL OVERRIDES FOR SPECIFIC TRANSLATIONS


