from ingestor.usx.files.base_file import BaseFile
from ingestor.usx.translation import Translation

from database.boundary.usx_boundary import USXReadBoundary, USXWriteBoundary

from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

from manager.dbmanager import DBManager

class DBLAgreement(BaseFile):
    def __init__(self, db: DBManager, agreement_id, license_code):
        self.db = db
        self.log = None

        self.translation = None
        self.translation_file_path = None
        self.this_file_path = None
        self.file_id = None

        self.agreement_id = agreement_id
        self.license_code = license_code

        self.valid = False
        self.exists = False

        self.new = False # Is this a newly introduced agreement?

        self.details = {}

        self.read = USXReadBoundary(db)
        self.write = USXWriteBoundary(db)

        self.check_agreement_exists(agreement_id)

    def get_valid(self):
        return self.valid
    
    def get_exists(self):
        return self.exists
    
    def is_new(self):
        return self.new
    
    def get_details(self, key):
        if key is not None:
            return self.details.get(key)
        else:
            return self.details
        
    def get_agreement_id(self):
        return self.agreement_id

    def check_agreement_exists(self, agreement_id):
        found = self.read.find_agreement(
            agreement_id=agreement_id
        )
        if found: # i.e. != None
            self.exists = True
            self.check_agreement_valid()
        else:
            self.new = True
            self.write.init_agreement(self.agreement_id)

    def check_agreement_valid(self):
        # If license exists, and is not expired, license = valid
        self.valid = self.read.find_agreement_expired(self.agreement_id)

    # ======================================== MANUAL CALLS ========================================

    # Done After Translation Creation
    def set_translation(self, translation: Translation, translation_file_path: Path):
        self.translation = translation
        self.translation_file_path = translation_file_path

        self.log = translation.log

        self.upload_license_file()
        if self.exists == False and self.valid == False:
            self.create_agreement()

    # Done after MetaData processing
    def link_agreement_revision(self, revision):
        self.write.persist_agreement_revision_mapping(
            agreement_id=self.agreement_id, 
            revision=revision
        )

    # ----------------------------------------- DERIVATIVE -----------------------------------------

    def upload_license_file(self):
        file_name = "license.xml"

        object_start = self.translation.get_dbl_id()
        self.this_file_path = self.translation_file_path / file_name
        self.file_id = self.upload_file(
            object_name=f"{object_start}/{file_name}",
            file_path=self.this_file_path,
            content_type='application/xml',
            data_format="XML",
            version_note="Ingested: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

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

        self.create_agreement_attributes()

    def create_agreement_attributes(self):
        file_xml = BeautifulSoup(self.read_file(), "xml")
        
        publication_rights = file_xml.find("publicationRights")
        if not publication_rights:
            return

        for right in publication_rights.find_all(recursive=False):
            value = right.text.strip().lower()

            self.write.persist_agreement_attributes(
                agreement_id=self.agreement_id,
                attribute_code=right.name,          # allowIntroductions
                attribute_value=value == "true"     # bool
            )

    def check_license(self):
        if self.license_code == None:
            return None
        
        licence_id = self.read.find_license(license_code=self.license_code)
        return licence_id