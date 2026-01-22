CREATE TABLE IF NOT EXISTS entity.entities (
    id              SERIAL PRIMARY KEY
);

-- This will also count as Entity Names to some degree since we are counting each occurence and mentions of them, but this could have start and end
CREATE TABLE IF NOT EXISTS entity.entityoccurence (
    id              SERIAL PRIMARY KEY,
	start_token		INTEGER,
	end_token   	INTEGER,
	FOREIGN KEY (start_token) REFERENCES bible.tokens (id) ON DELETE CASCADE,
	FOREIGN KEY (end_token) REFERENCES bible.tokens (id) ON DELETE CASCADE
);

-- Will act as lookup not so much as source of truth, tho it can, and definetly something to work on
-- e.g. CHILD_OF, PARENT_OF, SON_OF, DAUGHTER_OF
-- CREATE TABLE IF NOT EXISTS lookup.entity_relationship_types (
--     id              SERIAL PRIMARY KEY,
-- 	relationship    TEXT UNIQUE,
--     description     TEXT
-- );

-- Intended to work on showing relationship in different directions e.g. PARENT_OF, flipped will show CHILD_OF, and can also be SON_OF or DAUGHTER_OF
-- CREATE TABLE IF NOT EXISTS lookup.entity_relationship_map (
--     id              SERIAL PRIMARY KEY,
-- 	relationship    TEXT,
--     RTL             TEXT,
--     FOREIGN KEY (relationship) REFERENCES lookup.entity_relationship_types (relationship) ON DELETE SET NULL
-- );

CREATE TABLE IF NOT EXISTS entity.entity_relationships (
    id              SERIAL PRIMARY KEY,
	from_entity		INTEGER,
	to_entity	    INTEGER,
    relationship    TEXT,
	FOREIGN KEY (from_entity) REFERENCES entity.entities (id) ON DELETE CASCADE,
    FOREIGN KEY (to_entity) REFERENCES entity.entities (id) ON DELETE CASCADE
	-- FOREIGN KEY (relationship) REFERENCES lookup.entity_relationship_types (relationship) ON DELETE CASCADE
);