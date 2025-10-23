from zipfile import ZipFile
from minio import Minio
from pathlib import Path
import os
from bs4 import BeautifulSoup
import psycopg2
import shutil

class MinioUSXUpload:
    def __init__(self, minio_client: Minio, medium, process_location, bucket, source_url, translation_id):
        self.client = minio_client
        self.medium = medium # Audio | Video | Text (USX)
        self.process_location = process_location
        self.bucket = bucket # The Minio bucket to create the files in.
        self.translation_id = translation_id

        # Adds a database connection
        self.conn = psycopg2.connect(
            host="REDACTED_IP",
            port=5444,
            dbname="postgres",
            user="postgres",
            password="REDACTED_PASSWORD"
        )

        self.cur = self.conn.cursor()

        self.source_id = self.get_source(source_url)

        print("✅ Starting Upload ...")

        # Fetch and print result
        # version = self.cur.fetchone()
        # print("Connected successfully! PostgreSQL version:", version)

        self.metadata_content = ""

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
        self.cur.close()
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
            VALUES (%s);
        """, (source_url,))
        self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.sources",))
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
            print(new_location)
            self.check_files(new_location)

        # After unzipping delete the old zip file
        shutil.rmtree(zip_path, ignore_errors=True)
        if zip_path.is_dir():
            shutil.rmtree(zip_path, ignore_errors=True)  # delete folder + contents
        elif zip_path.is_file():
            Path(zip_path).unlink(missing_ok=True)

    def check_files(self, file_location):
        top_folder = str(file_location).split("\\")[-1]
        
        # Get License file
        license_file_path = Path(file_location) / "license.xml" # Only if there is an expiration on the license
        if license_file_path.exists():
            pass

        # Find metadata file
        metadata_file_path = Path(file_location) / "metadata.xml"
        metadata_file_content = ""
        with open(metadata_file_path, encoding="utf-8") as file:
            metadata_file_content = file.read()

        metadata_xml = BeautifulSoup(metadata_file_content, "xml")
        revision = metadata_xml.find("DBLMetadata").get("revision")

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
                object_name = f"{top_folder}/{revision}/{file_name}"
                content_type = metadata_xml.find("resource", uri=content.get("src")).get("mimeType")
                file_id = self.upload_file(object_name, file_path, content_type)

                book_info = metadata_xml.find("name", id=content.get("name"))
                short_name = book_info.find("short").text
                long_name = book_info.find("long").text
                
                # Then update the database linking to them
                if self.medium == "text":
                    self.cur.execute("""
                        INSERT INTO bible.booktofile (book_code, translation_id, file_id, short, long) VALUES (%s, %s, %s, %s, %s);
                    """, (book, self.translation_id, file_id, short_name, long_name))
                if self.medium == "audio":
                    self.cur.execute("""
                        INSERT INTO bible.booktofile (book_code, translation_id, file_id, short, long) VALUES (%s, %s, %s, %s, %s);
                    """, (book, self.translation_id, None, short_name, long_name))

                    self.cur.execute("""
                        INSERT INTO bible.chapteroccurences (chapter_ref, file_id) VALUES (%s, %s);
                    """, (chapter_ref, file_id))
        
        self.conn.commit()
        
        if file_location.is_dir():
            shutil.rmtree(file_location, ignore_errors=True)  # delete folder + contents
        elif file_location.is_file():
            Path(file_location).unlink(missing_ok=True)

    def upload_file(self, object_name, file_path, content_type):
        self.client.fput_object(self.bucket, object_name, str(file_path), content_type=content_type)
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
        """, (info.etag, info.content_type, info.object_name, info.bucket_name, self.source_id))
        self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.files",))

        return self.cur.fetchone() # Return file_id to link to

    # Make use and amend below function, to feed in files for processing (e.g. Book Classes)
    def stream_file(self, object_name):
        # Get file
        response = None 
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name,
            )
            print(str(response.data))
        finally:
            if response:
                response.close()
                response.release_conn()
               