from label_studio_sdk import Client, LabelStudio
import os
from pathlib import Path
import subprocess
import json

from dotenv import load_dotenv

# Automatically find the project root (folder containing .env)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / ".env").exists():
        load_dotenv(parent / ".env")
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

    print("\nRaw output:\n", result.stdout)

    # Try to extract token if the output is in JSON format
    try:
        user_info = json.loads(result.stdout)
        print("\nUser Token:", user_info.get("token"))
        return user_info.get("token")
    except json.JSONDecodeError:
        # Fallback: simple string search
        for line in result.stdout.splitlines():
            if "'token':" in line or '"token":' in line:
                print("\nExtracted Token Line:", line)
                return line
                break
            
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

