-- Used to store unique list of words used for this bible translation to use as initial list to check against
CREATE TABLE IF NOT EXISTS bible.word_list (
    id              SERIAL PRIMARY KEY,
    text            TEXT NOT NULL UNIQUE,   -- unique word
    lemma_id        INTEGER,                    -- root/lemma (self-reference if needed)
    nlp             BOOLEAN DEFAULT FALSE,
    type            TEXT,
    language_iso    TEXT,
    FOREIGN KEY (lemma_id) REFERENCES bible.word_list (id) ON DELETE SET NULL,
    FOREIGN KEY (language_iso) REFERENCES bible.languages (iso)  ON DELETE CASCADE
);

-- Meant to be used in labelling for specific tokens to show they are of specific interest to me for labelling or mapping extra information
CREATE TABLE IF NOT EXISTS lookup.word_tags (
    id                  SERIAL PRIMARY KEY,
    name                TEXT UNIQUE NOT NULL, -- e.g. "Person", "Location", "Entity"
    description         TEXT
);

-- Only storing important bible.tokens
CREATE TABLE IF NOT EXISTS bible.tokens (
    id                      SERIAL PRIMARY KEY,
    text                    TEXT,
    chapter_occurence_id    INTEGER,
    chapter_start_offset    INTEGER,
    chapter_end_offset      INTEGER, 
    pos                     TEXT, -- Info that is populate later
    tag                     TEXT,
    dep                     TEXT,
    head_token_id           INTEGER,
    lemma_id                TEXT,
    trailing_space          BOOLEAN,
    is_alpha                BOOLEAN,
    is_punct                BOOLEAN,
    is_space                BOOLEAN,
    is_quote                BOOLEAN,
    is_left_punct           BOOLEAN,
    is_right_punct          BOOLEAN,
    like_num                BOOLEAN,
    language_id             INTEGER,
    translation_id          INTEGER,
    FOREIGN KEY (chapter_occurence_id) REFERENCES bible.chapteroccurences (id),
    FOREIGN KEY (head_token_id) REFERENCES bible.tokens (id),
    FOREIGN KEY (pos) REFERENCES lookup.nlp_pos_types (pos_tag),
    FOREIGN KEY (tag) REFERENCES lookup.nlp_tag_types (tag),
    FOREIGN KEY (dep) REFERENCES lookup.nlp_dep_types (dep),
    FOREIGN KEY (language_id) REFERENCES bible.languages (id),
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id)
);
CREATE INDEX idx_bible_tokens_text ON bible.tokens (text);
CREATE INDEX idx_bible_tokens_chapter_occurence_id ON bible.tokens (chapter_occurence_id);
CREATE INDEX idx_bible_tokens_chapter_start_offset ON bible.tokens (chapter_start_offset);
CREATE INDEX idx_bible_tokens_chapter_end_offset ON bible.tokens (chapter_end_offset);
CREATE INDEX idx_bible_tokens_head_token_id ON bible.tokens (head_token_id);
CREATE INDEX idx_bible_tokens_lemma_id ON bible.tokens (lemma_id);
CREATE INDEX idx_bible_tokens_pos ON bible.tokens (pos);
CREATE INDEX idx_bible_tokens_language_id ON bible.tokens (language_id);
CREATE INDEX idx_bible_tokens_translation_id ON bible.tokens (translation_id);