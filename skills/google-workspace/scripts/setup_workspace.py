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
  uv run scripts/setup_workspace.py
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
    # Photos: old photoslibrary/photoslibrary.readonly scopes were killed March 2025.
    # These surviving scopes only cover app-uploaded content.
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
    "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata",
    # Picker API scope — for interactive selection from full library
    "https://www.googleapis.com/auth/photospicker.mediaitems.readonly",
    "https://www.googleapis.com/auth/cloud-platform",
]

# Primary unified directory
WORKSPACE_DIR = Path.home() / ".google_workspace"

# Legacy per-service directories (for backward compat distribution)
LEGACY_DIRS = {
    "gmail": Path.home() / ".gmail_credentials",
    "calendar": Path.home() / ".calendar_credentials",
    "contacts": Path.home() / ".contacts_credentials",
    "drive": Path.home() / ".drive_credentials",
    "photos": Path.home() / ".photos_credentials",
}

# Possible locations for the source credentials.json
POSSIBLE_CRED_FILES = [
    WORKSPACE_DIR / "credentials.json",
    Path.home() / ".gemini/credentials/google_client_secret.json",
    Path.home() / "Downloads/credentials.json",
    Path.cwd() / "credentials.json",
    LEGACY_DIRS["gmail"] / "credentials.json",
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
        print(f"4. Save it to: {WORKSPACE_DIR / 'credentials.json'}")
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

    # 3. Write to unified workspace directory
    print()
    print("Configuring unified workspace directory...")
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    (WORKSPACE_DIR / "token.json").write_text(token_json)

    # Ensure credentials.json exists in workspace dir
    workspace_creds = WORKSPACE_DIR / "credentials.json"
    if not workspace_creds.exists():
        shutil.copy(creds_file, workspace_creds)

    print(f"  Token saved to: {WORKSPACE_DIR / 'token.json'}")

    # 4. Distribute to legacy directories (backward compat)
    print()
    print("Distributing to legacy directories (backward compat)...")

    for skill, directory in LEGACY_DIRS.items():
        directory.mkdir(parents=True, exist_ok=True)

        # Write Token
        (directory / "token.json").write_text(token_json)

        # Ensure credentials exist there too
        dest_creds = directory / "credentials.json"
        if not dest_creds.exists():
            shutil.copy(creds_file, dest_creds)

        print(f"  - {skill.capitalize()}: Ready")

    print()
    print("All Google Workspace services are now ready to use.")
    print(f"Primary credentials: {WORKSPACE_DIR}")

if __name__ == "__main__":
    main()
