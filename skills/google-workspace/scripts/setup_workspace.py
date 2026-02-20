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

import workspace_lib

# --- Configuration ---


# Possible locations for the source credentials.json
POSSIBLE_CRED_FILES = [
    workspace_lib.WORKSPACE_DIR / "credentials.json",
    Path.home() / ".gemini/credentials/google_client_secret.json",
    Path.home() / "Downloads/credentials.json",
    Path.cwd() / "credentials.json",
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
        print(f"4. Save it to: {workspace_lib.WORKSPACE_DIR / 'credentials.json'}")
        sys.exit(1)

    print(f"Using credentials from: {creds_file}")

    # 2. Authenticate
    print()
    print("Requesting access...")
    print("A browser window will open. Please log in and grant all requested permissions.")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), workspace_lib.ALL_SCOPES)
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
    workspace_lib.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    (workspace_lib.WORKSPACE_DIR / "token.json").write_text(token_json)

    # Ensure credentials.json exists in workspace dir
    workspace_creds = workspace_lib.WORKSPACE_DIR / "credentials.json"
    if not workspace_creds.exists():
        shutil.copy(creds_file, workspace_creds)

    print(f"  Token saved to: {workspace_lib.WORKSPACE_DIR / 'token.json'}")

    print()
    print("All Google Workspace services are now ready to use.")
    print(f"Credentials: {workspace_lib.WORKSPACE_DIR}")

if __name__ == "__main__":
    main()
