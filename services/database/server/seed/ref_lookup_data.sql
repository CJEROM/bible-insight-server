INSERT INTO lookup.data_formats (code, mime_type, extension, description) VALUES
    ('USX', 'application/xml', 'xml', 'Unified Standard XML Bible Format'),
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
    ('7Z', 'application/x-7z-compressed', '7z', '7-Zip Archive'),
    ('LDML', 'application/xml', 'ldml', 'Unicode Locale Data Markup Language');

INSERT INTO lookup.source_types (code, name, description) VALUES 
    ('PUB', 'Publisher', 'An organization or entity that officially publishes and releases biblical resources, datasets, or scholarly works. Publishers typically hold intellectual property rights and are responsible for the official release of materials.'),
    ('DAT', 'Dataset', 'A structured collection of biblical data organized for a specific purpose, such as morphological analysis, lexical information, or textual variants. May be produced by publishers, contributors, or distributors.'),
    ('FILE', 'File', 'An individual file containing biblical data or resources. May exist as part of a dataset or as a standalone resource. Represents the actual data artifact being processed or stored.'),
    ('CONT', 'Contributor', 'An individual, organization, or scholarly entity that contributes to the creation, editing, translation, or annotation of biblical resources. Contributors may work on datasets without being the official publisher.'),
    ('DIST', 'Distributor', 'An organization or platform that makes biblical resources available to users, potentially aggregating content from multiple publishers and contributors. Distributors facilitate access and delivery but may not hold original publishing rights.'),
    ('LICP', 'Licence Provider', 'Licence standard creators');