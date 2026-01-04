import time

from playwright.sync_api import sync_playwright
import os
import time
from pathlib import Path

from usxingestor.translation import Translation
from usxingestor.strongsingestor import StrongsIngestor
from manager.managerhandler import ManagerHandler

class Ingestor:
    def __init__(self, manager: ManagerHandler = None, dbl_id = None, agreement_id = None, all_translations: list = None):
        self.manager = manager
        if manager == None:
            self.manager = ManagerHandler()
            self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        StrongsIngestor(self.manager)

        self.dbl_id = dbl_id
        self.agreement_id = agreement_id
        self.all_translations = all_translations

        self.env = self.manager.get_env()
        self.db = self.manager.get_db()

        # Worth adding option, that if dbl_id and agreement_id have been passed in, run just the class for that translation
        #       This would be useful when enforcing foreign key constraints with translation relationships

        self.start_time = time.time()

        # Folder where you want downloads to go
        self.download_path = Path(__file__).parents[2] / "downloads"
        os.makedirs(self.download_path, exist_ok=True)

        self.get_downloads()

        self.db.commit()
        self.db.close()

        duration = time.time() - self.start_time
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration % 1) * 1000)  # or *100 for .mm format

        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

        print(f"✅ Completed Ingestor in [{formatted_duration}]!\n")

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
        translation_id = self.db.fetch_one("""
            SELECT id FROM bible.translations WHERE dbl_id = %s AND agreement_id = %s;
        """, (dbl_id, agreement_id))

        # If the translation already exists, then quit processing this translation
        if translation_id != None:
            return -1
        
        # If not create a new translation entry and add to supported translations      
        self.db.execute("""
            INSERT INTO bible.dblinfo (dbl_id, agreement_id, supported) VALUES (%s, %s, TRUE)
            ON CONFLICT (dbl_id, agreement_id) DO NOTHING;
        """, (dbl_id,agreement_id))

        return self.db.fetch_clean_one("""
            INSERT INTO bible.translations (dbl_id, agreement_id) VALUES (%s, %s) RETURNING id;
        """, (dbl_id, agreement_id))

    def get_downloads(self):
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False, timeout=999999)  # headless=False shows the browser
            context = browser.new_context(accept_downloads=True)  # Important to handle downloads

            page = context.new_page()
        
            # Go to the normal page
            page.goto("https://app.library.bible/")

            page.wait_for_load_state("networkidle") # Wait until no network requests for ~500ms (are we being redirected to login?)

            # Do we need to login?
            if page.query_selector("input[name='email']"):
                # Fill in the username/email and password
                dbl_credentials = self.env.get_dbl_credentials()
                page.fill("input[name='email']", dbl_credentials["username"])
                page.fill("input[name='password']", dbl_credentials["password"])
                page.click("button#rememberMe") # Try Remember me for 30 days, to prevent excessive logging and checking

                # Click the login button
                page.click("button:has-text('Sign in')")

                # Wait for navigation after login
                page.wait_for_url("https://app.library.bible/")
                print("✅ Succesful Log In")
            else:
                print("     Already logged in") # Assumes that we couldn't find email field in link means we are logged in already

            translations = None
            if self.all_translations == None:
                translations = self.db.fetch_all("""SELECT dbl_id, agreement_id FROM bible.DBLInfo WHERE supported = TRUE;""")
            else:
                translations = self.all_translations

            for i, (dbl_id, agreement_id) in enumerate(translations):
                if self.dbl_id != None and self.agreement_id != None:
                    if i == 0:
                        dbl_id = self.dbl_id
                        agreement_id = self.agreement_id
                    else:
                        break

                translation_id = self.get_translation(dbl_id, agreement_id)
                if translation_id == -1:
                    print(f"❌ Translation {dbl_id}-{agreement_id} already exists! Skipping ...")
                    continue # Skip because its already in our system

                print(f"\n\n✅ Starting Translation {dbl_id}-{agreement_id} Processing!")

                new_path = None

                # Go to the DBL translation page
                url = "https://app.library.bible/content/" + dbl_id + "/download?agreementId=" + str(agreement_id)
                page.goto(url, wait_until="domcontentloaded")  # Replace with your URL

                page.wait_for_load_state("networkidle")

                # Wait for the download button to appear
                # Inspect the page and adjust the selector to match the button
                page.wait_for_selector("button:has-text('Download All')")  

                zip_button = page.query_selector("button:has-text('Download All')")
                if zip_button:

                    # Trigger the download
                    with page.expect_download() as download_info:
                        page.click("button:has-text('Download All')")  # Click the download button
                    download = download_info.value

                    # Save to your folder
                    new_path = Path(self.download_path) / download.suggested_filename
                    download.save_as(os.path.join(self.download_path, download.suggested_filename))
                    print(f"✅ Downloaded ZIP: {new_path}")

                    Translation(self.manager, "text", new_path, url, translation_id, dbl_id, agreement_id)
                else:
                    print("⚠️ No ZIP button found, assuming audio download instead")
                    # Expand all folders
                    # self.expand_all_folders(page)

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

                    new_path = Path(self.download_path) / download_folder_name
                    
                    print(f"✅ Downloaded {len(file_buttons)} Audio Files: {new_path}")

                    Translation(self.manager, "audio", new_path, url, translation_id, dbl_id, agreement_id)

            browser.close()

if __name__ == "__main__":
    # Ingestor()
    Ingestor(dbl_id="7142879509583d59", agreement_id="240016")
    # Ingestor(dbl_id="65eec8e0b60e656b", agreement_id="246069")
