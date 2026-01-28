CREATE TABLE audit.licence_attribute_mapping (
    mapping_id SERIAL PRIMARY KEY,

    licence_id   INT,
    agreement_id INT,

    provider_code  TEXT NOT NULL,
    attribute_code TEXT NOT NULL,

    -- Enforce XOR: either licence OR agreement
    CHECK (
        (licence_id IS NOT NULL AND agreement_id IS NULL)
        OR
        (licence_id IS NULL AND agreement_id IS NOT NULL)
    ),

    FOREIGN KEY (licence_id)
        REFERENCES audit.licences(id)
        ON DELETE CASCADE,

    FOREIGN KEY (agreement_id)
        REFERENCES audit.dbl_agreements(agreement_id)
        ON DELETE CASCADE,

    FOREIGN KEY (provider_code, attribute_code)
        REFERENCES audit.licence_attributes(provider_code, attribute_code)
);