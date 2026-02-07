CREATE TABLE IF NOT EXISTS bible.paragraphs ( -- DEPRECATED
    id              SERIAL PRIMARY KEY,
    node_id         INTEGER,
    style_id        INTEGER,
    parent_para     INTEGER, -- For establishing logical paragraphs through grouping
    is_versetext    BOOLEAN,
    FOREIGN KEY (parent_para) REFERENCES bible.paragraphs (id) ON DELETE SET NULL,
    FOREIGN KEY (node_id) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (style_id) REFERENCES bible.styles (id) ON DELETE CASCADE
);