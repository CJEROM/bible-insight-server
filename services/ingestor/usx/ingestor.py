import time

from playwright.sync_api import sync_playwright, Page
import os
import time
from pathlib import Path

from ingestor.usx.translation import Translation
from ingestor.usx.strongsingestor import StrongsIngestor
from manager.managerhandler import ManagerHandler
from ingestor.usx.files.agreements import DBLAgreement

class Ingestor:
    def __init__(self, manager: ManagerHandler = None, dbl_id = None, agreement_id = None, all_translations: list = None):
        self.manager = manager
        if manager == None:
            self.manager = ManagerHandler()
            self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        # StrongsIngestor(self.manager)

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

        self.open_dbl_session()

        self.db.commit()
        self.db.close()

        duration = time.time() - self.start_time
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration % 1) * 1000)  # or *100 for .mm format

        formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

        print(f"✅ Completed Ingestor in [{formatted_duration}]!\n")

    # DEPRACATED SINCE EXPANDED BY DEFAULT NOW
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

    def verify_log_in(self, page: Page):
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

    def open_dbl_session(self):
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False, timeout=999999)  # headless=False shows the browser
            context = browser.new_context(accept_downloads=True)  # Important to handle downloads

            page = context.new_page()
        
            # Go to the normal page
            page.goto("https://app.library.bible/")

            page.wait_for_load_state("networkidle") # Wait until no network requests for ~500ms (are we being redirected to login?)

            self.verify_log_in(page)

            translations = None
            if self.all_translations == None:
                # translations = self.db.fetch_all("""SELECT dbl_id, agreement_id FROM bible.DBLInfo WHERE supported = TRUE;""")
                translations = [self.dbl_id, self.agreement_id]
            else:
                translations = self.all_translations

            for i, (dbl_id, agreement_id) in enumerate(translations):
                print(f"\n\n✅ Starting Translation {dbl_id}-{agreement_id} Processing!")

                if self.agreement_id != None:
                    if i == 0:
                        dbl_id = self.dbl_id
                        agreement_id = self.agreement_id
                    else:
                        break
                
                browse_method = 0
                if dbl_id == None:
                    browse_method = 2
                else:
                    browse_method = 1

                # Go to the DBL translation page
                
                self.choose_browse_method(dbl_id, agreement_id, browse_method, page)

                page.wait_for_load_state("networkidle")

                self.download_files(dbl_id, agreement_id, page)

            browser.close()

    def choose_browse_method(dbl_id: str | None, agreement_id: int, method: int, page: Page):
        # Allows choosing what url to go to
        url = None

        match method:
            case 1: # --------------------------- FINAL URL LOCATION FOR DOWNLOAD ---------------------------
                # https://app.library.bible/content/[DBL_ID]/download?agreementId=[AGREEMENT_ID]
                url = "https://app.library.bible/content/" + dbl_id + "/download?agreementId=" + str(agreement_id)
                page.goto(url, wait_until="domcontentloaded")  # Replace with your URL

            case 2: # --------------------------- DIRECTS TO METHOD 1 (USING ONLY AGREEMENT) ---------------------------
                # https://app.library.bible/agreements/[AGREEMENT_ID]
                url = "https://app.library.bible/agreements/" + str(agreement_id)
                page.goto(url, wait_until="domcontentloaded")  # Replace with your URL

                page.wait_for_selector("button:has-text('Access Files')")  
                page.click("button:has-text('Access Files')")
                page.wait_for_url(wait_until="domcontentloaded")

            # ------------------------------------------ OTHER METHODS ------------------------------------------
            # NOTE: These aren't reliable for our use case to download files currently, but they do exist, and might have future uses
            case 3:
                # https://app.library.bible/agreements/[AGREEMENT_ID]/history
                url = "https://app.library.bible/agreements/" + str(agreement_id) + "/history"
                
            case 4:
                # https://app.library.bible/content/[DBL_ID]/summary
                url = "https://app.library.bible/content/" + dbl_id + "/summary"
                
            case 5:
                # https://app.library.bible/content/[DBL_ID]/revisions
                url = "https://app.library.bible/content/" + dbl_id + "/revisions"
                
            case 6:
                # https://app.library.bible/content/[DBL_ID]/revisions/[AGREEMENT_ID]/summary
                url = "https://app.library.bible/content/" + dbl_id + "/revisions/" + str(agreement_id) + "/summary"
                
            case 7:
                # https://app.library.bible/content/[DBL_ID]/revisions/[AGREEMENT_ID]/files
                url = "https://app.library.bible/content/" + dbl_id + "/revisions/" + str(agreement_id) + "/files"

    def read_translation_from_url(self, page: Page) -> tuple[str, int]:
        # Fails if DBL changes the URL structure
        url = page.url
        parts = url.split("/")

        assert parts[3] == "content", f"Unexpected URL structure: {url}"
        assert parts[5].startswith("download"), f"Unexpected URL structure: {url}"

        dbl_id = parts[4]

        query = parts[5]
        assert "agreementId=" in query, f"Missing agreementId in URL: {url}"

        agreement_id = int(query.split("agreementId=")[1])

        return (dbl_id, agreement_id, url)
    
    def get_licence_code(self, page: Page):
        # Applicable to CC based licences and Public Domain
        pass

    def download_files(self, page: Page):
        # Wait for the download button to appear
        # Inspect the page and adjust the selector to match the button
        page.wait_for_selector("button:has-text('Download All')")  

        new_path = None

        dbl_id, agreement_id, source_url = self.read_translation_from_url(page)

        agreement = DBLAgreement(agreement_id, self.get_licence_code(page))

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

            Translation(self.manager, "text", new_path, source_url, dbl_id, agreement)
        else:
            print("⚠️ No ZIP button found, assuming audio download instead")
            # Expand all folders
            # self.expand_all_folders(page)

            page.wait_for_load_state("networkidle")
            
            download_folder_name = f"audio-{dbl_id}"

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

            Translation(self.manager, "audio", new_path, source_url, dbl_id, agreement)

if __name__ == "__main__":
    # Can be set up to run all supported translations
    Ingestor(dbl_id="7142879509583d59", agreement_id="240016")
    # Ingestor(dbl_id="65eec8e0b60e656b", agreement_id="246069")
