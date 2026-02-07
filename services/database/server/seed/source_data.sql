
-- ============================================================================
-- PUBLISHERS & ORGANIZATIONS
-- ============================================================================

-- Tyndale House Cambridge
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('PUB', 'TYNDALE', 'Tyndale House Cambridge', 
 'A biblical research institute and publisher dedicated to biblical scholarship and the production of scholarly biblical resources. Sponsors research projects and publishes academic works including the Tyndale House Edition of the Greek New Testament.',
 NULL,
 'https://www.tyndalehouse.com/',
 'Tyndale House, Cambridge. https://www.tyndalehouse.com/',
 '1944-01-01',
 '{"type": "research_institute", "focus": ["biblical_scholarship", "textual_criticism", "biblical_languages"], "notable_projects": ["Tyndale House Greek New Testament", "STEPBible"]}'::jsonb);

-- GitHub (Distributor)
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, metadata) VALUES
('DIST', 'GITHUB', 'GitHub', 
 'A web-based platform for version control and collaborative software development. Widely used for distributing and hosting open-source biblical datasets, linguistic resources, and related tools.',
 NULL,
 'https://github.com/',
 'GitHub, Inc. https://github.com/',
 '{"type": "platform", "purpose": "code_hosting", "features": ["version_control", "collaboration", "distribution"]}'::jsonb);

-- STEPBible Data Repository (Dataset collection with parent)
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, parent_source, date_published, metadata) VALUES
('DAT', 'STEP', 'STEPBible Data Repository', 
 'Scripture Tools for Every Person - a comprehensive collection of tagged, morphologically analyzed biblical texts. Includes Hebrew, Greek, and English texts with extensive linguistic tagging, made freely available for research and study.',
 NULL,
 'https://www.stepbible.org/',
 'STEPBible Data Repository. Tyndale House, Cambridge. https://www.stepbible.org/',
 (SELECT id FROM audit.sources WHERE code = 'TYNDALE'),
 '2010-01-01',
 '{"license": "CC BY 4.0", "languages": ["Hebrew", "Greek", "English"], "features": ["morphology", "lexical_tagging"], "distributed_via": "GitHub"}'::jsonb);

-- OpenScriptures (update to show GitHub as distributor)
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('DAT', 'OPENSCR', 'OpenScriptures', 
 'A collaborative dataset collection creating free, open-licensed biblical resources including morphologically tagged Hebrew Bible texts and Greek New Testament resources. Emphasizes community-driven development and open standards.',
 NULL,
 'https://github.com/openscriptures',
 'OpenScriptures Project. https://github.com/openscriptures.',
 '2009-01-01',
 '{"approach": "collaborative", "license": "various open licenses", "focus": ["morphology", "Hebrew_Bible", "Greek_NT"], "distributed_via": "GitHub"}'::jsonb);

-- Digital Bible Library (DBL) - Distributor/Platform
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('DIST', 'DBL', 'Digital Bible Library', 
 'A digital platform managed by United Bible Societies that provides access to Scripture texts, audio recordings, and related resources in hundreds of languages. Serves as a centralized repository for Bible translation projects worldwide.',
 NULL,
 'https://library.bible/',
 'Digital Bible Library. United Bible Societies. https://library.bible/',
 '2012-01-01',
 '{"organization": "United Bible Societies", "resource_types": ["text", "audio", "video"], "language_count": "1800+"}'::jsonb);

-- Summer Institute of Linguistics (SIL)
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('PUB', 'SIL', 'SIL International', 
 'A global faith-based nonprofit organization that studies, documents, and assists in developing the world''s lesser-known languages. Known for linguistic research, Bible translation support, and literacy development.',
 NULL,
 'https://www.sil.org/',
 'SIL International. https://www.sil.org/',
 '1934-01-01',
 '{"formerly_known_as": "Summer Institute of Linguistics", "founded": 1934, "focus": ["linguistics", "language_development", "literacy"]}'::jsonb);

-- Unicode Consortium
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('PUB', 'UNICODE', 'Unicode Consortium', 
 'A non-profit organization that maintains the Unicode Standard, enabling consistent encoding, representation, and handling of text expressed in most of the world''s writing systems. Critical for biblical text encoding and multilingual support.',
 NULL,
 'https://unicode.org/',
 'The Unicode Consortium. Unicode Standard. https://unicode.org/',
 '1991-01-01',
 '{"standards": ["Unicode", "CLDR", "UCA"], "focus": ["character_encoding", "internationalization"]}'::jsonb);

