from zipfile import ZipFile
from minio import Minio
from pathlib import Path
import os
from bs4 import BeautifulSoup
import psycopg2
import shutil
import re
import time
from label_studio_sdk import LabelStudio
import json

from book import Book

from dotenv import load_dotenv

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
        break

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL")
LABEL_STUDIO_API_TOKEN = os.getenv("LABEL_STUDIO_API_TOKEN")

class MinioUSXUpload:
    def __init__(self, minio_client: Minio, medium, process_location, bucket, source_url, translation_id, dbl_id, agreement_id):
        self.client = minio_client
        self.medium = medium # Audio | Video | Text (USX)
        self.process_location = process_location
        self.bucket = bucket # The Minio bucket to create the files in.
        self.translation_id = translation_id
        self.dbl_id = dbl_id
        self.agreement_id = agreement_id

        # Adds a database connection
        self.conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD
        )

        self.revision = None

        self.cur = self.conn.cursor()

        self.start_time = time.time()

        self.source_id = self.get_source(source_url)

        print("✅ Starting Upload ...")

        # Fetch and print result
        # version = self.cur.fetchone()
        # print("Connected successfully! PostgreSQL version:", version)
        
        self.translation_title = f"{self.medium}-{self.dbl_id}-{self.agreement_id}"

        self.translation_name = None

        # self.stream_file("bible-raw", "text-65eec8e0b60e656b-246069/release/USX_1/1CH.usx")
        match medium:
            case "text": # USX Files e.g. for deeper analysis
                # unzip first
                self.unzip_folder(self.process_location)
            case "video": # Videos e.g. for the deaf (sign language)
                # self.check_files(self.process_location)
                pass
            case "audio": # Audio e.g. for the blind or preference
                self.check_files(self.process_location)

        self.conn.commit()

        duration = time.time() - self.start_time, 2
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration % 1) * 1000)  # or *100 for .mm format

        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

        print(f"✅ Completed Translation Import in [{formatted_duration}]!\n")

        # Create Label Studio Project for this specific translation of the bible
        label_studio_client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_TOKEN)
        # me = label_studio_client.users.whoami()

        # Should consider how else to do this
        project_label_config = """
        <View>
            <Relations>
                <Relation value="org:founded_by"/>
                <Relation value="org:founded"/>
            </Relations>
            <Labels name="label" toName="text">
                <Label value="PER" background="#e74c3c"/>        <!-- Red -->
                <Label value="LOC" background="#9b59b6"/>      <!-- Purple -->
                <Label value="GRP" background="#f1c40f"/>         <!-- Yellow -->
                <Label value="PRON" background="#27ae60"/>       <!-- Green -->
                <Label value="Divine" background="#3498db"/>   <!-- Light Blue -->
                <Label value="NOUN" background="#16a085"/>          <!-- Teal -->
                <Label value="APOS" background="#e67e22"/>  <!-- Orange -->
                <Label value="Q" background="#d35400"/>         <!-- Dark Orange -->
            </Labels>

            <Text name="text" value="$text"/>
        </View>
        """

        translation_project = label_studio_client.projects.create(
            title=self.translation_title,
            description=self.translation_name,
            label_config=project_label_config
        )

        # For now not sure how this works
        export_storage = label_studio_client.export_storage.s3.create(
            s3endpoint=f"http://{MINIO_ENDPOINT}", #Updated from localhost to hardcoded IP
            aws_access_key_id=MINIO_USERNAME,
            aws_secret_access_key=MINIO_PASSWORD,
            project=translation_project.id,
            bucket="bible-nlp",
            prefix=f"{self.translation_title}/exports/",
            title="TEST Export"
        )

        self.cur.execute("""
            INSERT INTO bible.labellingprojects (id) 
            VALUES (%s)
            RETURNING id;
        """, (
            translation_project.id,
        ))

        self.cur.execute("""
            INSERT INTO bible.translationlabellingprojects (translation_id, project_id) 
            VALUES (%s, %s)
            RETURNING id;
        """, (
            self.translation_id,
            translation_project.id
        ))

        self.conn.commit()
        self.conn.close()

    def get_source(self, source_url):
        # Find if url is already stored source in database
        self.cur.execute("""SELECT id FROM bible.sources WHERE url = %s;""", (source_url,))
        source_id = self.cur.fetchone()
        if source_id != None:
            return source_id[0]
        
        # If not create new and return it
        self.cur.execute("""
            INSERT INTO bible.sources (url) 
            VALUES (%s)
            RETURNING id;
        """, (source_url,))
        # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.sources",))
        return self.cur.fetchone()[0]

    def unzip_folder(self, zip_path):
        # This will unzip the zip folder, and then delete the original and replace process location with new path name
        downloads_location = Path(zip_path).parent

        with ZipFile(zip_path, 'r') as zip:
            # list all file paths in the ZIP
            all_files = zip.namelist()

            # find the top-level folder (first part before '/')
            top_levels = {Path(f).parts[0] for f in all_files if '/' in f}
            top_folder = next(iter(top_levels)) if top_levels else None

            # extract everything
            zip.extractall(downloads_location)

            # Saves the new location for the usx files to be ran in next part of pipeline
            new_location = downloads_location / top_folder
            self.check_files(new_location)

        # After unzipping delete the old zip file
        shutil.rmtree(zip_path, ignore_errors=True)
        if zip_path.is_dir():
            shutil.rmtree(zip_path, ignore_errors=True)  # delete folder + contents
        elif zip_path.is_file():
            Path(zip_path).unlink(missing_ok=True)

    def get_support_files(self, file_location, object_start, file_path, content_type):
        file_name = file_path.split("/")[-1]
        object_name = object_start + f"{file_name}"

        new_file_path = Path(file_location) / file_path
        if new_file_path.exists():
            return self.upload_file(object_name, new_file_path, content_type)
        
        return None
    
    def check_language(self, language_xml):
        # Check if language already added to database, if not create it and return language_id
        self.cur.execute("""SELECT id FROM bible.languages WHERE iso = %s;""", (language_xml.find("iso").text,))
        language_id = self.cur.fetchone()

        if language_id != None:
            return language_id[0]
        
        self.cur.execute("""
            INSERT INTO bible.languages (iso, name, namelocal, scriptdirection) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (
            language_xml.find("iso").text,
            language_xml.find("name").text,
            language_xml.find("nameLocal").text,
            language_xml.find("scriptDirection").text
        ))
        # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.languages",))
        return self.cur.fetchone()[0]
    
    def update_translationinfo_db(self, metadata_xml):
        self.language_id = self.check_language(metadata_xml.find("language"))
        self.cur.execute("""
            UPDATE bible.translationinfo
            SET medium = %s,
                name = %s,
                namelocal = %s,
                description = %s,
                abbreviationlocal = %s,
                language_id = %s
            WHERE dbl_id = %s;        
        """, (
            self.medium, 
            metadata_xml.find("identification").find("name").text, 
            metadata_xml.find("identification").find("nameLocal").text,
            metadata_xml.find("identification").find("description").text,
            metadata_xml.find("identification").find("abbreviationLocal").text,
            self.language_id,
            self.dbl_id
        ))

        self.create_translation_relationships(metadata_xml)

    def create_translation_relationships(self, metadata_xml):
        translation_relationships = metadata_xml.find("relationships")
        for relation in translation_relationships.find_all("relation"):
            # Example: <relation id="9879dbb7cfe39e4d" revision="4" type="text" relationType="source"/>
            relation_dbl_id = relation.get("id")
            relation_revision = relation.get("revision")
            relation_type = relation.get("relationType")
            self.cur.execute("""
                INSERT INTO bible.translationrelationships (from_translation, from_revision, to_translation, to_revision, type) 
                VALUES (%s, %s, %s, %s, %s)
            """, (self.translation_id, self.revision, relation_dbl_id, relation_revision, relation_type))

    def check_files(self, file_location):
        top_folder = str(file_location).split("\\")[-1]

        # Find metadata file
        metadata_file_path = Path(file_location) / "metadata.xml"
        metadata_file_content = ""
        with open(metadata_file_path, encoding="utf-8") as file:
            metadata_file_content = file.read()

        metadata_xml = BeautifulSoup(metadata_file_content, "xml")
        self.update_translationinfo_db(metadata_xml)
        self.translation_metadata_xml = metadata_xml
        translation_abbreviation = metadata_xml.find("identification").find("abbreviationLocal").text
        translation_full_name = metadata_xml.find("identification").find("name").text
        self.translation_name = f"{translation_abbreviation}: {translation_full_name}"

        self.revision = metadata_xml.find("DBLMetadata").get("revision")
        revision_note = metadata_xml.find("archiveStatus").find("comments")
        if revision_note != None:
            revision_note = revision_note.text

        object_start = f"{top_folder}/{self.revision}/"

        # Since dependant on language
        ldml_file = metadata_xml.select_one('resource[uri$=".ldml"]').get("uri")
        ldml_file_id = None
        if ldml_file is not None:
            ldml_file_id = self.get_support_files(file_location, object_start, ldml_file, "application/xml")

        # Update this information for translation in database
        self.cur.execute("""
            UPDATE bible.translations
            SET revision = %s,
                revision_note = %s,
                metadata_file = %s,
                license_file = %s,
                ldml_file = %s,
                versification_file = %s,
                style_file = %s
            WHERE id = %s;        
        """, (
            self.revision, 
            revision_note, 
            self.get_support_files(file_location, object_start, "metadata.xml", "application/xml"),
            self.get_support_files(file_location, object_start, "license.xml", "application/xml"),
            ldml_file_id,
            self.get_support_files(file_location, object_start, "release/versification.vrs", "application/xml"),
            self.get_support_files(file_location, object_start, "release/styles.xml", "application/xml"),
            self.translation_id
        ))

        self.conn.commit() # Commit all changes to database

        publication = metadata_xml.find("publication", default="true") # Get default files for publication
        contents = publication.find_all("content")

        # Selectively upload the files I want in the format I want (from metadata)
        for content in contents:
            # Get the file path for current file
            parts = content.get("src").split("/")
            file_name = parts[-1] # Get filename
            file_path = file_location
            for part in parts:
                file_path = file_path / part

            chapter_ref = content.get("role")
            book = chapter_ref.split(" ")[0]

            self.cur.execute("""
                SELECT code FROM bible.books WHERE code = %s;
            """, (book,))
            found_book = self.cur.fetchone()

            if found_book != None:
                # If this is text and the book is among ones we are interested in, take the file and upload it to minio
                object_name = f"{top_folder}/{self.revision}/{file_name}"
                content_type = metadata_xml.find("resource", uri=content.get("src")).get("mimeType")
                file_id = self.upload_file(object_name, file_path, content_type)

                book_info = metadata_xml.find("name", id=content.get("name"))
                short_name = book_info.find("short").text
                long_name = book_info.find("long").text
                
                # Then update the database linking to them
                if self.medium == "text":
                    self.cur.execute("""
                        INSERT INTO bible.booktofile (book_code, translation_id, file_id, short, long) VALUES (%s, %s, %s, %s, %s) RETURNING id;
                    """, (book, self.translation_id, file_id, short_name, long_name))
                    # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.booktofile",))
                    book_map_id = self.cur.fetchone()[0]

                    Book(self.language_id, self.translation_id, book_map_id, file_id, self.stream_file(object_name), self.conn)
                if self.medium == "audio":
                    # Audio and eventually video don't have any connection but in serving the files themselves for consumption
                    #   Maybe in the future some ML analysis but not needed right now or necesitates, using the class to build
                    #   Since below are all the database references it needs.
                    self.cur.execute("""
                        INSERT INTO bible.booktofile (book_code, translation_id, file_id, short, long) VALUES (%s, %s, %s, %s, %s) RETURNING id;
                    """, (book, self.translation_id, None, short_name, long_name))
                    # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.booktofile",))
                    book_map_id = self.cur.fetchone()[0]

                    self.cur.execute("""
                        INSERT INTO bible.chapteroccurences (chapter_ref, file_id, book_to_file_id) VALUES (%s, %s, %s);
                    """, (chapter_ref, file_id, book_map_id))
        
        self.conn.commit()

        print("Cleaning Up Artifacts...")
        
        if file_location.is_dir():
            shutil.rmtree(file_location, ignore_errors=True)  # delete folder + contents
        elif file_location.is_file():
            Path(file_location).unlink(missing_ok=True)

    def upload_file(self, object_name, file_path, content_type, bucket=None):
        if bucket == None:
            bucket = self.bucket
        self.client.fput_object(bucket, object_name, str(file_path), content_type=content_type)
        info = self.client.stat_object(self.bucket, object_name)
        # Example
            # Object(
            #     bucket_name='bible-dbl-raw', 
            #     object_name='text-65eec8e0b60e656b-246069/10/2JN.usx', 
            #     last_modified=datetime.datetime(2025, 10, 23, 16, 43, 21, tzinfo=datetime.timezone.utc), 
            #     etag='9b6bcda7e20ed8ffad0953711880191e', 
            #     size=3713, 
            #     metadata=HTTPHeaderDict(
            #         {'Accept-Ranges': 'bytes', 
            #          'Content-Length': '3713', 
            #          'Content-Type': 'application/xml', 
            #          'ETag': '"9b6bcda7e20ed8ffad0953711880191e"', 
            #          'Last-Modified': 'Thu, 23 Oct 2025 16:43:21 GMT', 
            #          'Server': 'MinIO', 
            #          'Strict-Transport-Security': 'max-age=31536000; includeSubDomains', 
            #          'Vary': 'Origin, Accept-Encoding', 
            #          'X-Amz-Id-2': 'dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8', 
            #          'X-Amz-Request-Id': '18712C730E5C7C9C', 
            #          'X-Content-Type-Options': 'nosniff', 
            #          'X-Ratelimit-Limit': '6778', 
            #          'X-Ratelimit-Remaining': '6778', 
            #          'X-Xss-Protection': '1; mode=block', 
            #          'Date': 'Thu, 23 Oct 2025 16:43:21 GMT'}), 
            #     version_id=None, 
            #     is_latest=None, 
            #     storage_class=None, 
            #     owner_id=None, 
            #     owner_name=None, 
            #     content_type='application/xml', 
            #     is_delete_marker=False, 
            #     tags=None, 
            #     is_dir=False
            # )
        
        self.cur.execute("""
            INSERT INTO bible.files (etag, type, file_path, bucket, source_id) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (info.etag, info.content_type, info.object_name, info.bucket_name, self.source_id))
        # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.files",))

        file_id = self.cur.fetchone()[0]

        if "versification" in object_name:
            self.createVersification(self.stream_file(object_name))
        elif "styles" in object_name:
            self.createStylesAndProperties(self.stream_file(object_name), file_id)
        # elif "ldml" in object_name:

        return file_id # Return file_id to link to

    # Make use and amend below function, to feed in files for processing (e.g. Book Classes)
    def stream_file(self, object_name):
        # Get file
        response = None 
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name,
            )
            # Read the data as bytes, then decode as UTF-8
            data = response.read().decode("utf-8")
            return data
        finally:
            if response:
                response.close()
                response.release_conn()
               
    def createStylesAndProperties(self, styles_string, styles_file_id):
        style_additions = 0
        property_additions = 0
        # We only set styles and properties once, since it is duplicated across all translations, just usx formatting.
        self.cur.execute("""SELECT last_value FROM bible.styles_id_seq;""")
        styles = self.cur.fetchone()[0]

        if styles > 1:
            return
        
        styles_xml = BeautifulSoup(styles_string, "xml")
        properties = styles_xml.find_all("property")

        previous_style_parent = None
        style_id = None

        for property in properties:
            style_parent = property.find_parent("style")
            
            property_name = property.get("name")
            property_unit = property.get("unit")
            property_value = property.text

            if style_parent == None:
                # General Properties (without a parent style in stylesheet)
                if property_unit != None:
                    self.cur.execute("""
                        INSERT INTO bible.properties (name, value, unit) 
                        VALUES (%s, %s, %s)
                    """, (property_name, property_value, property_unit))
                else:
                    self.cur.execute("""
                        INSERT INTO bible.properties (name, value) 
                        VALUES (%s, %s)
                    """, (property_name, property_value))

                continue

            if previous_style_parent != style_parent:
                # Create new style
                style = style_parent.get("id")
                style_name = style_parent.find("name").text
                style_description = style_parent.find("description").text
                style_versetext = style_parent.get("versetext")
                style_publishable = style_parent.get("publishable")

                self.cur.execute("""
                    INSERT INTO bible.styles (style, name, description, versetext, publishable, source_file_id) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (style, style_name, style_description, style_versetext, style_publishable, styles_file_id))

                # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.styles",))
                style_id = self.cur.fetchone()[0]

                previous_style_parent = style_parent

            if property_unit != None:
                self.cur.execute("""
                    INSERT INTO bible.properties (name, value, unit, style_id) 
                    VALUES (%s, %s, %s, %s)
                """, (property_name, property_value, property_unit, style_id))
            else:
                self.cur.execute("""
                    INSERT INTO bible.properties (name, value, style_id) 
                    VALUES (%s, %s, %s)
                """, (property_name, property_value, style_id))


        if style_additions > 0:
            print(f"[{style_additions}] Styles loaded into database")

        if property_additions > 0:
            print(f"[{property_additions}] Properties loaded into database")

    def createVersification(self, file_string):
        # file_xml = BeautifulSoup(file_string, "xml")
        # We can split file string by "#", remove blank ones, then grapb the relevant section
        #       by finding next index after sections we want, then read that line by line for each section

        file_sections_headers = [
            "# Verse number is the maximum verse number for that chapter.",
            "# Mappings from this versification to standard versification",
            "# Excluded verses",
            "# Verse segment information"
        ]
        
        # Build regexes that capture everything between headers (non-greedy, across lines)
        find_bible_info = re.escape(file_sections_headers[0]) + r"(.*?)" + re.escape(file_sections_headers[1])
        find_versification_map = re.escape(file_sections_headers[1]) + r"(.*?)" + re.escape(file_sections_headers[2])
        find_excluded_verses = re.escape(file_sections_headers[2]) + r"(.*?)" + re.escape(file_sections_headers[3])

        # Run searches
        matches = [
            re.search(find_bible_info, file_string, re.DOTALL),
            re.search(find_versification_map, file_string, re.DOTALL),
            re.search(find_excluded_verses, file_string, re.DOTALL)
        ]

        # Extract just the captured groups (excluding headers)
        file_sections = [m.group(1).strip() if m else "" for m in matches]

        self.createVerses(file_sections[0])
        self.createExcludedVerses(file_sections[2])
    
    def createExcludedVerses(self, section_text):
        additions = 0
        # Create list of excluded verses
        for line in section_text.splitlines():
            if line.startswith("#! -"):
                verse_ref = line[4:].strip()
                book_code = verse_ref[0:3]

                self.cur.execute("""
                    SELECT id FROM bible.books WHERE code=%s
                """, (book_code,))
                valid_book = self.cur.fetchone()

                if valid_book == None:
                    continue

                self.cur.execute("""
                    INSERT INTO bible.excludedverses (verse_ref, translation_id) 
                    VALUES (%s, %s)
                """, (verse_ref, self.translation_id))
                additions += 1

        if additions > 0:
            print(f"[{additions}] Excluded Verses added to database")
    
    def createVerses(self, section_text):
        additions = 0
        # Create all Verses Tables instances - different from VerseOccurences, just chceck they all exist
        for line in section_text.splitlines():
            sections = line.split(" ")
            book_code = sections[0]

            self.cur.execute("""
                SELECT id FROM bible.books WHERE code=%s
            """, (book_code,))
            book_id = self.cur.fetchone()

            if book_id == None:
                continue

            for chapter in range(1,len(sections)):
                chapter_num, verse_count = sections[chapter].split(":")
                chapter_ref = book_code + " " + chapter_num

                self.cur.execute("""
                    SELECT id FROM bible.chapters WHERE chapter_ref=%s
                """, (chapter_ref,))
                found_chapter = self.cur.fetchone()

                # Validates any non standard chapters that might apear outside ones initialised originally
                if found_chapter == None:
                    try:
                        print(book_code, int(chapter_num), chapter_ref)
                        self.cur.execute("""
                            INSERT INTO bible.chapters (book_code, chapter_num, chapter_ref, standard) 
                            VALUES (%s, %s, %s, %s);
                        """, (book_code, int(chapter_num), chapter_ref, False))
                    except Exception as e:
                        print(f"❌ Skipped Chapter Creation of [{chapter_ref}]")
                        # In the case it can't seem to create a new chapter then skip the chapter (won't take it as important)

                for verse in range(1, (int(verse_count)+1)):
                    verse_ref = chapter_ref + ":" + str(verse)

                    self.cur.execute("""
                        SELECT id FROM bible.verses WHERE verse_ref=%s
                    """, (verse_ref,))
                    verse_id = self.cur.fetchone()

                    if verse_id == None:
                        self.cur.execute("""
                            INSERT INTO bible.verses (chapter_ref, verse_ref, verse) 
                            VALUES (%s, %s, %s)
                        """, (chapter_ref, verse_ref, str(verse)))
                        additions += 1
        
        if additions > 0:
            print(f"[{additions}] Verses Initialized into database")