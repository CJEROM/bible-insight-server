-- Consider turning into unique instance for controlling bible.styles across all bible.translations instead, like default settings
CREATE TABLE IF NOT EXISTS bible.styles (
    id                  SERIAL PRIMARY KEY,
    style               TEXT,
    name                TEXT,
    description         TEXT,
    versetext           BOOLEAN,
    publishable         BOOLEAN,
    source_file_id      INTEGER,
    FOREIGN KEY (source_file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);
CREATE INDEX idx_bible_styles_file ON bible.styles (source_file_id);
CREATE INDEX idx_bible_styles_style ON bible.styles (style);

CREATE TABLE IF NOT EXISTS bible.properties (
    id                  SERIAL PRIMARY KEY,
    name                TEXT,
    value               TEXT,
    unit                TEXT,
    style_id            INTEGER,
    FOREIGN KEY (style_id) REFERENCES bible.styles (id) ON DELETE CASCADE
);