-- Paratext
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('PUB', 'PARATEXT', 'Paratext', 
 'A Bible translation software tool developed by United Bible Societies and SIL International. Industry standard for Bible translation projects, providing text editing, checking tools, and project management capabilities.',
 NULL,
 'https://paratext.org/',
 'Paratext. United Bible Societies and SIL International. https://paratext.org/',
 '1993-01-01',
 '{"developers": ["United Bible Societies", "SIL International"], "type": "software", "purpose": "Bible translation and checking"}'::jsonb);

-- ============================================================================
-- LEXICAL RESOURCES
-- ============================================================================

-- Brown-Driver-Briggs Hebrew Lexicon
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('DAT', 'BDB', 'Brown-Driver-Briggs Hebrew and English Lexicon', 
 'A comprehensive Hebrew lexicon of the Old Testament, considered a standard reference work for biblical Hebrew. Organized by root words with extensive etymological and semantic information.',
 '1906',
 'https://archive.org/details/hebrewenglishlex00geseuoft',
 'Brown, Francis, S.R. Driver, and Charles A. Briggs. 1906. The Brown-Driver-Briggs Hebrew and English Lexicon. Boston: Houghton, Mifflin and Company.',
 '1906-01-01',
 '{"authors": ["Francis Brown", "S.R. Driver", "Charles A. Briggs"], "language": "Hebrew", "testament": "Old Testament", "status": "public domain"}'::jsonb);

-- Liddell-Scott-Jones Greek Lexicon
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, date_published, metadata) VALUES
('DAT', 'LSJ', 'Liddell-Scott-Jones Greek-English Lexicon', 
 'The authoritative lexicon for Classical Greek, widely used for Koine Greek and Septuagint studies. Provides comprehensive etymological, semantic, and usage information for ancient Greek vocabulary.',
 '9th Edition',
 'https://stephanus.tlg.uci.edu/lsj/',
 'Liddell, Henry George, Robert Scott, and Henry Stuart Jones. 1940. A Greek-English Lexicon. 9th ed. Oxford: Clarendon Press.',
 '1940-01-01',
 '{"authors": ["Henry George Liddell", "Robert Scott", "Henry Stuart Jones"], "edition": "9th", "language": "Greek", "scope": "Classical and Koine Greek"}'::jsonb);

-- ============================================================================
-- EXAMPLE: Specific Dataset with Parent
-- ============================================================================

-- STEPBible Hebrew Dataset (example of dataset with parent publisher)
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, parent_source, date_published, metadata) VALUES
('DAT', 'STEP-OSHB', 'STEPBible Open Scriptures Hebrew Bible', 
 'Morphologically tagged Hebrew Bible based on the Westminster Leningrad Codex, with extensive linguistic analysis and tagging provided by STEPBible.',
 '2024',
 'https://github.com/STEPBible/STEPBible-Data',
 'STEPBible Open Scriptures Hebrew Bible. 2024. Tyndale House, Cambridge. https://github.com/STEPBible/STEPBible-Data.',
 (SELECT id FROM audit.sources WHERE code = 'STEP'),
 '2024-01-01',
 '{"base_text": "Westminster Leningrad Codex", "features": ["morphology", "cantillation", "vowel_points"], "format": "OSIS XML"}'::jsonb);

-- DBL USX Format Specification (example of standard/format as dataset)
INSERT INTO audit.sources (source_type, code, name, description, version, url, official_citation, parent_source, date_published, metadata) VALUES
('DAT', 'DBL-USX', 'DBL Unified Scripture XML Format', 
 'XML-based format used by Digital Bible Library for encoding Scripture texts. Provides structured markup for verses, paragraphs, character formatting, and cross-references.',
 '3.0',
 'https://github.com/ubsicap/usx',
 'Unified Scripture XML (USX) Format. United Bible Societies. https://github.com/ubsicap/usx.',
 (SELECT id FROM audit.sources WHERE code = 'DBL'),
 '2020-01-01',
 '{"type": "format_specification", "format": "XML", "schema_version": "3.0", "purpose": "Scripture markup"}'::jsonb);