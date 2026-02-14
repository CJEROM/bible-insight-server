

CREATE TABLE standards.iso15924_scripts (
    code            CHAR(4) PRIMARY KEY,  -- e.g. Latn
    numeric         CHAR(3) UNIQUE NOT NULL, -- e.g. 215
    name            VARCHAR(100) NOT NULL,
    unicode_age     VARCHAR(10),
    date_added      DATE
);