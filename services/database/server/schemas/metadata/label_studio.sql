CREATE TABLE IF NOT EXISTS nlp.labelling_projects (
    id                  INTEGER PRIMARY KEY,
    name                TEXT,   
    description         TEXT,
    exports             INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS nlp.translation_labelling_projects (
    id                  SERIAL PRIMARY KEY,
    translation_id      INTEGER,
    project_id          INTEGER,
    FOREIGN KEY (translation_id) REFERENCES bible.translations (id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES nlp.labellingprojects (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nlp.labelling_files (
    id                  SERIAL PRIMARY KEY,
    file_id             INTEGER,
    project_id          INTEGER,
    FOREIGN KEY (project_id) REFERENCES nlp.labelling_projects (id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES audit.files (id)
);