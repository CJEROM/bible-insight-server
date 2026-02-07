from ingestor.usx.files.base_file import BaseFile
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from pathlib import Path

from ingestor.usx.book import Book

from ingestor.usx.files.ldml import LDML
from ingestor.usx.files.styles import Styles
from ingestor.usx.files.versification import Versification

from database.boundary.usx_boundary import USXReadBoundary, USXWriteBoundary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager
    from ingestor.usx.files.agreements import DBLAgreement

class Metadata(BaseFile):
    def __init__(self, translation_file_path: Path, log: "LogManager", source_url, main_manager: "ManagerHandler", agreement: "DBLAgreement"):
        self.translation_file_path  = translation_file_path
        self.log                    = log
        self.manager                = main_manager
        self.obj                    = main_manager.get_obj()
        self.db                     = main_manager.get_db()
        # self.label                  = main_manager.get_label()
        self.dbl_agreement          = agreement

        self.read               = USXReadBoundary(self.db)
        self.write              = USXWriteBoundary(self.db)

        # Now should it create a new source every time it downloads? 
        #       or have the same one for this translation
        self.source_id          = None
        self.source_url         = source_url

        self.metadata           = {}

        self.translation_id     = None
        self.translation_name   = None
        self.language_id        = None

        # Object Storage Start Path
        self.object_start       = None

        self.ingestion_start    = self.get_time()

        self.styles         = None
        self.ldml           = None
        self.versification  = None

        self.read_metadata_file(translation_file_path)

    def get_time(self):
        return datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")

    def get_metadata(self, key:str = None):
        if key is not None:
            return self.metadata.get(key)
        return self.metadata
    
    def get_translation_name(self):
        return self.translation_name
    
    def get_object_start(self):
        return self.object_start

    def extract_metadata(self, metadata_xml: BeautifulSoup):
        self.metadata["language_iso"]   = metadata_xml.find("language").find("iso").text
        self.metadata["language_name"]  = metadata_xml.find("language").find("name").text
        self.metadata["language_local"] = metadata_xml.find("language").find("nameLocal").text
        self.metadata["script"]         = metadata_xml.find("language").find("script").text
        self.metadata["scriptCode"]     = metadata_xml.find("language").find("scriptCode").text
        self.metadata["scriptDirection"]= metadata_xml.find("language").find("scriptDirection").text
        self.metadata["ldml"]           = metadata_xml.find("language").find("ldml").text
        self.metadata["numerals"]       = metadata_xml.find("language").find("numerals").text

        self.metadata["abbreviation"]   = metadata_xml.find("identification").find("abbreviation").text
        self.metadata["abbreviationLocal"]   = metadata_xml.find("identification").find("abbreviationLocal").text
        self.metadata["name"]           = metadata_xml.find("identification").find("name").text
        self.metadata["nameLocal"]      = metadata_xml.find("identification").find("nameLocal").text
        self.metadata["description"]    = metadata_xml.find("identification").find("description").text
        self.metadata["medium"]         = metadata_xml.find("type").find("medium").text

        self.metadata["copyright"]      = metadata_xml.find("copyright").find("statementContent").text
        self.metadata["promotion"]      = metadata_xml.find("promotion").find("promoVersionInfo").text

        self.metadata["revision"]       = int(metadata_xml.find("DBLMetadata").get("revision"))
        self.metadata["revision_note"]  = metadata_xml.find("archiveStatus").find("comments").text
        self.metadata["revision_date"]  = metadata_xml.find("archiveStatus").find("dateUpdated").text

        self.metadata["dbl_id"]         = metadata_xml.find("DBLMetadata").get("id")
        self.metadata["file_version"]   = metadata_xml.find("DBLMetadata").get("version")

        self.translation_name           = f"{self.metadata["abbreviation"]}: {self.metadata["name"]}"

        self.log.log_to_file(f"Extracted Metedata!", "METADATA", "DEBUG")

    def create_translation_relationships(self, metadata_xml: BeautifulSoup):
        translation_relationships = metadata_xml.find("relationships")
        for relation in translation_relationships.find_all("relation"):
            # Example: <relation id="9879dbb7cfe39e4d" revision="4" type="text" relationType="source"/>
            relation_dbl_id     = relation.get("id")
            relation_revision   = relation.get("revision")
            relation_type   = relation.get("relationType")

            self.write.persist_translation_relation(
                from_dbl_id     = self.get_metadata("dbl_id"),
                from_revision   = self.get_metadata("revision"),
                to_dbl_id       = relation_dbl_id,
                to_revision     = relation_revision,
                relation_type   = relation_type
            )
            self.log.log_to_file(f"Created Translation Relationship with [ID: {relation_dbl_id}] [Revision: {relation_revision}] [medium: {relation_type}]", "METADATA", "DEBUG")

    def match_language(self):
        # Should find what language we are in
        self.get_metadata("language_iso")
        self.get_metadata("language_name")
        self.get_metadata("language_local")

        # Match Script?
        self.get_metadata("script")
        self.get_metadata("scriptCode")
        self.get_metadata("scriptDirection")
        self.get_metadata("ldml")

        # Match number system?
        self.get_metadata("numerals")

        # Method may change as Language Ingestion is completed
        #   Currently relies on language already existing in DB to be succesful
        language_id = self.read.find_language(
            iso_code=self.get_metadata("language_iso")
        )

        self.log.log_to_file(f"Matched language for translation to ID: {language_id} with ISO: {self.get_metadata("language_iso")}!", "METADATA", "DEBUG")
    
        self.language_id = language_id

        return language_id

    def create_translation_details(self):
        self.translation_id = self.write.persist_usx_translation(
            dbl_id              = self.get_metadata("dbl_id"),
            revision            = self.get_metadata("revision"),
            revision_note       = self.get_metadata("revision_note"),
            revision_date       = self.get_metadata("revision_date"),
            medium              = self.get_metadata("medium"),
            name                = self.get_metadata("name"),
            name_local          = self.get_metadata("nameLocal"),
            abbreviation        = self.get_metadata("abbreviation"),
            abbreviationLocal   = self.get_metadata("abbreviationLocal"),
            copyright           = self.get_metadata("copyright"),
            promotion           = self.get_metadata("promotion"),
            language_id         = self.match_language()
        )

        self.log.log_to_file(f"Created Translation Entry -> ID = {self.translation_id}!", "METADATA", "DEBUG")

    def create_dbl_info(self):
        # If the agreement is new then mark as test import
        self.log.log_to_file(f"Creating DBL INFO Entry ...", "METADATA", "DEBUG")
        self.write.persist_translation_info(
            dbl_id              = self.get_metadata("dbl_id"),
            revision            = self.get_metadata("revision"),
            is_supported        = True,
            is_test_import      = self.dbl_agreement.is_new()
        )
        self.log.log_to_file(f"DBL INFO Created!", "METADATA", "DEBUG")
        # Non test translation's are those that are included in initial DB seeding

    def validate_translation_import(self) -> bool:
        dbl_id      = self.get_metadata("dbl_id")
        revision    = self.get_metadata("revision")
        self.log.log_to_file(f"Validating Translation Import ...", "METADATA", "DEBUG")

        # 1. Check if translation / revision already exists
        existing_translation = self.read.find_translation(
            dbl_id      = dbl_id,
            revision    = revision
        )

        if existing_translation is not None:
            self.log.log_to_file(f"Validating Result = FAIL -> Translation already exists!", "METADATA", "DEBUG")
            return False

        # 2. Check if translation / revision is supported
        is_supported = self.read.is_translation_supported(
            dbl_id      = dbl_id,
            revision    = revision
        )

        if is_supported is None:
            self.log.log_to_file(f"Validating Result = PASS. New Translation will be marked as Test Import!", "METADATA", "DEBUG")
            return True

        if not is_supported:
            self.log.log_to_file(f"Validating Result = FAIL -> Translation NOT supported!", "METADATA", "DEBUG")
            return False

        self.log.log_to_file(f"Validating Result = PASS!", "METADATA", "DEBUG")
        return True
    
    def create_source(self, source_url):
        # Find if url is already stored source in database
        self.log.log_to_file(f"Creating Translation Source!", "METADATA", "DEBUG")

        source_unique_code  = f"DBL-{self.get_metadata("abbreviation")}"
        source_id           = self.read.find_source(code=source_unique_code)

        if source_id != None:
            self.dbl_agreement.set_source(source_id)
            self.log.log_to_file(f"Translation Source Already Exists, with ID [{source_id}]!", "METADATA", "DEBUG")
            return source_id
        
        # Find parent source (DBL - Distrubtor) - In the future customise to link to publishers better?
        parent_source_id = self.read.find_source(code='DBL')
        self.log.log_to_file(f"DBL Parent Source found with ID [{parent_source_id}]!", "METADATA", "DEBUG")
        
        # If not create new and return it
        new_source_id = self.write.persist_source(
            source_type         = "DAT", # Dataset
            code                = source_unique_code,
            name                = self.get_metadata("name"),
            description         = self.get_metadata("description"),
            version             = None,   # self.get_metadata("file_version")
            url                 = source_url,
            note                = None,
            parent_source       = parent_source_id,
            # official_citation=,
            # date_published=,
            # metadata=,
        )

        self.dbl_agreement.set_source(new_source_id)

        self.log.log_to_file(f"Created New Source [ID: {new_source_id}] [URL: {source_url}]", "METADATA", "INFO")
        return new_source_id
    
    def create_source_mappings(self):
        # For mapping publishers etc. to translation from metadata information we receive

        # Only required on first instance of creation of source for a particular translation
        pass

    def read_metadata_file(self, file_path):
        file_name               = "metadata.xml"
        metadata_file_path      = Path(file_path) / file_name
        self.this_file_path     = metadata_file_path
        metadata_file_content   = ""

        with open(metadata_file_path, encoding="utf-8") as file:
            metadata_file_content = file.read()

        metadata_xml = BeautifulSoup(metadata_file_content, "xml")

        self.extract_metadata(metadata_xml)

        # We don't rely on agreement to store files, we build from dbl_id and revision
        self.object_start = f"{self.get_metadata("dbl_id")}/{self.get_metadata("revision")}"

        self.source_id = self.create_source(self.source_url)

        file_id = self.upload_file(
            object_name     = f"{self.object_start}/{file_name}",
            file_path       = self.this_file_path,
            content_type    = 'application/xml',
            data_format     = "XML",
            version_note    = self.get_metadata("file_version")
        )

        self.log.log_to_file(f"Uploaded Metadata file with ID [{file_id}]!", "METADATA", "DEBUG")

        valid = self.validate_translation_import()

        ingestion_id = self.write.start_ingestion(
            source_id       = self.source_id,
            start_time      = self.ingestion_start
        )
        self.log.log_to_file(f"Ingestion Started!", "METADATA", "INFO")

        if valid:
            self.create_dbl_info()
            self.create_translation_details()
            self.create_translation_relationships(metadata_xml)

            self.write.persist_translation_file( # Map Metadata to Translation through translation_files table
                translation_id  = self.translation_id,
                file_id         = file_id,
                type            = "Metadata",
                version         = self.get_metadata("file_version")
            )
            
            self.upload_support_files(metadata_xml)
            self.get_book_files(metadata_xml)

            self.write.end_ingestion(
                ingestion_id    = ingestion_id,
                end_time        = self.get_time()
            )

            # Create Label Studio Project for this specific translation of the bible
            self.labelproject = self.label.create_new_translation_project(
                translation_id      = self.translation_id, 
                project_name        = self.get_metadata("name"), 
                project_description = f"{self.get_metadata("dbl_id")}-{self.dbl_agreement.get_id()}"
            )
        else:
            self.write.end_ingestion(
                ingestion_id    = ingestion_id,
                end_time        = self.get_time(),
                error_message   = "Translation invalid!"
            )
            # Consider deleting data so far on failure

    def upload_support_files(self, metadata_xml: BeautifulSoup):
        # License File => Passed on, and not stored in metadata
        ldml_file           = metadata_xml.select_one('resource[uri$=".ldml"]')         # Ends with
        versification_file  = metadata_xml.select_one('resource[uri*="versification"]') # Contains
        styles_file         = metadata_xml.select_one('resource[uri*="styles"]')        # Contains

        self.populate_support_file(versification_file,  "TXT", None)
        self.populate_support_file(styles_file,         "XML", "1.0")
        self.populate_support_file(ldml_file,           "LDML", None)

    def populate_support_file(self, 
            file_metadata_xml: Tag, 
            data_format: str, 
            version_notes: str = None
        ):

        # In the case of Audio - we only get metadata support file, so skip the rest
        if file_metadata_xml == None:
            return
        
        uri         = file_metadata_xml.get("uri")
        mimeType    = file_metadata_xml.get("mimeType")

        file_name = uri.split("/")[-1]
        file_extension = file_name.split(".")[1]

        new_file_path = Path(self.translation_file_path) / uri

        # Write File to DB
        file_id = self.upload_file(
            object_name     = f"{self.object_start}/{file_name}",
            file_path       = new_file_path,
            content_type    = mimeType,
            data_format     = data_format,
            version_note    = version_notes
        )

        # Write Translation File Map to DB
        support_file_type = file_name.split(".")[0].capitalize()
        if file_extension == ".ldml":
            support_file_type = "LDML"
        self.log.log_to_file(f"Uploaded {support_file_type} file with ID [{file_id}]!", "METADATA", "DEBUG")

        self.write.persist_translation_file(
            translation_id  = self.translation_id,
            file_id         = file_id,
            type            = support_file_type,
            version         = version_notes
        )
        self.log.log_to_file(f"Mapped File to Translation ID [{self.translation_id}]!", "METADATA", "DEBUG")

        match file_name.split(".")[0].capitalize():
            case "Versification":
                self.versification  = Versification(
                    translation_id  = self.translation_id,
                    main_manager    = self.manager,
                    log             = self.log,
                    source_id       = self.source_id,
                    file_path       = new_file_path
                )
            case "Styles":
                self.styles         = Styles(
                    styles_file_id  = file_id,
                    main_manager    = self.manager, 
                    log             = self.log, 
                    source_id       = self.source_id, 
                    file_path       = new_file_path
                )
            case "LDML":
                self.ldml           = LDML(
                    main_manager    = self.manager, 
                    log             = self.log, 
                    source_id       = self.source_id, 
                    file_path       = new_file_path
                )

    def get_book_files(self, metadata_xml: BeautifulSoup):
        contents = metadata_xml.find("publication", default="true").find_all("content")

        self.log.log_to_file(f"Starting Bible Book processing ...", "METADATA", "DEBUG")

        self.log.set_progress_total(len(contents))

        # Selectively upload the files I want in the format I want (from metadata)
        for i, (content) in enumerate(contents):
            # Get the file path for current file
            parts = content.get("src").split("/")
            file_name = parts[-1] # Get filename
            file_path = self.translation_file_path
            for part in parts:
                file_path = file_path / part

            chapter_ref = content.get("role")
            book = chapter_ref.split(" ")[0]

            # Check whether book code is among those in DB (the ones we want to store)
            found_book = self.read.find_book(book_code=book)
            if found_book: # if not None, then it is one we want

                # Prepare data
                object_name = f"{self.object_start}/{file_name}"
                resource    = metadata_xml.find("resource", uri=content.get("src"))
                mimeType    = resource.get("mimeType")

                book_info   = metadata_xml.find("name", id=content.get("name"))
                short_name  = book_info.find("short").text
                long_name   = book_info.find("long").text

                # Responsible for mapping file depening on medium
                if self.get_metadata("medium") == "text":
                    # Upload files and mapping
                    file_id = self.upload_file(
                        object_name     = object_name,
                        file_path       = file_path,
                        content_type    = mimeType,
                        data_format     = "USX",
                        version_note    = "3.0" # USX version used, add as note (why not)
                    )

                    book_map_id = self.write.persist_book_file(
                        book_code       = book,
                        translation_id  = self.translation_id,
                        file_id         = file_id,
                        short           = short_name,
                        long            = long_name
                    )

                    # We are uploading Books
                    Book(self, book, book_map_id, file_id, file_path, self.log)   

                    self.log.set_progress(found_book, i+1)  

                elif self.get_metadata("medium") == "audio":
                    # Upload files and mapping
                    file_id = self.upload_file(
                        object_name     = object_name,
                        file_path       = file_path,
                        content_type    = mimeType,
                        data_format     = "MP3"
                    )

                    book_map_id = self.write.persist_book_file(
                        book_code       = book,
                        translation_id  = self.translation_id,
                        file_id         = None, # Audio only has chapter files and no book files
                        short           = short_name,
                        long            = long_name
                    )

                    # We are uploading Chapters - 
                    #   We create Chapter Occurence since no further text processing and no audio processsing pipeline
                    self.write.persist_chapter_occurence(
                        chapter_ref     = chapter_ref,
                        book_map_id     = book_map_id,
                        translation_id  = self.translation_id
                    )

                    self.log.set_progress(chapter_ref, i+1)
