CREATE TABLE IF NOT EXISTS lookup.node_attribute_types (
    id                      SERIAL PRIMARY KEY,
    attribute               TEXT UNIQUE,
    description             TEXT,
    active                  BOOLEAN
);

-- For all the node types e.g. <para>
CREATE TABLE IF NOT EXISTS lookup.node_types (
    id                      SERIAL PRIMARY KEY,
    node                    TEXT UNIQUE,
    description             TEXT,
    active                  BOOLEAN
);

-- Maps the different attributes to node types
CREATE TABLE IF NOT EXISTS lookup.node_map (
    id                      SERIAL PRIMARY KEY,
    node_type               TEXT,
    node_attribute          TEXT,
    UNIQUE(node_type, node_attribute), -- Unique combinations of what attributes and nodes go together
    FOREIGN KEY (node_type) REFERENCES lookup.node_types (node),
    FOREIGN KEY (node_attribute) REFERENCES lookup.node_attribute_types (attribute)
);

-- Shows what possibilities could happen with a node_type and the parent node to recreate the tree structure
CREATE TABLE IF NOT EXISTS lookup.node_tree (
    id                      SERIAL PRIMARY KEY,
    node_parent             TEXT,
    node_child              TEXT,
    FOREIGN KEY (node_parent) REFERENCES lookup.node_types (node),
    FOREIGN KEY (node_child) REFERENCES lookup.node_types (node)
);

-- Shows in what combinations a node can come up
CREATE TABLE IF NOT EXISTS lookup.node_options (
    id                      SERIAL PRIMARY KEY,
    node_type               TEXT,
    node_attribute          TEXT,
    option                  INTEGER,
    node_tree_id            INTEGER,
    FOREIGN KEY (node_type, node_attribute) REFERENCES lookup.node_map (node_type, node_attribute),
    FOREIGN KEY (node_type) REFERENCES lookup.node_types (node),
    FOREIGN KEY (node_attribute) REFERENCES lookup.node_attribute_types (attribute),
    FOREIGN KEY (node_tree_id) REFERENCES lookup.node_tree (id)
);

-- Built for speed, so very denormalised and flat which is what it needs to be
CREATE TABLE IF NOT EXISTS bible.nodes (
    id                      SERIAL PRIMARY KEY,
    node_text               TEXT,
    node_type               TEXT,
    code                    TEXT,
    sid                     TEXT,
    eid                     TEXT,
    vid                     TEXT,
    style                   TEXT,
    number                  TEXT,
    caller                  TEXT,
    closed                  TEXT,
    version                 TEXT,
    strong                  TEXT,
    loc                     TEXT,
    align                   TEXT,
    parent_node_id          INTEGER, -- Can be null due to usx root node
    index_in_parent         INTEGER,
    book_map_id             INTEGER,
    translation_id          INTEGER,
    canonical_path          TEXT,
    is_tokenisable          BOOLEAN,
    chapter_start_offset    INTEGER,
    chapter_end_offset      INTEGER,
    FOREIGN KEY (parent_node_id) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (node_type) REFERENCES lookup.node_types (node) ON DELETE CASCADE
    -- Comment out or change this link in the future when switching over to new lexemes
    -- FOREIGN KEY (strong) REFERENCES bible.lexemes (strongs_code) ON DELETE CASCADE
);
CREATE INDEX idx_bible_nodes_node_text ON bible.nodes (node_text) WHERE is_tokenisable = TRUE;
CREATE INDEX idx_bible_nodes_sid ON bible.nodes (sid) WHERE sid IS NOT NULL;
CREATE INDEX idx_bible_nodes_eid ON bible.nodes (eid) WHERE eid IS NOT NULL;
CREATE INDEX idx_bible_nodes_strong ON bible.nodes (strong) WHERE strong IS NOT NULL;
CREATE INDEX idx_bible_nodes_parent_node_id ON bible.nodes (parent_node_id);
CREATE INDEX idx_bible_nodes_book_map_id ON bible.nodes (book_map_id);
CREATE INDEX idx_bible_nodes_translation_id ON bible.nodes (translation_id);

-- Current nodes table is following stable USX, for new attributes, assign in nodes_extended, to add flexibility
CREATE TABLE IF Not EXISTS bible.nodes_attributes (
    id                      SERIAL PRIMARY KEY,
    node_id                 INTEGER,
    node_attribute          TEXT,
    value                   TEXT,
    FOREIGN KEY (node_id) REFERENCES bible.nodes (id),
    FOREIGN KEY (node_attribute) REFERENCES lookup.node_attribute_types (attribute)
);