
-- ==============================================================================================================================
-- LANGUAGE
-- ==============================================================================================================================

DROP SCHEMA IF EXISTS lexicon CASCADE;
CREATE SCHEMA lexicon;

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