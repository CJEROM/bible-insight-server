-- Example of how roles could be used in Bible Insight database
CREATE ROLE bi_reader   LOGIN PASSWORD '...';
CREATE ROLE bi_writer   LOGIN PASSWORD '...';
CREATE ROLE bi_ingestor LOGIN PASSWORD '...';
CREATE ROLE bi_admin    LOGIN PASSWORD '...';

GRANT USAGE ON SCHEMA bible TO bi_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA bible TO bi_reader;

GRANT INSERT, UPDATE ON audit.* TO bi_ingestor;