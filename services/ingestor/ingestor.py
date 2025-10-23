import requests
from bs4 import BeautifulSoup
import psycopg2

from playwright.sync_api import sync_playwright
import os
import time
from minio import Minio
from pathlib import Path

from miniousxupload import MinioUSXUpload

USERNAME = "REDACTED_USERNAME"
PASSWORD = "REDACTED_PASSWORD"

# Folder where you want downloads to go
download_path = "C:/Users/CephJ/Documents/git/bible-insight-server/downloads"
os.makedirs(download_path, exist_ok=True)

# Passes Minio client connection on to the MinioUSXUpload class
client = Minio(
    "localhost:9900",
    access_key="REDACTED_USERNAME",
    secret_key="REDACTED_PASSWORD",
    secure=False
)

conn = psycopg2.connect(
    host="REDACTED_IP",
    port=5444,
    dbname="postgres",
    user="postgres",
    password="REDACTED_PASSWORD"
)

cur = conn.cursor()

cur.execute("""
    SELECT dbl_id, agreement_id FROM bible.DBLInfo;
""")

def expand_all_folders(page):
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

def get_downloads():
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
            page.fill("input[name='email']", USERNAME)
            page.fill("input[name='password']", PASSWORD)
            page.click("button#rememberMe") # Try Remember me for 30 days, to prevent excessive logging and checking

            # Click the login button
            page.click("button:has-text('Sign in')")

            # Wait for navigation after login
            page.wait_for_url("https://app.library.bible/")
            print("✅ Succesful Log In")
        else:
            print("Already logged in")
      
        hi = True # Placeholder, to limit to 1 download

        for dbl_id, agreement_id in cur.fetchall():
            if hi:
                print(dbl_id, agreement_id)
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

                    # Check if there was no download ZIP, so download would equal 0? 

                    # Save to your folder
                    new_path = Path(download_path) / download.suggested_filename
                    download.save_as(os.path.join(download_path, download.suggested_filename))
                    print(f"✅ Downloaded ZIP: {new_path}")

                    MinioUSXUpload(client, "text", new_path, "bible-dbl-raw", url)
                else:
                    print("⚠️ No ZIP button found, assuming audio download instead")
                    # Expand all folders
                    expand_all_folders(page)

                    page.wait_for_load_state("networkidle")
                    
                    download_folder_name = f"audio-{dbl_id}-{agreement_id}"

                    file_buttons = page.query_selector_all("button[aria-label^='Download']")

                    for btn in file_buttons:
                        filename = btn.get_attribute("aria-label").replace("Download ", "").strip()

                        book = filename.split(".")[0].split("_")[0]
                        folder_names = ["release", "audio", book]
                        if filename == "metadata.xml":
                            folder_names = []

                        folder_path = os.path.join(Path(download_path) / download_folder_name, *folder_names)
                        os.makedirs(folder_path, exist_ok=True)

                        # Trigger download
                        with page.expect_download() as download_info:
                            btn.click()
                        download = download_info.value
                        download.save_as(os.path.join(folder_path, filename))

                        # print(f"✅ Downloaded {filename} → {folder_path}")

                    new_path = Path(download_path) / download_folder_name
                    
                    print(f"✅ Downloaded {len(file_buttons)} Audio Files: {new_path}")

                    MinioUSXUpload(client, "audio", new_path, "bible-dbl-raw", url)

                hi = False

        browser.close()

if __name__ == "__main__":
    get_downloads()