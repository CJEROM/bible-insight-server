-- Consider Amending Tables so that can also include 

CREATE TABLE IF NOT EXISTS bible.translationrefnotes (
    id                      SERIAL PRIMARY KEY,
    from_verse_ref          TEXT,
    from_chapter_ref        TEXT,
    to_verse_ref            TEXT,
    to_chapter_ref          TEXT, -- Footnote can link to chapter instead (e.g. PSA 9:0) which doesn't qualify as non standard verse
    node_id                 INTEGER,
    FOREIGN KEY (node_id) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (from_verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (from_chapter_ref) REFERENCES bible.chapters (chapter_ref) ON DELETE CASCADE,
    FOREIGN KEY (to_verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (to_chapter_ref) REFERENCES bible.chapters (chapter_ref) ON DELETE CASCADE
);
CREATE INDEX idx_bible_translationrefnotes_from_verse_ref ON bible.translationrefnotes (from_verse_ref) WHERE from_verse_ref IS NOT NULL;
CREATE INDEX idx_bible_translationrefnotes_from_chapter_ref ON bible.translationrefnotes (from_chapter_ref) WHERE from_chapter_ref IS NOT NULL;
CREATE INDEX idx_bible_translationrefnotes_to_verse_ref ON bible.translationrefnotes (to_verse_ref) WHERE to_verse_ref IS NOT NULL;
CREATE INDEX idx_bible_translationrefnotes_to_chapter_ref ON bible.translationrefnotes (to_chapter_ref) WHERE to_chapter_ref IS NOT NULL;
