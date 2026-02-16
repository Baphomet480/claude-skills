#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Workspace Master Setup
Authenticates ONCE for Gmail, Calendar, Contacts, Drive, and Photos.

Usage:
  uv run ~/.agents/skills/gmail/scripts/setup_workspace.py
"""

import shutil
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

# --- Configuration ---

# The superset of scopes for all skills
ALL_SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/photoslibrary",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
    "https://www.googleapis.com/auth/cloud-platform",
]

# Paths for each skill
SKILL_DIRS = {
    "gmail": Path.home() / ".gmail_credentials",
    "calendar": Path.home() / ".calendar_credentials",
    "contacts": Path.home() / ".contacts_credentials",
    "drive": Path.home() / ".drive_credentials",
    "photos": Path.home() / ".photos_credentials",
}

# Possible locations for the source credentials.json
POSSIBLE_CRED_FILES = [
    Path.home() / ".gemini/credentials/google_client_secret.json",
    Path.home() / "Downloads/credentials.json",
    Path.cwd() / "credentials.json",
    SKILL_DIRS["gmail"] / "credentials.json",
]


def find_credentials():
    for path in POSSIBLE_CRED_FILES:
        if path.exists():
            return path
    return None


def main():
    print()
    print("Google Workspace Master Setup")
    print("(Gmail + Calendar + Contacts + Drive + Photos)")
    print()

    # 1. Find Client Secrets
    creds_file = find_credentials()
    if not creds_file:
        print("Error: 'credentials.json' not found.")
        print()
        print("To fix this:")
        print("1. Go to Google Cloud Console > APIs & Services > Credentials")
        print("2. Create 'OAuth 2.0 Client IDs' (Desktop app)")
        print("3. Download the JSON file")
        print(f"4. Save it to: {POSSIBLE_CRED_FILES[0]}")
        sys.exit(1)

    print(f"Using credentials from: {creds_file}")

    # 2. Authenticate
    print()
    print("Requesting access...")
    print("A browser window will open. Please log in and grant all requested permissions.")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), ALL_SCOPES)
        creds = flow.run_local_server(port=0)
        token_json = creds.to_json()
        print()
        print("Authentication successful.")
    except Exception as e:
        print()
        print(f"Authentication failed: {e}")
        return

    # 3. Distribute
    print()
    print("Configuring skills...")

    for skill, directory in SKILL_DIRS.items():
        directory.mkdir(parents=True, exist_ok=True)

        # Write Token
        (directory / "token.json").write_text(token_json)

        # Ensure credentials exist there too
        dest_creds = directory / "credentials.json"
        if not dest_creds.exists():
            shutil.copy(creds_file, dest_creds)

        print(f"  - {skill.capitalize()}: Ready")

    print()
    print("All Google skills are now ready to use.")

if __name__ == "__main__":
    main()
