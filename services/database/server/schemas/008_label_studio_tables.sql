CREATE TABLE IF NOT EXISTS nlp.labellingprojects (
    id                  INTEGER PRIMARY KEY,
    name                TEXT,   
    description         TEXT,
    exports             INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS nlp.translationlabellingprojects (
    id                  SERIAL PRIMARY KEY,
    translation_id      INTEGER,
    project_id          INTEGER,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES nlp.labellingprojects (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nlp.labellingfiles (
    id                  SERIAL PRIMARY KEY,
    file_id             INTEGER,
    project_id          INTEGER,
    FOREIGN KEY (project_id) REFERENCES nlp.labellingprojects (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);