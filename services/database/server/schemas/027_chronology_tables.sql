-- Order of all bible.verses in the bible, can also skip if concurrent sections are read as normal
CREATE TABLE IF NOT EXISTS bible.chronologyoccurence (
    id                  SERIAL PRIMARY KEY,
	chapter_ref			TEXT,
	verse_ref			TEXT
);

CREATE TABLE IF NOT EXISTS bible.chronology (
    id                  SERIAL PRIMARY KEY,
	prev_occurence		INTEGER,
	FOREIGN KEY (prev_occurence) REFERENCES bible.chronologyoccurence (id)
);