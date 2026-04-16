-- step_tokens
-- break down into actual tokens ()

DROP SCHEMA morphology CASCADE;
CREATE SCHEMA morphology;

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
        name            TEXT,
        description     TEXT
);

-- POS (Part Of Speech)
CREATE TABLE IF NOT EXISTS morphology.functions(
        id              SERIAL PRIMARY KEY,
        name            TEXT,
        description     TEXT
);

CREATE TABLE IF NOT EXISTS morphology.feature_values(
        id              SERIAL PRIMARY KEY,
        feature_id      INTEGER,
        value           TEXT,
        description     TEXT,
        FOREIGN KEY (feature_id) REFERENCES morphology.features (id)
);

CREATE TABLE IF NOT EXISTS morphology.derived_feature_values(
        id              SERIAL PRIMARY KEY,
        from_value_id   INTEGER,
        derived_value   INTEGER,    
        FOREIGN KEY (from_value_id) REFERENCES morphology.feature_values (id),
        FOREIGN KEY (derived_value) REFERENCES morphology.feature_values (id)
);

CREATE TABLE IF NOT EXISTS morphology.code_values(
        id              SERIAL PRIMARY KEY,
        code_id         INTEGER,
        value_id        INTEGER,    
        FOREIGN KEY (code_id) REFERENCES morphology.codes (id),
        FOREIGN KEY (value_id) REFERENCES morphology.feature_values (id)
);

CREATE TABLE IF NOT EXISTS morphology.features_rules(
        id              SERIAL PRIMARY KEY,
        feature_id      INTEGER REFERENCES morphology.features (id),
        function_id     INTEGER REFERENCES morphology.functions (id),
        language_id     CHAR(1) REFERENCES lexicon.language (id),
        required        BOOLEAN,
        UNIQUE (feature_id, function_id, language_id)
);

-- ==================================================================================================================================================================

-- NOTE: Currently blank entries on the following for 'Name type' & 'Indeclinable' (chosen to preserve during ingestion for now)

-- SELECT * FROM morphology.codes c
-- JOIN morphology.code_values cv ON c.id = cv.code_id
-- JOIN morphology.feature_values fv ON fv.id = cv.value_id
-- WHERE fv.id IN (1588, 2133);