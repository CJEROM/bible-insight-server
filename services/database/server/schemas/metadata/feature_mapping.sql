-- Map features possible for translation (using license and agreement data as well as the data contents)
CREATE TABLE audit.features (
    feature_code    TEXT PRIMARY KEY,
    name            TEXT,
    description     TEXT,
    active          BOOLEAN DEFAULT TRUE,
    testing         BOOLEAN DEFAULT FALSE
);

-- Features link to:
--      Sources (Dataset / File)
--      Licenses
--      Agreements
--      Translations

CREATE TABLE audit.feature_mapping (
    mapping_id      SERIAL PRIMARY KEY,
    feature_code    TEXT NOT NULL,
    source_id       INTEGER,
    license_id      INTEGER,
    agreement_id    INTEGER,
    translation_id  INTEGER,
    is_allowed      BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (feature_code) REFERENCES audit.features(feature_code),
    FOREIGN KEY (source_id) REFERENCES audit.sources(id),
    FOREIGN KEY (license_id) REFERENCES audit.licenses(id),
    FOREIGN KEY (agreement_id) REFERENCES audit.dbl_agreements(agreement_id),
    FOREIGN KEY (translation_id) REFERENCES bible.translations(id)
);