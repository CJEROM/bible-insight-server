CREATE TABLE IF NOT EXISTS audit.dbl_agreements (
    agreement_id        INTEGER PRIMARY KEY,
    dbl_id              TEXT NOT NULL, --

    -- Link to the actual license document/file
    licence_file_id     INTEGER  NOT NULL,
    base_licence_id     INTEGER, -- Licence to extend current one

    notes               TEXT,

    FOREIGN KEY (dbl_id) REFERENCES audit.dbl_info(dbl_id),
    FOREIGN KEY (base_licence_id) REFERENCES audit.licences(id),
    FOREIGN KEY (licence_file_id) REFERENCES audit.files(id)
);

-- Agreement-specific attributes (DBL publication rights, custom overrides)
--      Attributes to function like PERMISSION when TRUE, and RESTRICITON when FALSE
CREATE TABLE audit.agreement_attributes (
    agreement_id    INTEGER NOT NULL,
    attribute_code  TEXT NOT NULL,
    
    -- Specific value for this agreement
    attribute_value TEXT,  -- 'true', 'false', or specific details
    
    PRIMARY KEY (agreement_id, attribute_code),
    FOREIGN KEY (agreement_id) REFERENCES audit.agreements(id) ON DELETE CASCADE,
    FOREIGN KEY (attribute_code) REFERENCES audit.licence_attributes(attribute_code)
);

-- Link agreements to specific revisions (some may overlap, the latter agreement applies)
-- Currently not needed (see how it may go in future), with controlled
--      "access granted per revision? or whole translation?"
CREATE TABLE IF NOT EXISTS audit.dbl_revision_agreements (
    id                  SERIAL PRIMARY KEY,
    agreement_id        INTEGER,
    revision            INTEGER,
    -- active              BOOLEAN DEFAULT TRUE, -- If multiple terms exist for same revision -> FALSE
    UNIQUE (agreement_id, revision),
    FOREIGN KEY (agreement_id) REFERENCES audit.dbl_agreements(agreement_id) ON DELETE CASCADE
);