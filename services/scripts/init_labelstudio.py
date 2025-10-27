from label_studio_sdk import Client, LabelStudio
import os
from pathlib import Path
import subprocess
import json
import ast
import time

from playwright.sync_api import sync_playwright

from dotenv import load_dotenv

ENV_FILE_PATH = ""

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
        ENV_FILE_PATH = parent / ".env"
        break

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL")
LABEL_STUDIO_USERNAME = os.getenv("LABEL_STUDIO_USERNAME")
LABEL_STUDIO_PASSWORD = os.getenv("LABEL_STUDIO_PASSWORD")
LABEL_STUDIO_EMAIL = os.getenv("LABEL_STUDIO_EMAIL")
LABEL_STUDIO_API_TOKEN = os.getenv("LABEL_STUDIO_API_TOKEN")

CONTAINER_NAME = "label-studio-app-1"  # Adjust if your container name differs

def create_legacy_token():
    # Get the user info and token
    result = subprocess.run([
        "docker", "exec", CONTAINER_NAME,
        "label-studio", "user",
        "--username", LABEL_STUDIO_USERNAME
    ], capture_output=True, text=True, check=True)

    # print("\nRaw output:\n", result.stdout)

    ## LOOKS LIKE WILL HAVE TO IMPLEMENT THIS THROUGH APP WRIGHT AFTER ALL, WITH SLIGHT DELAY UNTIL ITS LOADED, 
    #           THEN SIGN IN AND CREATE ASSOCIATED ACTIONS UNTIL API KEY AVAILABLE

    # Remove the header line if present
    lines = result.stdout.strip().splitlines()
    if lines[0].startswith("=> User info"):
        # join all remaining lines into one string
        result_str = "\n".join(lines[1:]).strip()
    else:
        result_str = result.stdout.strip()

    try:
        # Try parsing as a Python literal dict
        user_info = ast.literal_eval(result_str)
        token = user_info.get("token")
        print("\nUser Token:", token)
        return token
    except Exception as e:
        print("⚠️ Failed to parse output:", e)
        print("Output was:\n", result_str)
        return None

    # => User info:
    # {
    #     'id': 1, 
    #     'first_name': 'User', 
    #     'last_name': 'Somebody', 
    #     'username': 'label-studio', 
    #     'email': 'example@labelstud.io', 
    #     'last_activity': '2021-06-15T19:37:29.594618Z', 
    #     'avatar': '/data/avatars/img.jpg', 
    #     'initials': 'el', 
    #     'phone': '', 
    #     'active_organization': 1, 
    #     'token': '<api_token>', 
    #     'status': 'ok'
    # }

def find_api_token():
    # On first time start up / log in for user, can generate a personal API key for them, by browsing the web page
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # headless=False shows the browser
        context = browser.new_context(accept_downloads=True)  # Important to handle downloads

        page = context.new_page()

        # time.sleep(15)
    
        # Go to the normal page
        page.goto(LABEL_STUDIO_URL)

        # Do we need to login?
        if page.query_selector("input[name='email']"):
            # Fill in the username/email and password
            page.fill("input[name='email']", LABEL_STUDIO_USERNAME)
            page.fill("input[name='password']", LABEL_STUDIO_PASSWORD)

            # Click the login button
            page.click("button:has-text('Log in')")

        page.click("span:has-text('CE')")
        page.click("span:has-text('Account & Settings')")
        page.click("span:has-text('Personal Access Token')")

        API_TOKEN = refresh_api_token(page)
        while API_TOKEN == None:
            API_TOKEN = refresh_api_token(page)

        return API_TOKEN
    
def refresh_api_token(page):
    button = page.locator("button:has(span:has-text('Create New Token'))")
    if button and button.is_disabled():
        page.click("span:has-text('Revoke')")
        revoke_confirm_button = page.locator("button:has(span:has-text('Revoke'))").nth(1)
        revoke_confirm_button.click()
        time.sleep(1)
        page.click("button:has(span:has-text('Create New Token'))")
        print("Revoked and regenerated API Token")
    else:
        page.click("button:has(span:has-text('Create New Token'))")

    time.sleep(1) # prevent reading empty token
    
    API_TOKEN = None
    try:    
        API_TOKEN = page.input_value("input.lsf-input-ls.w-full") # The API Token
    except Exception as e:
        pass

    if API_TOKEN == "":
        API_TOKEN = None

    return API_TOKEN

def update_env_file(new_token, env_var):
    """Replace old token line with new one in the .env file."""
    if not ENV_FILE_PATH:
        print("❌ .env file not found")
        return

    lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as f:
            for line in f:
                # Keep everything except old token lines
                if not line.strip().startswith(f"{env_var}="):
                    lines.append(line.rstrip("\n"))

    # Add new token line
    lines.append(f'{env_var}="{new_token}"')

    # Write back the cleaned file
    with open(ENV_FILE_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✅ {env_var} updated in {ENV_FILE_PATH}")

    return new_token

def generate_token():
    if not LABEL_STUDIO_API_TOKEN:
        LABEL_STUDIO_API_TOKEN = find_api_token()
        if LABEL_STUDIO_API_TOKEN:
            update_env_file(LABEL_STUDIO_API_TOKEN, "LABEL_STUDIO_API_TOKEN")
        else:
            print("❌ No token extracted — nothing written.")
    else: 
        print("✅ Token Already exists!")

if __name__ == "__main__":
    MAX_RETRIES = 3
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_TOKEN)
            me = client.users.whoami()
            print(f"✅ Connected to [Label Studio] successfully on try {attempt+1}!")
            break  # success
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            attempt += 1

            # Regenerate token only after the first failure
            LABEL_STUDIO_API_TOKEN = generate_token()

            if attempt == MAX_RETRIES:
                print("❌ All retries failed. Exiting.")
                raise
    