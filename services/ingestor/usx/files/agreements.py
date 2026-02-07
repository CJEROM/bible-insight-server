from ingestor.usx.files.base_file import BaseFile
from ingestor.usx.translation import Translation

from database.boundary.usx_boundary import USXReadBoundary, USXWriteBoundary

from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class DBLAgreement(BaseFile):
    def __init__(self, manager: "ManagerHandler", agreement_id, license_code, log: "LogManager"):
        self.manager                = manager
        self.db                     = manager.get_db()
        self.obj                    = manager.get_obj()
        self.log                    = log

        self.log.log_to_file(f"Initialising Agreement ...", "AGREEMENT", "INFO")

        self.translation            = None
        self.translation_file_path  = None
        self.this_file_path         = None
        self.file_id                = None

        self.source_id              = None

        self.agreement_id           = agreement_id
        self.license_code           = license_code

        self.valid                  = False
        self.exists                 = False

        self.new                    = False # Is this a newly introduced agreement?

        self.details                = {}

        self.read                   = USXReadBoundary(self.db)
        self.write                  = USXWriteBoundary(self.db)

        self.check_agreement_exists(agreement_id)

    def get_valid(self):
        return self.valid
    
    def get_exists(self):
        return self.exists
    
    def is_new(self):
        return self.new
    
    def set_source(self, source_id):
        self.source_id = source_id
    
    def get_details(self, key):
        if key is not None:
            return self.details.get(key)
        else:
            return self.details
        
    def get_id(self):
        return self.agreement_id

    def check_agreement_exists(self, agreement_id):
        found = self.read.find_agreement(
            agreement_id    = agreement_id
        )
        if found: # i.e. != None
            self.exists     = True
            self.log.log_to_file(f"Agreement Exists, Now Verifying ...", "AGREEMENT", "INFO")
            self.valid      = self.check_agreement_valid(found.dateLicenceExpiry)
        else:
            self.new        = True
            self.log.log_to_file(f"New Agreement found, Creating New in Database", "AGREEMENT", "INFO")
            self.log.log_to_file(f"NOTE: The asociated Translation will be marked as a Test Import!", "AGREEMENT", "INFO")
            self.write.init_agreement(self.agreement_id)

    def check_agreement_valid(self, expiry: datetime | None) -> bool:
        valid = False
        
        # if licence exists, but no expiry set, then valid (we will update it during ingestion)
        if expiry is None:
            valid = True
            self.log.log_to_file(f"Agreement Validation result = PASS", "AGREEMENT", "INFO")
            return valid

        # If license exists, and is not expired, license = valid
        # If licence exists, and is expired, licence = not valid
        valid   = self.read.find_agreement_expired(self.agreement_id)

        result  = "PASS" if valid else "FAIL"
        self.log.log_to_file(f"Agreement Validation result: {result}", "AGREEMENT", "INFO")

        return valid

    # ======================================== MANUAL CALLS ========================================

    # Done After Translation Creation
    def set_translation(self, translation: Translation, translation_file_path: Path):
        self.translation            = translation
        self.translation_file_path  = translation_file_path

        self.log.log_to_file(f"Agreement updated with Translation", "AGREEMENT", "INFO")

        self.upload_license_file()
        if self.exists == False and self.valid == False:
            self.create_agreement()

    # Done after MetaData processing
    def link_agreement_revision(self, revision):
        self.write.persist_agreement_revision_mapping(
            agreement_id    = self.agreement_id, 
            revision        = revision
        )

    # ----------------------------------------- DERIVATIVE -----------------------------------------

    def upload_license_file(self):
        file_name = "license.xml"

        object_start        = self.translation.get_dbl_id()
        self.this_file_path = self.translation_file_path / file_name

        self.file_id = self.upload_file(
            object_name     = f"{object_start}/{file_name}",
            file_path       = self.this_file_path,
            content_type    = 'application/xml',
            data_format     = "XML",
            version_note    = "Ingested: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        self.log.log_to_file(f"Uploaded licence file for the agreement with ID [{self.file_id}]", "AGREEMENT", "INFO")

    def create_agreement(self):
        file_xml = BeautifulSoup(self.read_file(), "xml")

        self.write.update_agreement(
            agreement_id        = self.agreement_id,
            dbl_id              = self.translation.get_dbl_id(),
            base_licence_id     = self.check_license(),
            dateLicence         = file_xml.find("dateLicense").text,
            dateLicenseExpiry   = file_xml.find("dateLicenseExpiry").text,
            licence_file_id     = self.file_id
        )

        self.log.log_to_file(f"Updated / Created Agreement in Database", "AGREEMENT", "INFO")

        self.create_agreement_attributes()

    def create_agreement_attributes(self):
        file_xml = BeautifulSoup(self.read_file(), "xml")
        
        publication_rights = file_xml.find("publicationRights")
        if not publication_rights:
            return

        for right in publication_rights.find_all(recursive=False):
            value = right.text.strip().lower()

            self.write.persist_agreement_attributes(
                agreement_id        = self.agreement_id,
                attribute_code      = right.name,          # allowIntroductions
                attribute_value     = value == "true"     # bool
            )

            self.log.log_to_file(f"Mapped [{right.name}] as [{value}] to Agreement", "AGREEMENT", "DEBUG")

    def check_license(self):
        if self.license_code == None:
            self.log.log_to_file(f"No base licene found", "AGREEMENT", "DEBUG")
            return None
        
        licence_id = self.read.find_license(license_code=self.license_code)
        self.log.log_to_file(f"Linked base licence with ID [{licence_id}] to Agreement", "AGREEMENT", "DEBUG")
        return licence_id