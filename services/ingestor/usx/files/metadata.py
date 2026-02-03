from base_file import BaseFile
from bs4 import BeautifulSoup
from pathlib import Path

from ingestor.usx.translation import Translation
from ingestor.usx.book import Book

from ldml import LDML
from styles import Styles
from versification import Versification

class Metadata(BaseFile):
    def __init__(self, this_translation: Translation, translation_file_path: Path):
        self.translation_file_path = translation_file_path
        self.metadata = {

        }

        self.this_translation = this_translation
        self.translation_id = this_translation.get_translation_id()
        self.translation_name = None

        # Object Storage Start Path
        self.object_start = None

        self.read_metadata_file(translation_file_path)

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

        self.metadata["abbreviation"]   = metadata_xml.find("identification").find("abbreviationLocal").text
        self.metadata["name"]           = metadata_xml.find("identification").find("name").text
        self.metadata["nameLocal"]      = metadata_xml.find("identification").find("nameLocal").text
        self.metadata["description"]    = metadata_xml.find("identification").find("description").text
        self.metadata["medium"]         = metadata_xml.find("type").find("medium").text

        self.metadata["copyright"]      = metadata_xml.find("copyright").find("statementContent").text
        self.metadata["promotion"]      = metadata_xml.find("promotion").find("promoVersionInfo").text

        self.metadata["revision"]       = metadata_xml.find("DBLMetadata").get("revision")
        self.metadata["revision_note"]  = metadata_xml.find("archiveStatus").find("comments").text
        self.metadata["revision_date"]  = metadata_xml.find("archiveStatus").find("dateUpdated").text

        self.metadata["dbl_id"]         = metadata_xml.find("DBLMetadata").find("id").text
        self.metadata["file_version"]   = metadata_xml.find("DBLMetadata").find("version").text

        self.translation_name           = f"{self.metadata["abbreviation"]}: {self.metadata["name"]}"

    def create_translation_relationships(self, metadata_xml: BeautifulSoup):
        translation_relationships = metadata_xml.find("relationships")
        for relation in translation_relationships.find_all("relation"):
            # Example: <relation id="9879dbb7cfe39e4d" revision="4" type="text" relationType="source"/>
            relation_dbl_id = relation.get("id")
            relation_revision = relation.get("revision")
            relation_type = relation.get("relationType")
            self.db.execute("""
                INSERT INTO bible.translationrelationships (from_translation, from_revision, to_translation, to_revision, type) 
                VALUES (%s, %s, %s, %s, %s)
            """, (self.translation_id, self.revision, relation_dbl_id, relation_revision, relation_type))
            self.log.log_to_file(f"Created Translation Relationship with [ID: {relation_dbl_id}] [Revision: {relation_revision}] [medium: {relation_type}]", "TRANSLATION", "DEBUG")

    # TO DO
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
    
        return language_id

    def update_translation_details(self):
        self.write.update_usx_translation(
            translation_id  = self.translation_id,
            revision        = self.get_metadata("revision"),
            revision_note   = self.get_metadata("revision_note"),
            revision_date   = self.get_metadata("revision_date"),
            medium          = self.get_metadata("medium"),
            name            = self.get_metadata("name"),
            name_local      = self.get_metadata("nameLocal"),
            abbreviation    = self.get_metadata("abbreviation"),
            copyright       = self.get_metadata("copyright"),
            promotion       = self.get_metadata("promotion"),
            language_id     = self.match_language()
        )

    # TO DO
    def update_agreement_mapping(self):
        pass

    def read_metadata_file(self, file_path):
        metadata_file_path = Path(file_path) / "metadata.xml"
        self.this_file_path = metadata_file_path
        metadata_file_content = ""
        with open(metadata_file_path, encoding="utf-8") as file:
            metadata_file_content = file.read()

        metadata_xml = BeautifulSoup(metadata_file_content, "xml")

        self.extract_metadata(metadata_xml)

        # We don't rely on agreement to store files, we build from dbl_id and revision
        self.object_start = f"{self.get_metadata("dbl_id")}/{self.get_metadata("revision")}/"

        self.update_translation_details()
        self.create_translation_relationships(metadata_xml)
        self.upload_support_files(metadata_xml)
        self.get_book_files(metadata_xml)

    def upload_support_files(self, metadata_xml: BeautifulSoup):
        # License File => Passed on, and not stored in metadata
        ldml_file           = metadata_xml.select_one('resource[uri$=".ldml"]')
        versification_file  = metadata_xml.select_one('resource[uri$="versification"]')
        styles_file         = metadata_xml.select_one('resource[uri$="styles"]')
        metadata_file       = metadata_xml.select_one('resource[uri$="metadata"]')

        self.populate_support_file(metadata_file,       "XML", self.get_metadata("file_version"))
        self.populate_support_file(versification_file,  "TXT", None)
        self.populate_support_file(styles_file,         "XML", "1.0")
        self.populate_support_file(ldml_file,           "LDML", None)

    def populate_support_file(self, 
            file_metadata_xml: BeautifulSoup, 
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
            object_name=self.object_start + file_name,
            file_path=new_file_path,
            content_type=mimeType,
            data_format=data_format,
            version_note=version_notes
        )

        # Write Translation File Map to DB
        support_file_type = file_name.split(".")[0].capitalize()
        if file_extension == ".ldml":
            support_file_type = "LDML"

        self.write.persist_translation_file(
            translation_id=self.translation_id,
            file_id=file_id,
            type=support_file_type,
            version=version_notes
        )

        match file_name.split(".")[0].capitalize():
            case "Versification":
                Versification(self.manager, self.log, self.source_id, new_file_path)
            case "Styles":
                Styles(self.manager, self.log, self.source_id, new_file_path, file_id)
            case "LDML":
                LDML(self.manager, self.log, self.source_id, new_file_path)

    def get_book_files(self, metadata_xml: BeautifulSoup):
        contents = metadata_xml.find("publication", default="true").find_all("content")

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
                resource = metadata_xml.find("resource", uri=content.get("src"))
                mimeType = resource.get("mimeType")

                book_info = metadata_xml.find("name", id=content.get("name"))
                short_name = book_info.find("short").text
                long_name = book_info.find("long").text

                # Responsible for mapping file depening on medium
                if self.get_metadata("medium") == "text":
                    # Upload files and mapping
                    file_id = self.upload_file(
                        object_name=object_name,
                        file_path=file_path,
                        content_type=mimeType,
                        data_format="USX",
                        version_note="3.0" # USX version used, add as note (why not)
                    )

                    book_map_id = self.write.persist_book_file(
                        book_code=book,
                        translation_id=self.translation_id,
                        file_id=file_id,
                        short=short_name,
                        long=long_name
                    )

                    # We are uploading Books
                    Book(self, found_book, book_map_id, file_id, self.obj.stream_file(object_name), self.log)   

                    self.log.set_progress(found_book, i+1)  

                elif self.get_metadata("medium") == "audio":
                    # Upload files and mapping
                    file_id = self.upload_file(
                        object_name=object_name,
                        file_path=file_path,
                        content_type=mimeType,
                        data_format="MP3"
                    )

                    book_map_id = self.write.persist_book_file(
                        book_code=book,
                        translation_id=self.translation_id,
                        file_id=None, # Audio only has chapter files and no book files
                        short=short_name,
                        long=long_name
                    )

                    # We are uploading Chapters - 
                    #   We create Chapter Occurence since no further text processing and no audio processsing pipeline
                    self.write.persist_chapter_occurence(
                        chapter_ref=chapter_ref,
                        book_map_id=book_map_id,
                        translation_id=self.translation_id
                    )

                    self.log.set_progress(chapter_ref, i+1)
