import time
import asyncio

from playwright.async_api import async_playwright, Page
import os
import time
from pathlib import Path
import re

from ingestor.usx.translation import Translation
from ingestor.usx.strongsingestor import StrongsIngestor
from manager.managerhandler import ManagerHandler
from ingestor.usx.files.agreements import DBLAgreement

class Ingestor:
    def __init__(
        self,
        manager: ManagerHandler | None = None,
        dbl_id: str | None = None,
        agreement_id: int | None = None,
        all_translations: list | None = None,
    ):
        self.manager = manager or ManagerHandler()
        self.manager.get_obj().set_default_bucket("bible-dbl-raw")

        self.dbl_id = dbl_id
        self.agreement_id = agreement_id
        self.all_translations = all_translations

        self.env = self.manager.get_env()
        self.db = self.manager.get_db()

        self.download_path = Path(__file__).parents[2] / "downloads"
        os.makedirs(self.download_path, exist_ok=True)

    async def run(self):
        start_time = time.time()

        try:
            await self.open_dbl_session()
            self.db.commit()
        finally:
            self.db.close()

        duration = time.time() - start_time
        self._print_duration(duration)

    def _print_duration(self, duration: float):
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration % 1) * 1000)

        formatted = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
        print(f"✅ Completed Ingestor in [{formatted}]!\n")

    # DEPRACATED SINCE EXPANDED BY DEFAULT NOW
    async def expand_all_folders(self, page):
        """
        Expands all collapsible folders on the DBL download page
        so that every nested level (release, audio, ROM, etc.) becomes visible.
        """

        while True:
            # Find all buttons that can expand folders
            expand_buttons = await page.query_selector_all("button[aria-label^='Expand ']")

            if not expand_buttons:
                # No more expandable folders found
                break

            print(f"Found {len(expand_buttons)} folders to expand...")

            for btn in expand_buttons:
                try:
                    label = btn.get_attribute("aria-label")
                    await btn.scroll_into_view_if_needed()
                    await btn.click()
                    time.sleep(0.3)  # small delay for DOM update
                except Exception as e:
                    print(f"⚠️ Failed to expand {label}: {e}")

            # Allow time for the page to render new nested folders
            time.sleep(0.5)

        print("✅ All folders expanded.")

    async def verify_log_in(self, page: Page):
        # Do we need to login?
        if await page.query_selector("input[name='email']"):
            # Fill in the username/email and password
            dbl_credentials = self.env.get_dbl_credentials()
            await page.fill("input[name='email']", dbl_credentials["username"])
            await page.fill("input[name='password']", dbl_credentials["password"])
            await page.click("button#rememberMe") # Try Remember me for 30 days, to prevent excessive logging and checking

            # Click the login button
            await page.click("button:has-text('Sign in')")

            # Wait for navigation after login
            await page.wait_for_url("https://app.library.bible/")
            print("✅ Succesful Log In")
        else:
            print("     Already logged in") # Assumes that we couldn't find email field in link means we are logged in already

    async def open_dbl_session(self):
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False, timeout=999999)  # headless=False shows the browser
            context = await browser.new_context(accept_downloads=True)  # Important to handle downloads

            page = await context.new_page()
        
            # Go to the normal page
            await page.goto("https://app.library.bible/")

            await page.wait_for_load_state("networkidle") # Wait until no network requests for ~500ms (are we being redirected to login?)

            await self.verify_log_in(page)

            translations = None
            if self.all_translations == None:
                # translations = self.db.fetch_all("""SELECT dbl_id, agreement_id FROM bible.DBLInfo WHERE supported = TRUE;""")
                translations = [(self.dbl_id, self.agreement_id)]
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
                
                await self.choose_browse_method(dbl_id, agreement_id, browse_method, page)

                await page.wait_for_load_state("networkidle")

                await self.download_files(page)

            await browser.close()

    async def choose_browse_method(self, dbl_id: str | None, agreement_id: int, method: int, page: Page):
        # Allows choosing what url to go to
        url = None

        match method:
            case 1: # --------------------------- FINAL URL LOCATION FOR DOWNLOAD ---------------------------
                # https://app.library.bible/content/[DBL_ID]/download?agreementId=[AGREEMENT_ID]
                url = "https://app.library.bible/content/" + dbl_id + "/download?agreementId=" + str(agreement_id)
                await page.goto(url, wait_until="domcontentloaded")  # Replace with your URL

            case 2: # --------------------------- DIRECTS TO METHOD 1 (USING ONLY AGREEMENT) ---------------------------
                # https://app.library.bible/agreements/[AGREEMENT_ID]
                url = "https://app.library.bible/agreements/" + str(agreement_id)
                await page.goto(url, wait_until="domcontentloaded")  # Replace with your URL

                await page.wait_for_selector("button:has-text('Access Files')")  
                await page.click("button:has-text('Access Files')")
                await page.wait_for_url(wait_until="domcontentloaded")

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
    
    async def get_licence_code(self, page: Page):
        # Applicable to CC based licences and Public Domain
        licence_text = await page.locator(
            "p:has-text('available to the public') strong"
        ).inner_text()

        return self.parse_licence(licence_text)    

    def parse_licence(self, text: str) -> str | None:
        ALLOWED_CC_LICENCES = {
            "CC BY",
            "CC BY-SA",
            "CC BY-ND",
            "CC BY-NC",
            "CC BY-NC-SA",
            "CC BY-NC-ND",
        }
        # Rule 1: explicit Public Domain
        if "Public Domain" in text:
            return "PUBLIC_DOMAIN"

        # Rule 2: extract bracketed licence code
        match = re.search(r"\[(.*?)\]", text)
        if not match:
            return None
            # raise AssertionError(f"No licence code found: {text}")

        code = match.group(1).strip()

        if code not in ALLOWED_CC_LICENCES:
            return None
            # raise AssertionError(f"Unknown Creative Commons licence: {code}")

        return f"{code} 4.0"

    async def download_files(self, page: Page):
        # Wait for the download button to appear
        # Inspect the page and adjust the selector to match the button
        await page.wait_for_selector("button:has-text('Download All')")  

        new_path = None

        dbl_id, agreement_id, source_url = self.read_translation_from_url(page)

        # Initialise logfile
        self.translation_title = f"{self.dbl_id}-{self.agreement_id}"

        self.log = self.manager.create_log_in_folder(["logs", "ingestor"], f"{self.translation_title}")
        self.log.set_logging_level(2)

        licence_code = await self.get_licence_code(page)
        agreement = DBLAgreement(self.manager, agreement_id, licence_code, self.log)
        if agreement.get_valid() == False:
            self.log.log_to_file(f"Ingestion Cancelled due to invalid Agreement!", "INGESTOR", "INFO")
            return

        zip_button = await page.query_selector("button:has-text('Download All')")
        if zip_button:

            # Trigger the download
            async with page.expect_download() as download_info:
                await page.click("button:has-text('Download All')")  # Click the download button
            download = await download_info.value

            # Save to your folder
            new_path = Path(self.download_path) / download.suggested_filename
            await download.save_as(os.path.join(self.download_path, download.suggested_filename))
            print(f"✅ Downloaded ZIP: {new_path}")

            Translation(self.manager, "text", new_path, source_url, dbl_id, agreement, self.log)
        else:
            print("⚠️ No ZIP button found, assuming audio download instead")
            # Expand all folders
            # self.expand_all_folders(page)

            await page.wait_for_load_state("networkidle")
            
            download_folder_name = f"audio-{dbl_id}"

            file_buttons = await page.query_selector_all("button[aria-label^='Download']")

            for btn in file_buttons:
                filename = await btn.get_attribute("aria-label").replace("Download ", "").strip()

                book = filename.split(".")[0].split("_")[0]
                folder_names = ["release", "audio", book]
                if filename == "metadata.xml":
                    folder_names = []

                folder_path = os.path.join(Path(self.download_path) / download_folder_name, *folder_names)
                os.makedirs(folder_path, exist_ok=True)

                # Trigger download
                async with page.expect_download() as download_info:
                    await btn.click()
                download = await download_info.value
                await download.save_as(os.path.join(folder_path, filename))

            new_path = Path(self.download_path) / download_folder_name
            
            print(f"✅ Downloaded {len(file_buttons)} Audio Files: {new_path}")

            Translation(self.manager, "audio", new_path, source_url, dbl_id, agreement, self.log)

async def main(
        dbl_id: str | None,
        agreement_id: int
    ):
    await Ingestor(
        dbl_id=dbl_id,
        agreement_id=agreement_id
    ).run()

if __name__ == "__main__":
    # Can be set up to run all supported translations
    asyncio.run(main(
        dbl_id="7142879509583d59",
        agreement_id="240016"
    ))
    # Ingestor(dbl_id="65eec8e0b60e656b", agreement_id="246069")
