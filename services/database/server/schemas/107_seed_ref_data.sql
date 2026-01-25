INSERT INTO lookup.data_formats (code, mime_type, extension, description) VALUES
    ('USX', 'application/xml', 'usx', 'Unified Standard XML Bible Format'),
    ('TSV', 'text/tab-separated-values', 'tsv', 'Tab Separated Values'),
    ('XML', 'application/xml', 'xml', 'Extensible Markup Language'),
    ('JSON', 'application/json', 'json', 'JavaScript Object Notation'),
    ('MP3', 'audio/mpeg', 'mp3', 'MPEG Audio Layer III'),
    ('WAV', 'audio/wav', 'wav', 'Waveform Audio File Format'),
    ('JPEG', 'image/jpeg', 'jpg', 'JPEG Image'),
    ('PNG', 'image/png', 'png', 'Portable Network Graphics'),
    ('PDF', 'application/pdf', 'pdf', 'Portable Document Format'),
    ('CSV', 'text/csv', 'csv', 'Comma Separated Values'),
    ('XLSX', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx', 'Microsoft Excel Open XML Spreadsheet'),
    ('TXT', 'text/plain', 'txt', 'Plain Text File'),
    ('ZIP', 'application/zip', 'zip', 'ZIP Archive'),
    ('7Z', 'application/x-7z-compressed', '7z', '7-Zip Archive');

INSERT INTO lookup.source_types (code, name, description) VALUES
    ('PUB', 'Publisher', 'A publisher that provides various datasets and files.'),
    ('DAT', 'Dataset', 'A dataset that contains structured data for specific purposes.'),
    ('FILE', 'File', 'An individual file that may be part of a dataset or standalone.');