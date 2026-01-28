CREATE TABLE IF NOT EXISTS bible.translationfootnotes (
    id                      SERIAL PRIMARY KEY,
    verse_ref               TEXT,
    chapter_ref             TEXT, -- Footnote can link to chapter instead (e.g. PSA 9:0) which doesn't qualify as non standard verse
    node_id                 INTEGER,
    FOREIGN KEY (node_id) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (chapter_ref) REFERENCES bible.chapters (chapter_ref) ON DELETE CASCADE
);
CREATE INDEX idx_bible_translationfootnotes_verse_ref ON bible.translationfootnotes (verse_ref) WHERE verse_ref IS NOT NULL;
CREATE INDEX idx_bible_translationfootnotes_chapter_ref ON bible.translationfootnotes (chapter_ref) WHERE chapter_ref IS NOT NULL;
CREATE INDEX idx_bible_translationfootnotes_node_id ON bible.translationfootnotes (node_id);
