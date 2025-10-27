from label_studio_sdk import Client, LabelStudio
import os
from pathlib import Path
import subprocess
import json
import ast

from dotenv import load_dotenv

ENV_FILE_PATH = ""

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
        ENV_FILE_PATH = parent / ".env"
        break

LABEL_STUDIO_USERNAME = os.getenv("LABEL_STUDIO_USERNAME")
LABEL_STUDIO_PASSWORD = os.getenv("LABEL_STUDIO_PASSWORD")
LABEL_STUDIO_EMAIL = os.getenv("LABEL_STUDIO_EMAIL")

CONTAINER_NAME = "label-studio-app-1"  # Adjust if your container name differs

def create_api_token():
    # Get the user info and token
    result = subprocess.run([
        "docker", "exec", CONTAINER_NAME,
        "label-studio", "user",
        "--username", LABEL_STUDIO_USERNAME
    ], capture_output=True, text=True, check=True)

    # print("\nRaw output:\n", result.stdout)

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

def update_env_file(new_token):
    """Replace old token line with new one in the .env file."""
    if not ENV_FILE_PATH:
        print("❌ .env file not found")
        return

    lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as f:
            for line in f:
                # Keep everything except old token lines
                if not line.strip().startswith("LABEL_STUDIO_TOKEN="):
                    lines.append(line.rstrip("\n"))

    # Add new token line
    lines.append(f'LABEL_STUDIO_TOKEN="{new_token}"')

    # Write back the cleaned file
    with open(ENV_FILE_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✅ LABEL_STUDIO_TOKEN updated in {ENV_FILE_PATH}")

if __name__ == "__main__":
    token = create_api_token()
    if token:
        update_env_file(token)
    else:
        print("❌ No token extracted — nothing written.")

    label_studio_client = LabelStudio(
        api_key=token,
    )
    label_studio_client.projects.create()