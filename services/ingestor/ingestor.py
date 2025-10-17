import requests
from bs4 import BeautifulSoup
import psycopg2

from playwright.sync_api import sync_playwright
import os
import time

USERNAME = "REDACTED_USERNAME"
PASSWORD = "REDACTED_PASSWORD"

# Folder where you want downloads to go
download_path = "C:/Users/CephJ/Documents/git/bible-insight-server/downloads"
os.makedirs(download_path, exist_ok=True)

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
        else:
            print("Already logged in")
      
        hi = True # Placeholder, to limit to 1 download

        for dbl_id, agreement_id in cur.fetchall():
            if hi:
                print(dbl_id, agreement_id)

                # Go to the DBL translation page
                url = "https://app.library.bible/content/" + dbl_id + "/download?agreementId=" + str(agreement_id)
                page.goto(url)  # Replace with your URL

                # Wait for the download button to appear
                # Inspect the page and adjust the selector to match the button
                page.wait_for_selector("button:has-text('Download')")  

                # Trigger the download
                with page.expect_download() as download_info:
                    page.click("button:has-text('Download ZIP')")  # Click the download button
                download = download_info.value

                # Save to your folder
                download.save_as(os.path.join(download_path, download.suggested_filename))
                print(f"Downloaded {download.suggested_filename} to {download_path}")

                hi = False

        browser.close()

if __name__ == "__main__":
    get_downloads()