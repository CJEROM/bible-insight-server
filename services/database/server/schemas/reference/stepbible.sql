-- step_tokens
-- break down into actual tokens ()

DROP SCHEMA stepbible CASCADE;
CREATE SCHEMA stepbible;

DROP SCHEMA morphology CASCADE;
CREATE SCHEMA morphology;

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

-- SELECT DISTINCT d_strong
-- FROM stepbible.tagnt;
-- SELECT DISTINCT d_strong
-- FROM stepbible.tagnt;

-- SELECT DISTINCT grammar
-- FROM stepbible.tagnt;

-- SELECT DISTINCT editions
-- FROM stepbible.tagnt;

-- SELECT DISTINCT s_strong
-- FROM stepbible.tagnt;

-- SELECT DISTINCT spelling_variants
-- FROM stepbible.tagnt;

-- SELECT DISTINCT meaning_variants
-- FROM stepbible.tagnt;

-- SELECT DISTINCT dictionary_form
-- FROM stepbible.tagnt;

-- SELECT DISTINCT grammar
-- FROM stepbible.tagnt;

-- SELECT DISTINCT instance
-- FROM stepbible.tagnt
-- WHERE instance LIKE '%\_%' ESCAPE '\';
-- SELECT DISTINCT grammar
-- FROM stepbible.tagnt;

-- SELECT DISTINCT editions
-- FROM stepbible.tagnt;

-- SELECT DISTINCT s_strong
-- FROM stepbible.tagnt;

-- SELECT DISTINCT spelling_variants
-- FROM stepbible.tagnt;

-- SELECT DISTINCT meaning_variants
-- FROM stepbible.tagnt;

-- SELECT DISTINCT instance
-- FROM stepbible.tagnt;

-- SELECT DISTINCT instance
-- FROM stepbible.tagnt
-- WHERE instance LIKE '%\_%' ESCAPE '\';

-- SELECT DISTINCT sub_meanings
-- FROM stepbible.tagnt;
-- SELECT DISTINCT instance
-- FROM stepbible.tagnt;

-- SELECT DISTINCT instance
-- FROM stepbible.tagnt
-- WHERE instance LIKE '%\_%' ESCAPE '\';

-- SELECT DISTINCT sub_meanings
-- FROM stepbible.tagnt;

-- SELECT DISTINCT alt_strongs
-- FROM stepbible.tagnt;

-- SELECT DISTINCT variant_notes
-- FROM stepbible.tagnt;
-- POTENTIALLY RECREATE EACH ENTRY PER TRANSLATION

-- MAPPING TABLE WITH POTENTIAL OVERRIDES FOR SPECIFIC TRANSLATIONS




-- ==============================================================================================================================

-- CREATE TABLE IF NOT EXISTS morphology.systems(
--         id              SERIAL PRIMARY KEY,
--         code            TEXT UNIQUE,
--         name            TEXT,
--         description     TEXT,
--         source_id       INTEGER,
--         language_scope  TEXT,
--         FOREIGN KEY (source_id) REFERENCES audit.sources (id)
--         FOREIGN KEY (language_scope) REFERENCES standards.iso693_3_codes (id)
-- );
-- INSERT INTO morphology.systems (code, name, description, source_id, language_scope)
-- VALUES
--         ("", "", "", , "grc"),  -- Ancient Greek
--         ("", "", "", , "hbo");  -- Ancient Hebrew
--         -- ("", "", "", , "heb")        -- Modern Hebrew
        -- ("", "", "", , "arc")        -- 


-- ==================================================================================================================================================================

CREATE TABLE IF NOT EXISTS morphology.codes(
        id              SERIAL PRIMARY KEY,
        code            TEXT UNIQUE,
        morphology      TEXT,
        explanation     TEXT,
        example         TEXT,
        source_id       INTEGER,
        iso             TEXT,           -- Language code
        raw_data        TEXT,
        FOREIGN KEY (source_id) REFERENCES audit.sources (id),
        FOREIGN KEY (iso) REFERENCES standards.iso693_3_codes (id)
);

-- ==================================================================================================================================================================

CREATE TABLE IF NOT EXISTS morphology.features(
        id              SERIAL PRIMARY KEY,
        name            TEXT UNIQUE,
        description     TEXT
);
-- INSERT INTO morphology.features ()
-- VALUES
--         (),
--         ();

CREATE TABLE IF NOT EXISTS morphology.feature_values(
        id              SERIAL PRIMARY KEY,
        feature_id      INTEGER,
        feature         TEXT,
        value           TEXT,
        description     TEXT,
        UNIQUE (feature_id, value),
        FOREIGN KEY (feature_id) REFERENCES morphology.features (id)
);

CREATE TABLE IF NOT EXISTS morphology.derived_feature_values(
        id              SERIAL PRIMARY KEY,
        from_value_id   INTEGER,
        derived_value   INTEGER,    
        FOREIGN KEY (from_value_id) REFERENCES morphology.feature_values (id),
        FOREIGN KEY (derived_value) REFERENCES morphology.feature_values (id)
);

-- ==================================================================================================================================================================
