-- For parts of scripture talking about same period, and how it aligns e.g. Gospels
CREATE TABLE IF NOT EXISTS bible.harmonies (
    id                  SERIAL PRIMARY KEY,
	description			TEXT,
	order_num			INTEGER
);

CREATE TABLE IF NOT EXISTS bible.harmonymapping (
    harmony_id          INTEGER,
	verse_ref			TEXT,
	PRIMARY KEY (harmony_id, verse_ref),
	FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);