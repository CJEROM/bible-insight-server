CREATE TABLE IF NOT EXISTS bible.chapters (
    id                      SERIAL PRIMARY KEY,
    book_code               TEXT,
    chapter_num             INTEGER,
    chapter_ref             TEXT UNIQUE,
    standard                BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (book_code) REFERENCES bible.books (code) ON DELETE CASCADE
);
CREATE INDEX idx_bible_chapters_book_code ON bible.chapters (book_code);
CREATE INDEX idx_bible_chapters_chapter_ref ON bible.chapters (chapter_ref);

-- Either an audio file or text file from book
CREATE TABLE IF NOT EXISTS bible.chapteroccurences (
    id                      SERIAL PRIMARY KEY,
    chapter_ref             TEXT,
    translation_id          INTEGER,
    file_id            		INTEGER, -- audio_file
    book_map_id             INTEGER, -- usx_file
    start_node              INTEGER, -- usx_file
    end_node                INTEGER, -- usx_file
    reconstructed_text      TEXT,
    FOREIGN KEY (start_node) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (end_node) REFERENCES bible.nodes (id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_ref) REFERENCES bible.chapters (chapter_ref),
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id),
    FOREIGN KEY (file_id) REFERENCES audit.files (id) ON DELETE CASCADE
);
CREATE INDEX idx_bible_chapteroccurences_chapter_ref ON bible.chapteroccurences (chapter_ref);
CREATE INDEX idx_bible_chapteroccurences_translation_id ON bible.chapteroccurences (translation_id);
CREATE INDEX idx_bible_chapteroccurences_file_id ON bible.chapteroccurences (file_id) WHERE file_id IS NOT NULL;
CREATE INDEX idx_bible_chapteroccurences_book_map_id ON bible.chapteroccurences (book_map_id) WHERE book_map_id IS NOT NULL;