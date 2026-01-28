CREATE TABLE audit.license_attribute_mapping (
    mapping_id SERIAL PRIMARY KEY,

    license_id   INT,
    agreement_id INT,

    provider_code  TEXT NOT NULL,
    attribute_code TEXT NOT NULL,

    -- Enforce XOR: either license OR agreement
    CHECK (
        (license_id IS NOT NULL AND agreement_id IS NULL)
        OR
        (license_id IS NULL AND agreement_id IS NOT NULL)
    ),

    FOREIGN KEY (license_id)
        REFERENCES audit.licenses(id)
        ON DELETE CASCADE,

    FOREIGN KEY (agreement_id)
        REFERENCES audit.dbl_agreements(agreement_id)
        ON DELETE CASCADE,

    FOREIGN KEY (provider_code, attribute_code)
        REFERENCES audit.license_attributes(provider_code, attribute_code)
);