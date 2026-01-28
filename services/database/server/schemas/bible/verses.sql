CREATE TABLE IF NOT EXISTS bible.verses (
    id              SERIAL PRIMARY KEY,
    chapter_ref     TEXT,
    verse_ref       TEXT UNIQUE,
    verse           TEXT,
    standard        BOOLEAN DEFAULT TRUE, -- Whether this is standard verse or weird combo verse e.g. GEN 1:1-2
    FOREIGN KEY (chapter_ref) REFERENCES bible.chapters (chapter_ref) ON DELETE CASCADE
);
CREATE INDEX idx_bible_verses_chapter_ref ON bible.verses (chapter_ref);
CREATE INDEX idx_bible_verses_verse_ref ON bible.verses (verse_ref);

-- For linking non standard verses to their normal counter parts e.g. GEN 1:1-2 => GEN 1:1, GEN 1:2
CREATE TABLE IF NOT EXISTS bible.verse_correction (
    id                          SERIAL PRIMARY KEY,
    non_standard_verse_ref      TEXT,
    verse_ref                   TEXT,
    FOREIGN KEY (non_standard_verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE
);
CREATE INDEX idx_bible_verse_correction_non_standard_verse_ref ON bible.verse_correction (non_standard_verse_ref);
CREATE INDEX idx_bible_verse_correction_verse_ref ON bible.verse_correction (verse_ref);

CREATE TABLE IF NOT EXISTS bible.verseoccurences (
    id                      SERIAL PRIMARY KEY,
    verse_ref               TEXT,
    chapter_id              INTEGER, --Chapter Occurence this is under
    book_map_id             INTEGER,
    translation_id          INTEGER,
    start_node              INTEGER,
    end_node                INTEGER,
    FOREIGN KEY (chapter_id) REFERENCES bible.chapteroccurences (id) ON DELETE CASCADE,
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (start_node) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (end_node) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE
);
CREATE INDEX idx_bible_verseoccurences_verse_ref ON bible.verseoccurences (verse_ref);
CREATE INDEX idx_bible_verseoccurences_chapter_id ON bible.verseoccurences (chapter_id);
CREATE INDEX idx_bible_verseoccurences_book_map_id ON bible.verseoccurences (book_map_id);
CREATE INDEX idx_bible_verseoccurences_translation_id ON bible.verseoccurences (translation_id);

CREATE TABLE IF NOT EXISTS bible.excludedverses (
    id              SERIAL PRIMARY KEY,
    verse_ref       TEXT,
    translation_id  INTEGER,
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE
);
CREATE INDEX idx_bible_excludedverses_translation_id ON bible.excludedverses (translation_id);
