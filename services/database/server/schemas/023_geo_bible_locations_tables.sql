-- Location data can be more complicate than this, as can treat these as location reference points (waypoints / landmarks)
--		 so will require rendering in context and showing waypoints relative to area being referred to e.g. for territory 

CREATE TABLE IF NOT EXISTS bible.locations (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT UNIQUE,
    friendly_id         TEXT,
    file_id             INTEGER,
    type                TEXT,
    info                JSON
);

-- Refers to linking a location to a particular verse, and creating all the entries for this.
CREATE TABLE IF NOT EXISTS bible.locationoccurence (
    id                  SERIAL PRIMARY KEY,
    location_id         TEXT,
    verse_ref           TEXT,
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (verse_ref) REFERENCES bible.verses (verse_ref)
);

CREATE TABLE IF NOT EXISTS bible.locationrelationships (
    id                  SERIAL PRIMARY KEY,
    from_location       TEXT,
    to_location         TEXT,
    type                TEXT,
    modifier            TEXT,
    info                TEXT,
    FOREIGN KEY (from_location) REFERENCES bible.locations (location_id),
    FOREIGN KEY (to_location) REFERENCES bible.locations (location_id)
);

CREATE TABLE IF NOT EXISTS bible.geosources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT UNIQUE,
    info                JSON
);

CREATE TABLE IF NOT EXISTS bible.locationdatasources (
    id                  SERIAL PRIMARY KEY,
    source_id           TEXT,
    location_id         TEXT,
    type                TEXT,
    info                JSON,
    FOREIGN KEY (source_id) REFERENCES bible.geosources (source_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);

CREATE TABLE IF NOT EXISTS bible.images (
    id                  SERIAL PRIMARY KEY,
    image_id            TEXT UNIQUE,
    location_id         TEXT,
    file_id             INTEGER,
    info                JSON,
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

CREATE TABLE IF NOT EXISTS bible.locationimages (
    id                  SERIAL PRIMARY KEY,
    image_id            TEXT,
    location_id         TEXT,
    type                TEXT,
    info                JSON,
    FOREIGN KEY (image_id) REFERENCES bible.images (image_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);

-- Not storing it as a file, instead just as entries, due to 
CREATE TABLE IF NOT EXISTS bible.geometries (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT UNIQUE,
    file_id             INTEGER,
    geometries          TEXT,
    source              TEXT,
    surface             TEXT,
    info                JSON,
    FOREIGN KEY (geo_id) REFERENCES bible.locations (location_id),
    FOREIGN KEY (file_id) REFERENCES bible.files (id)
);

CREATE TABLE IF NOT EXISTS bible.locationgeometry (
    id                  SERIAL PRIMARY KEY,
    geo_id              TEXT,
    location_id         TEXT,
    FOREIGN KEY (geo_id) REFERENCES bible.geometries (geo_id),
    FOREIGN KEY (location_id) REFERENCES bible.locations (location_id)
);