CREATE TABLE audit.ingestion_stats (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER,
    version_id          INTEGER, -- ?????
    start_time          TIMESTAMP,
    end_time            TIMESTAMP,
    duration            INTERVAL GENERATED ALWAYS AS (end_time - start_time) STORED,
    error_message       TEXT,
    status              TEXT, -- pending, in_progress, completed, failed    
    FOREIGN KEY (source_id) REFERENCES audit.sources (id) ON DELETE CASCADE,
    FOREIGN KEY (version_id) REFERENCES audit.files (id) ON DELETE CASCADE
);