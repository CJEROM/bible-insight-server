-- This could potentially be used for publically shared notes for example

-- Audit type notes could potentially be compressed to save on storage + enhance security, or kept raw.
-- Could perhaps differentiate between when shared and when created by local and server versions

CREATE TABLE IF NOT EXISTS users.notes (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMP,
    modified_at     TIMESTAMP,
    complete_at     TIMESTAMP,
    title           TEXT,
    content         TEXT,
    tags            TEXT,
	user_id			INTEGER,
	FOREIGN KEY (user_id) REFERENCES users.users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS users.note_audits (
    id              SERIAL PRIMARY KEY,
    modified_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title           TEXT,
    content         TEXT,
    tags            TEXT,
	user_id			INTEGER,
    note_id         INTEGER,
	FOREIGN KEY (user_id) REFERENCES users.users (id) ON DELETE SET NULL,
    FOREIGN KEY (note_id) REFERENCES users.notes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users.note_relationships (
    id              SERIAL PRIMARY KEY,
    note_from    	INTEGER,
    note_to         INTEGER, 
	type			TEXT,
    FOREIGN KEY (note_from) REFERENCES users.notes (id),
	FOREIGN KEY (note_to) REFERENCES users.notes (id)
);

CREATE TABLE IF NOT EXISTS users.note_relationship_audits (
    id                      SERIAL PRIMARY KEY,
    note_from    	        INTEGER,
    note_to                 INTEGER, 
	type			        TEXT,
    modified_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note_relationship_id    INTEGER,
    FOREIGN KEY (note_from) REFERENCES users.notes (id),
	FOREIGN KEY (note_to) REFERENCES users.notes (id),
    FOREIGN KEY (note_relationship_id) REFERENCES users.note_relationships (id)
);

CREATE TABLE IF NOT EXISTS users.userhighlightsanchors (
    id              SERIAL PRIMARY KEY,
    node_id         INTEGER, 
	start_char		INTEGER,
	end_char		INTEGER,
	FOREIGN KEY (node_id) REFERENCES bible.nodes (id)
);

CREATE TABLE IF NOT EXISTS users.userhighlights (
    id              SERIAL PRIMARY KEY,
    start_anchor	INTEGER,
    end_anchor      INTEGER,
	color			TEXT,
    FOREIGN KEY (start_anchor) REFERENCES users.userhighlightsanchors (id) ON DELETE CASCADE,
	FOREIGN KEY (end_anchor) REFERENCES users.userhighlightsanchors (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users.readhistory (
    history_id              SERIAL PRIMARY KEY,
    date_time               TEXT DEFAULT CURRENT_TIMESTAMP,
    book_map_id             INTEGER,
    scripture_reference     TEXT,
	user_id					INTEGER,
    FOREIGN KEY (book_map_id) REFERENCES bible.booktofile (id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES users.users (id)
);