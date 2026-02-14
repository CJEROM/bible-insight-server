from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.dbmanager import DBManager

from database.boundary.base_boundary import ReadBoundary, WriteBoundary

LICENCE_REGISTRY = {
    
    "NONE": {
        "source_code"   : None,
        "name"          : "No Licence",
        "version"       : None,
        "link"          : None,
        "summary"       : "All rights reserved - no permissions granted",
        "notes"         : "Default copyright - no usage permitted without explicit permission",
        "attributes"    : [
            # PERMISSIONS
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "TRANSLATE",
            "PRINT",
            "DIGITAL",
            "SUBLICENSE",
            "PRIVATE_USE"
        ]
    },

    "PUBLIC_DOMAIN": {
        "source_code"   : None,
        "name"          : "Public Domain",
        "version"       : None,
        "link"          : None,
        "summary"       : "No copyright restrictions",
        "notes"         : "Work is in the public domain - free to use for any purpose",
        "attributes"    : [
            # PERMISSIONS
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "TRANSLATE",
            "PRINT",
            "DIGITAL",
            "SUBLICENSE",
            "PRIVATE_USE"
        ]
    },

    "CC0 1.0": {
        "source_code"   : "CC",
        "name"          : "CC0 1.0 Universal",
        "version"       : "1.0",
        "link"          : "https://creativecommons.org/publicdomain/zero/1.0/",
        "summary"       : "Public domain dedication",
        "notes"         : "Creator waives all rights - equivalent to public domain",
        "attributes"    : [
            # PERMISSIONS
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "TRANSLATE",
            "PRINT",
            "DIGITAL",
            "SUBLICENSE",
            "PRIVATE_USE"
        ]
    },

    "CC BY 4.0": {
        "source_code"   : "CC",
        "name"          : "Attribution 4.0 International",
        "version"       : "4.0",
        "link"          : "https://creativecommons.org/licenses/by/4.0/",
        "summary"       : "Free to use with attribution",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "TRANSLATE",
            "PRINT",
            "DIGITAL",
            "SUBLICENSE",
            "PRIVATE_USE",
            # OBLIGATIONS
            "ATTRIBUTION",
            "NOTICE"
        ]
    },

    "CC BY-SA 4.0": {
        "source_code"   : "CC",
        "name"          : "Attribution-ShareAlike 4.0 International",
        "version"       : "4.0",
        "link"          : "https://creativecommons.org/licenses/by-sa/4.0/",
        "summary"       : "Free to use with attribution, derivatives must use same license",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "TRANSLATE",
            "PRINT",
            "DIGITAL",
            "SUBLICENSE",
            "PRIVATE_USE",
            # OBLIGATIONS
            "ATTRIBUTION",
            "NOTICE",
            "SHARE_ALIKE"
        ]
    },

    "CC BY-NC 4.0": {
        "source_code"   : "CC",
        "name"          : "Attribution-NonCommercial 4.0 International",
        "version"       : "4.0",
        "link"          : "https://creativecommons.org/licenses/by-nc/4.0/",
        "summary"       : "Free for non-commercial use with attribution",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "DISTRIBUTE",
            "MODIFY",
            "TRANSLATE",
            "PRINT",
            "DIGITAL",
            "SUBLICENSE",
            "PRIVATE_USE",
            # OBLIGATIONS
            "ATTRIBUTION",
            "NOTICE",
            # RESTRICTIONS
            "NO_COMMERCIAL"
        ]
    },

    "CC BY-NC-SA 4.0": {
        "source_code"   : "CC",
        "name"          : "Attribution-NonCommercial-ShareAlike 4.0 International",
        "version"       : "4.0",
        "link"          : "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "summary"       : "Free for non-commercial use with attribution, derivatives must use same license",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "DISTRIBUTE",
            "MODIFY",
            "TRANSLATE",
            "PRINT",
            "DIGITAL",
            "PRIVATE_USE",
            # OBLIGATIONS
            "ATTRIBUTION",
            "NOTICE",
            "SHARE_ALIKE",
            # RESTRICTIONS
            "NO_COMMERCIAL"
        ]
    },

    "CC BY-ND 4.0": {
        "source_code"   : "CC",
        "name"          : "Attribution-NoDerivatives 4.0 International",
        "version"       : "4.0",
        "link"          : "https://creativecommons.org/licenses/by-nd/4.0/",
        "summary"       : "Free to use with attribution, no modifications allowed",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "COMMERCIAL",
            "DISTRIBUTE",
            "PRINT",
            "DIGITAL",
            "PRIVATE_USE",
            # OBLIGATIONS
            "ATTRIBUTION",
            "NOTICE",
            # RESTRICTIONS
            "NO_DERIVATIVES"
        ]
    },

    "CC BY-NC-ND 4.0": {
        "source_code"   : "CC",
        "name"          : "Attribution-NonCommercial-NoDerivatives 4.0 International",
        "version"       : "4.0",
        "link"          : "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "summary"       : "Free for non-commercial use with attribution, no modifications allowed",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "DISTRIBUTE",
            "PRINT",
            "DIGITAL",
            "PRIVATE_USE",
            # OBLIGATIONS
            "ATTRIBUTION",
            "NOTICE",
            # RESTRICTIONS
            "NO_COMMERCIAL",
            "NO_DERIVATIVES"
        ]
    },

    "GPL-2.0": {
        "source_code"   : "GNU",
        "name"          : "GNU General Public License v2.0",
        "version"       : "2.0",
        "link"          : "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
        "summary"       : "Copyleft license requiring source code disclosure",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "USE",
            "STUDY",
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "PRIVATE_USE",
            # OBLIGATIONS
            "COPYLEFT",
            "SOURCE_CODE",
            "PRESERVE_NOTICES",
            "DOCUMENT_CHANGES",
            "LICENSE_TEXT",
            # RESTRICTIONS
            "NO_WARRANTY",
            "NO_ADDITIONAL_RESTRICTIONS"
        ]
    },

    "GPL-3.0": {
        "source_code"   : "GNU",
        "name"          : "GNU General Public License v3.0",
        "version"       : "3.0",
        "link"          : "https://www.gnu.org/licenses/gpl-3.0.html",
        "summary"       : "Copyleft license with patent grant and anti-tivoization provisions",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "USE",
            "STUDY",
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "PRIVATE_USE",
            "PATENT_GRANT",
            # OBLIGATIONS
            "COPYLEFT",
            "SOURCE_CODE",
            "PRESERVE_NOTICES",
            "DOCUMENT_CHANGES",
            "LICENSE_TEXT",
            "INSTALLATION_INFO",
            # RESTRICTIONS
            "NO_WARRANTY",
            "NO_ADDITIONAL_RESTRICTIONS",
            "NO_DRM",
            "NO_TIVOIZATION"
        ]
    },

    "AGPL-3.0": {
        "source_code"   : "GNU",
        "name"          : "GNU Affero General Public License v3.0",
        "version"       : "3.0",
        "link"          : "https://www.gnu.org/licenses/agpl-3.0.html",
        "summary"       : "Copyleft license with network use disclosure requirement",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "USE",
            "STUDY",
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "PRIVATE_USE",
            "PATENT_GRANT",
            # OBLIGATIONS
            "COPYLEFT",
            "SOURCE_CODE",
            "PRESERVE_NOTICES",
            "DOCUMENT_CHANGES",
            "LICENSE_TEXT",
            "INSTALLATION_INFO",
            "NETWORK_DISCLOSURE",
            # RESTRICTIONS
            "NO_WARRANTY",
            "NO_ADDITIONAL_RESTRICTIONS",
            "NO_DRM",
            "NO_TIVOIZATION"
        ]
    },

    "LGPL-3.0": {
        "source_code"   : "GNU",
        "name"          : "GNU Lesser General Public License v3.0",
        "version"       : "3.0",
        "link"          : "https://www.gnu.org/licenses/lgpl-3.0.html",
        "summary"       : "Copyleft license allowing linking with proprietary software",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "USE",
            "STUDY",
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "PRIVATE_USE",
            "PATENT_GRANT",
            # OBLIGATIONS
            "SOURCE_CODE",
            "PRESERVE_NOTICES",
            "DOCUMENT_CHANGES",
            "LICENSE_TEXT",
            # RESTRICTIONS
            "NO_WARRANTY",
            "NO_ADDITIONAL_RESTRICTIONS"
        ]
    },

    "MIT": {
        "source_code"   : "MIT",
        "name"          : "MIT License",
        "version"       : None,
        "link"          : "https://opensource.org/licenses/MIT",
        "summary"       : "Permissive license with minimal restrictions",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "USE",
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "PRIVATE_USE",
            "SUBLICENSE",
            # OBLIGATIONS
            "PRESERVE_NOTICES",
            # RESTRICTIONS
            "NO_WARRANTY"
        ]
    },

    "APACHE-2.0": {
        "source_code"   : "APACHE",
        "name"          : "Apache License 2.0",
        "version"       : "2.0",
        "link"          : "https://www.apache.org/licenses/LICENSE-2.0",
        "summary"       : "Permissive license with patent grant",
        "notes"         : None,
        "attributes"    : [
            # PERMISSIONS
            "USE",
            "COMMERCIAL",
            "DISTRIBUTE",
            "MODIFY",
            "PRIVATE_USE",
            "SUBLICENSE",
            # OBLIGATIONS
            "PATENT_GRANT",
            "PRESERVE_NOTICES",
            "DOCUMENT_CHANGES",
            # RESTRICTIONS
            "NO_WARRANTY",
            "NO_TRADEMARK"
        ]
    },

}

class LicenceRegistry:
    def __init__(self, db: "DBManager"):
        self.db = db

        self.read = ReadBoundary(db)
        self.write = WriteBoundary(db)

        self.seed_all_licenses()

    def seed_all_licenses(self):
        for code, data in LICENCE_REGISTRY.items():
            source_id = None
            if data.get("source_code") != None:
                source_id = self.read.find_source(data.get("source_code"))
            
            licence_id = self.write.persist_licence(
                source_id       = source_id,
                code            = code,
                name            = data.get("name"),
                version         = data.get("version"),
                link            = data.get("link"),
                summary         = data.get("summary"),
                notes           = data.get("notes")
            )

            self.write.map_all_licence_attributes(
                licence_id      = licence_id,
                attributes      = data.get("attributes")
            )
