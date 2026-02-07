-- Order of all bible.verses in the bible, can also skip if concurrent sections are read as normal
CREATE TABLE IF NOT EXISTS structure.chronology (
    id                  SERIAL PRIMARY KEY,
	chapter_ref			TEXT,
	verse_ref			TEXT,
	order_num			INTEGER,
	version				INTEGER
);