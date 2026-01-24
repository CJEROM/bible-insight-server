INSERT INTO lookup.data_formats (code, mime_type, description) VALUES
    ('USX', 'application/xml', 'Unified Standard XML Bible Format'),
    ('TSV', 'text/tab-separated-values', 'Tab Separated Values'),
    ('XML', 'application/xml', 'Extensible Markup Language'),
    ('JSON', 'application/json', 'JavaScript Object Notation'),
    ('MP3', 'audio/mpeg', 'MPEG Audio Layer III'),
    ('WAV', 'audio/wav', 'Waveform Audio File Format'),
    ('JPEG', 'image/jpeg', 'JPEG Image'),
    ('PNG', 'image/png', 'Portable Network Graphics'),
    ('PDF', 'application/pdf', 'Portable Document Format'),
    ('CSV', 'text/csv', 'Comma Separated Values'),
    ('XLSX', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Microsoft Excel Open XML Spreadsheet'),
    ('TXT', 'text/plain', 'Plain Text File'),
    ('ZIP', 'application/zip', 'ZIP Archive'),
    ('7z', 'application/x-7z-compressed', '7-Zip Archive');

INSERT INTO lookup.source_types (code, name, description) VALUES
    ('PUB', 'Publisher', 'A publisher that provides various datasets and files.'),
    ('DAT', 'Dataset', 'A dataset that contains structured data for specific purposes.'),
    ('FILE', 'File', 'An individual file that may be part of a dataset or standalone.');