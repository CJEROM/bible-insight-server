from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.dbmanager import DBManager

from database.boundary.base_boundary import ReadBoundary, WriteBoundary


SOURCE_REGISTRY = {
    # ============================================================================
    # PUBLISHERS & ORGANIZATIONS
    # ============================================================================
    
    "TYNDALE": {
        "source_type": "PUB",
        "name": "Tyndale House Cambridge",
        "description": "A biblical research institute and publisher dedicated to biblical scholarship and the production of scholarly biblical resources. Sponsors research projects and publishes academic works including the Tyndale House Edition of the Greek New Testament.",
        "version": None,
        "url": "https://www.tyndalehouse.com/",
        "note": None,
        "parent_code": None,
        "official_citation": "Tyndale House, Cambridge. https://www.tyndalehouse.com/",
        "date_published": "1944-01-01",
        # "metadata": {
        #     "type": "research_institute",
        #     "focus": ["biblical_scholarship", "textual_criticism", "biblical_languages"],
        #     "notable_projects": ["Tyndale House Greek New Testament", "STEPBible"]
        # }
    },
    
    "GITHUB": {
        "source_type": "DIST",
        "name": "GitHub",
        "description": "A web-based platform for version control and collaborative software development. Widely used for distributing and hosting open-source biblical datasets, linguistic resources, and related tools.",
        "version": None,
        "url": "https://github.com/",
        "note": None,
        "parent_code": None,
        "official_citation": "GitHub, Inc. https://github.com/",
        "date_published": None,
        # "metadata": {
        #     "type": "platform",
        #     "purpose": "code_hosting",
        #     "features": ["version_control", "collaboration", "distribution"]
        # }
    },
    
    "STEPBIBLE": {
        "source_type": "DAT",
        "name": "STEPBible Data Repository",
        "description": "Scripture Tools for Every Person - a comprehensive collection of tagged, morphologically analyzed biblical texts. Includes Hebrew, Greek, and English texts with extensive linguistic tagging, made freely available for research and study.",
        "version": None,
        "url": "https://www.stepbible.org/",
        "note": None,
        "parent_code": "TYNDALE",
        "official_citation": "STEPBible Data Repository. Tyndale House, Cambridge. https://www.stepbible.org/",
        "date_published": "2010-01-01",
        # "metadata": {
        #     "license": "CC BY 4.0",
        #     "languages": ["Hebrew", "Greek", "English"],
        #     "features": ["morphology", "lexical_tagging"],
        #     "distributed_via": "GitHub"
        # }
    },
    
    "OPENSCRIPTURES": {
        "source_type": "DAT",
        "name": "OpenScriptures",
        "description": "A collaborative dataset collection creating free, open-licensed biblical resources including morphologically tagged Hebrew Bible texts and Greek New Testament resources. Emphasizes community-driven development and open standards.",
        "version": None,
        "url": "https://github.com/openscriptures",
        "note": None,
        "parent_code": None,
        "official_citation": "OpenScriptures Project. https://github.com/openscriptures.",
        "date_published": "2009-01-01",
        # "metadata": {
        #     "approach": "collaborative",
        #     "license": "various open licenses",
        #     "focus": ["morphology", "Hebrew_Bible", "Greek_NT"],
        #     "distributed_via": "GitHub"
        # }
    },
    
    "DBL": {
        "source_type": "DIST",
        "name": "Digital Bible Library",
        "description": "A digital platform managed by United Bible Societies that provides access to Scripture texts, audio recordings, and related resources in hundreds of languages. Serves as a centralized repository for Bible translation projects worldwide.",
        "version": None,
        "url": "https://library.bible/",
        "note": None,
        "parent_code": None,
        "official_citation": "Digital Bible Library. United Bible Societies. https://library.bible/",
        "date_published": "2012-01-01",
        # "metadata": {
        #     "organization": "United Bible Societies",
        #     "resource_types": ["text", "audio", "video"],
        #     "language_count": "1800+"
        # }
    },
    
    "SIL": {
        "source_type": "PUB",
        "name": "SIL International",
        "description": "A global faith-based nonprofit organization that studies, documents, and assists in developing the world's lesser-known languages. Known for linguistic research, Bible translation support, and literacy development.",
        "version": None,
        "url": "https://www.sil.org/",
        "note": None,
        "parent_code": None,
        "official_citation": "SIL International. https://www.sil.org/",
        "date_published": "1934-01-01",
        # "metadata": {
        #     "formerly_known_as": "Summer Institute of Linguistics",
        #     "founded": 1934,
        #     "focus": ["linguistics", "language_development", "literacy"]
        # }
    },
    
    "UNICODE": {
        "source_type": "PUB",
        "name": "Unicode Consortium",
        "description": "A non-profit organization that maintains the Unicode Standard, enabling consistent encoding, representation, and handling of text expressed in most of the world's writing systems. Critical for biblical text encoding and multilingual support.",
        "version": None,
        "url": "https://unicode.org/",
        "note": None,
        "parent_code": None,
        "official_citation": "The Unicode Consortium. Unicode Standard. https://unicode.org/",
        "date_published": "1991-01-01",
        # "metadata": {
        #     "standards": ["Unicode", "CLDR", "UCA"],
        #     "focus": ["character_encoding", "internationalization"]
        # }
    },
    
    "PARATEXT": {
        "source_type": "PUB",
        "name": "Paratext",
        "description": "A Bible translation software tool developed by United Bible Societies and SIL International. Industry standard for Bible translation projects, providing text editing, checking tools, and project management capabilities.",
        "version": None,
        "url": "https://paratext.org/",
        "note": None,
        "parent_code": None,
        "official_citation": "Paratext. United Bible Societies and SIL International. https://paratext.org/",
        "date_published": "1993-01-01",
        # "metadata": {
        #     "developers": ["United Bible Societies", "SIL International"],
        #     "type": "software",
        #     "purpose": "Bible translation and checking"
        # }
    },
    
    # ============================================================================
    # LEXICAL RESOURCES
    # ============================================================================
    
    "BDB": {
        "source_type": "PUB",
        "name": "Brown-Driver-Briggs Hebrew and English Lexicon",
        "description": "A comprehensive Hebrew lexicon of the Old Testament, considered a standard reference work for biblical Hebrew. Organized by root words with extensive etymological and semantic information.",
        "version": "1906",
        "url": "https://archive.org/details/hebrewenglishlex00geseuoft",
        "note": None,
        "parent_code": None,
        "official_citation": "Brown, Francis, S.R. Driver, and Charles A. Briggs. 1906. The Brown-Driver-Briggs Hebrew and English Lexicon. Boston: Houghton, Mifflin and Company.",
        "date_published": "1906-01-01",
        # "metadata": {
        #     "authors": ["Francis Brown", "S.R. Driver", "Charles A. Briggs"],
        #     "language": "Hebrew",
        #     "testament": "Old Testament",
        #     "status": "public domain"
        # }
    },
    
    "LSJ": {
        "source_type": "PUB",
        "name": "Liddell-Scott-Jones Greek-English Lexicon",
        "description": "The authoritative lexicon for Classical Greek, widely used for Koine Greek and Septuagint studies. Provides comprehensive etymological, semantic, and usage information for ancient Greek vocabulary.",
        "version": "9th Edition",
        "url": "https://stephanus.tlg.uci.edu/lsj/",
        "note": None,
        "parent_code": None,
        "official_citation": "Liddell, Henry George, Robert Scott, and Henry Stuart Jones. 1940. A Greek-English Lexicon. 9th ed. Oxford: Clarendon Press.",
        "date_published": "1940-01-01",
        # "metadata": {
        #     "authors": ["Henry George Liddell", "Robert Scott", "Henry Stuart Jones"],
        #     "edition": "9th",
        #     "language": "Greek",
        #     "scope": "Classical and Koine Greek"
        # }
    },
    
    # ============================================================================
    # SPECIFIC DATASETS WITH PARENTS
    # ============================================================================
    
    "STEP-OSHB": {
        "source_type": "DAT",
        "name": "STEPBible Open Scriptures Hebrew Bible",
        "description": "Morphologically tagged Hebrew Bible based on the Westminster Leningrad Codex, with extensive linguistic analysis and tagging provided by STEPBible.",
        "version": "2024",
        "url": "https://github.com/STEPBible/STEPBible-Data",
        "note": None,
        "parent_code": "STEP",
        "official_citation": "STEPBible Open Scriptures Hebrew Bible. 2024. Tyndale House, Cambridge. https://github.com/STEPBible/STEPBible-Data.",
        "date_published": "2024-01-01",
        # "metadata": {
        #     "base_text": "Westminster Leningrad Codex",
        #     "features": ["morphology", "cantillation", "vowel_points"],
        #     "format": "OSIS XML"
        # }
    },
    
    "DBL-USX": {
        "source_type": "DAT",
        "name": "DBL Unified Scripture XML Format",
        "description": "XML-based format used by Digital Bible Library for encoding Scripture texts. Provides structured markup for verses, paragraphs, character formatting, and cross-references.",
        "version": "3.0",
        "url": "https://github.com/ubsicap/usx",
        "note": None,
        "parent_code": "DBL",
        "official_citation": "Unified Scripture XML (USX) Format. United Bible Societies. https://github.com/ubsicap/usx.",
        "date_published": "2020-01-01",
        # "metadata": {
        #     "type": "format_specification",
        #     "format": "XML",
        #     "schema_version": "3.0",
        #     "purpose": "Scripture markup"
        # }
    },

    # ============================================================================
    # LICENSE PROVIDERS
    # ============================================================================

    "CC": {
        "source_type": "LICP",
        "name": "Creative Commons",
        "description": "A nonprofit organization that provides free, easy-to-use copyright licenses to make creative works and knowledge available for sharing, use, and building upon. Widely used for open biblical and scholarly resources.",
        "version": None,
        "url": "https://creativecommons.org/",
        "note": None,
        "parent_code": None,
        "official_citation": "Creative Commons. https://creativecommons.org/",
        "date_published": "2001-01-01",
        # "metadata": {
        #     "type": "license_provider",
        #     "founded": 2001,
        #     "license_types": ["CC0", "CC BY", "CC BY-SA", "CC BY-NC", "CC BY-NC-SA", "CC BY-ND", "CC BY-NC-ND"],
        #     "focus": ["copyright_licensing", "open_access", "creative_commons"]
        # }
    },

    "GNU": {
        "source_type": "LICP",
        "name": "GNU Project / Free Software Foundation",
        "description": "A free software, mass collaboration project founded by Richard Stallman. Responsible for the GNU General Public License (GPL) family of copyleft licenses widely used in open source software and data projects.",
        "version": None,
        "url": "https://www.gnu.org/",
        "note": None,
        "parent_code": None,
        "official_citation": "GNU Project. Free Software Foundation. https://www.gnu.org/",
        "date_published": "1983-09-27",
        # "metadata": {
        #     "type": "license_provider",
        #     "founded": 1983,
        #     "organization": "Free Software Foundation",
        #     "license_types": ["GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0"],
        #     "focus": ["free_software", "copyleft", "software_freedom"]
        # }
    },

    "MIT": {
        "source_type": "LICP",
        "name": "Massachusetts Institute of Technology",
        "description": "Academic institution that created one of the most permissive and widely-used open source licenses. The MIT License allows broad freedom with minimal restrictions.",
        "version": None,
        "url": "https://opensource.org/licenses/MIT",
        "note": None,
        "parent_code": None,
        "official_citation": "Massachusetts Institute of Technology. MIT License. https://opensource.org/licenses/MIT",
        "date_published": "1988-01-01",
        # "metadata": {
        #     "type": "license_provider",
        #     "license_types": ["MIT"],
        #     "focus": ["permissive_licensing", "open_source"]
        # }
    },

    "APACHE": {
        "source_type": "LICP",
        "name": "Apache Software Foundation",
        "description": "A nonprofit organization supporting Apache software projects. Created the Apache License, a permissive free software license with explicit patent grant provisions.",
        "version": None,
        "url": "https://www.apache.org/",
        "note": None,
        "parent_code": None,
        "official_citation": "Apache Software Foundation. https://www.apache.org/",
        "date_published": "1999-03-01",
        # "metadata": {
        #     "type": "license_provider",
        #     "founded": 1999,
        #     "license_types": ["Apache-1.0", "Apache-1.1", "Apache-2.0"],
        #     "focus": ["open_source", "permissive_licensing", "patent_protection"]
        # }
    },

    # "CODE": {
    #     "source_type"       : "",
    #     "name"              : "",
    #     "description"       : "",
    #     "version"           : "",
    #     "url"               : "",
    #     "note"              : "",
    #     "parent_source"     : "",
    #     "official_citation" : "",
    #     "date_published"    : "",
    #     "metadata"          : {}
    # },
}

class SourceRegistry:
    def __init__(self, db: "DBManager"):
        self.db = db

        self.read = ReadBoundary(db)
        self.write = WriteBoundary(db)

        self.seed_sources()

    def seed_sources(self):

        for code, data in SOURCE_REGISTRY.items():
            parent_source_id = None
            if data.get("source_code") != None:
                parent_source_id = self.read.find_source(data.get("parent_code"))

            self.write.persist_source(
                source_type         = data.get("source_type"),
                code                = code,
                name                = data.get("name"),
                description         = data.get("description"),
                version             = data.get("version"),
                url                 = data.get("url"),
                note                = data.get("note"),
                parent_source       = parent_source_id,
                official_citation   = data.get("official_citation"),
                date_published      = data.get("date_published"),
                metadata            = data.get("metadata")
            )