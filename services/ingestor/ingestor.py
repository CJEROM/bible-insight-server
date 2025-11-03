import requests
from bs4 import BeautifulSoup
import psycopg2

from playwright.sync_api import sync_playwright
import os
import time
from minio import Minio
from pathlib import Path

from miniousxupload import MinioUSXUpload

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

DBL_USERNAME = os.getenv("DBL_USERNAME")
DBL_PASSWORD = os.getenv("DBL_PASSWORD")

class Ingestor:
    def __init__(self):
        # Worth adding option, that if dbl_id and agreement_id have been passed in, run just the class for that translation
        #       This would be useful when enforcing foreign key constraints with translation relationships

        # Folder where you want downloads to go
        self.download_path = "C:/Users/CephJ/Documents/git/bible-insight-server/downloads"
        os.makedirs(self.download_path, exist_ok=True)

        # Passes Minio client connection on to the MinioUSXUpload class
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_USERNAME,
            secret_key=MINIO_PASSWORD,
            secure=False
        )

        self.conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USERNAME,
            password=POSTGRES_PASSWORD
        )

        self.cur = self.conn.cursor()

        self.get_downloads()

        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def expand_all_folders(self, page):
        """
        Expands all collapsible folders on the DBL download page
        so that every nested level (release, audio, ROM, etc.) becomes visible.
        """

        while True:
            # Find all buttons that can expand folders
            expand_buttons = page.query_selector_all("button[aria-label^='Expand ']")

            if not expand_buttons:
                # No more expandable folders found
                break

            print(f"Found {len(expand_buttons)} folders to expand...")

            for btn in expand_buttons:
                try:
                    label = btn.get_attribute("aria-label")
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    time.sleep(0.3)  # small delay for DOM update
                except Exception as e:
                    print(f"⚠️ Failed to expand {label}: {e}")

            # Allow time for the page to render new nested folders
            time.sleep(0.5)

        print("✅ All folders expanded.")

    def get_translation(self, dbl_id, agreement_id):
        agreement_id = str(agreement_id)
        self.cur.execute("""
            SELECT id FROM bible.translations WHERE dbl_id = %s AND agreement_id = %s;
        """, (dbl_id, agreement_id))

        # If the translation already exists, then quit processing this translation
        translation_id = self.cur.fetchone()
        if translation_id != None:
            return -1
        
        # If not create a new entry and pass along the new id        
        self.cur.execute("""
            INSERT INTO bible.translationinfo (dbl_id) VALUES(%s)
            ON CONFLICT (dbl_id) DO NOTHING;
        """, (dbl_id,))

        self.cur.execute("""
            INSERT INTO bible.translations (dbl_id, agreement_id) VALUES(%s, %s) RETURNING id;
        """, (dbl_id, agreement_id))
        self.conn.commit()

        # self.cur.execute("""SELECT currval(pg_get_serial_sequence(%s, 'id'));""", ("bible.translations",))
        return self.cur.fetchone()[0] # Return file_id to link to

    def get_downloads(self):
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)  # headless=False shows the browser
            context = browser.new_context(accept_downloads=True)  # Important to handle downloads

            page = context.new_page()
        
            # Go to the normal page
            page.goto("https://app.library.bible/")

            page.wait_for_load_state("networkidle") # Wait until no network requests for ~500ms (are we being redirected to login?)

            # Do we need to login?
            if page.query_selector("input[name='email']"):
                print("Need to log in")
                # Fill in the username/email and password
                page.fill("input[name='email']", DBL_USERNAME)
                page.fill("input[name='password']", DBL_PASSWORD)
                page.click("button#rememberMe") # Try Remember me for 30 days, to prevent excessive logging and checking

                # Click the login button
                page.click("button:has-text('Sign in')")

                # Wait for navigation after login
                page.wait_for_url("https://app.library.bible/")
                print("✅ Succesful Log In")
            else:
                print("Already logged in")

            self.cur.execute("""
                SELECT dbl_id, agreement_id FROM bible.DBLInfo;
            """)

            for dbl_id, agreement_id in self.cur.fetchall():

                translation_id = self.get_translation(dbl_id, agreement_id)
                if translation_id == -1:
                    print(f"❌ Translation {dbl_id}-{agreement_id} already exists! Skipping ...")
                    continue # Skip because its already in our system

                print(f"✅ Starting Translation {dbl_id}-{agreement_id} Processing!")

                new_path = None

                # dbl_id = "52a82b80a85343c5"
                # agreement_id = 279707

                # Go to the DBL translation page
                url = "https://app.library.bible/content/" + dbl_id + "/download?agreementId=" + str(agreement_id)
                page.goto(url)  # Replace with your URL

                # Wait for the download button to appear
                # Inspect the page and adjust the selector to match the button
                page.wait_for_selector("button:has-text('Download')")  

                zip_button = page.query_selector("button:has-text('Download ZIP')")
                if zip_button:

                    # Trigger the download
                    with page.expect_download() as download_info:
                        page.click("button:has-text('Download ZIP')")  # Click the download button
                    download = download_info.value

                    # Save to your folder
                    new_path = Path(self.download_path) / download.suggested_filename
                    download.save_as(os.path.join(self.download_path, download.suggested_filename))
                    print(f"✅ Downloaded ZIP: {new_path}")

                    MinioUSXUpload(self.client, "text", new_path, "bible-dbl-raw", url, translation_id, dbl_id, agreement_id)
                else:
                    print("⚠️ No ZIP button found, assuming audio download instead")
                    # Expand all folders
                    self.expand_all_folders(page)

                    page.wait_for_load_state("networkidle")
                    
                    download_folder_name = f"audio-{dbl_id}-{agreement_id}"

                    file_buttons = page.query_selector_all("button[aria-label^='Download']")

                    for btn in file_buttons:
                        filename = btn.get_attribute("aria-label").replace("Download ", "").strip()

                        book = filename.split(".")[0].split("_")[0]
                        folder_names = ["release", "audio", book]
                        if filename == "metadata.xml":
                            folder_names = []

                        folder_path = os.path.join(Path(self.download_path) / download_folder_name, *folder_names)
                        os.makedirs(folder_path, exist_ok=True)

                        # Trigger download
                        with page.expect_download() as download_info:
                            btn.click()
                        download = download_info.value
                        download.save_as(os.path.join(folder_path, filename))

                        # print(f"✅ Downloaded {filename} → {folder_path}")

                    new_path = Path(self.download_path) / download_folder_name
                    
                    print(f"✅ Downloaded {len(file_buttons)} Audio Files: {new_path}")

                    MinioUSXUpload(self.client, "audio", new_path, "bible-dbl-raw", url, translation_id, dbl_id, agreement_id)

                # break

            browser.close()

if __name__ == "__main__":
    Ingestor()