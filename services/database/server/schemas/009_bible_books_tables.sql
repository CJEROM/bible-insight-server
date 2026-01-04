CREATE TABLE IF NOT EXISTS bible.books (
    id              SERIAL PRIMARY KEY,
    code            TEXT UNIQUE,
	total_chapters	INTEGER
);
CREATE INDEX idx_bible_books_code ON bible.books (code);

CREATE TABLE IF NOT EXISTS bible.booktofile (
    id              SERIAL PRIMARY KEY,
    book_code       TEXT,
    translation_id  INTEGER,
    file_id         INTEGER,
    short           TEXT, -- Short Name for the book
    long            TEXT, -- Long Name for the book
    FOREIGN KEY (book_code) REFERENCES bible.books (code) ON DELETE CASCADE,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES bible.files (id) ON DELETE CASCADE
);
CREATE INDEX idx_bible_booktofile_book_code ON bible.booktofile (book_code);
CREATE INDEX idx_bible_booktofile_translation_id ON bible.booktofile (translation_id);

CREATE TABLE IF NOT EXISTS bible.bookgroups (
    id              SERIAL PRIMARY KEY,
    testament       BOOLEAN,
    level           INTEGER
);

CREATE TABLE IF NOT EXISTS bible.booktogroup (
    book_id         INTEGER,
    book_group_id   INTEGER,
    PRIMARY KEY (book_id, book_group_id),
    FOREIGN KEY (book_id) REFERENCES bible.books (id) ON DELETE CASCADE,
    FOREIGN KEY (book_group_id) REFERENCES bible.bookgroups (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bible.bookgroupnames (
    id              SERIAL PRIMARY KEY,
    book_group_id   INTEGER,
    language_id     INTEGER,
    name            TEXT,
    FOREIGN KEY (book_group_id) REFERENCES bible.bookgroups (id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES bible.languages (id) ON DELETE CASCADE
);
