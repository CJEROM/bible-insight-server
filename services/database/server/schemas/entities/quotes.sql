
CREATE TABLE IF NOT EXISTS nlp.quotes (
    id              SERIAL PRIMARY KEY,
    text            TEXT,
    quote_start     INTEGER,
    quote_end       INTEGER,
    parent_quote    INTEGER,
    speaker         TEXT,
    audience        TEXT,
    FOREIGN KEY (quote_start) REFERENCES bible.tokens (id) ON DELETE CASCADE,
    FOREIGN KEY (quote_end) REFERENCES bible.tokens (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_quote) REFERENCES nlp.quotes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nlp.quote_attribution (
    id                  SERIAL PRIMARY KEY,
    quote_id            INTEGER,
    entity_id           INTEGER,
    attribution         INTEGER, -- whether Speaker or audience or writer
    type                TEXT,
    FOREIGN KEY (entity_id) REFERENCES bible.entities (id) ON DELETE CASCADE,
    FOREIGN KEY (quote_id) REFERENCES nlp.quotes (id) ON DELETE CASCADE
);

-- Look up table for quote attributions
CREATE TABLE IF NOT EXISTS lookup.quote_attribution_types (
    id                  SERIAL PRIMARY KEY,
    attribution         TEXT,
    type                TEXT,
    description         TEXT
);
