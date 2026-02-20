#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Workspace Token Maintainer.
Refreshes the access token on disk to keep it valid, preventing
latency or expiration errors during CLI usage.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

# Add script directory to path to import workspace_lib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import workspace_lib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def main():
    creds_dir = workspace_lib.find_credentials_dir()
    token_file = creds_dir / "token.json"

    if not token_file.exists():
        print(f"No token found at {token_file}. Skipping maintenance.")
        return

    try:
        # Load without verifying scopes (we just want to refresh what's there)
        creds = Credentials.from_authorized_user_file(str(token_file))
        
        # Force refresh regardless of expiry time to ensure freshness
        if getattr(creds, "refresh_token", None):
            print(f"Refreshing token at {token_file}...")
            creds.refresh(Request())
            
            # Save
            token_file.write_text(creds.to_json())
            print(f"Success. Token refreshed at {datetime.now()}.")
        else:
            print("Token has no refresh token. Cannot maintain.")
            try:
                subprocess.run(["notify-send", "Google Workspace Auth Expired", "Please re-authenticate your Google Workspace AI Skill."], check=False)
                subprocess.run(["osascript", "-e", 'display notification "Please re-authenticate your Google Workspace AI Skill." with title "Google Workspace Auth Expired"'], check=False)
            except Exception:
                pass
            sys.exit(1)

    except Exception as e:
        print(f"Error refreshing token: {e}", file=sys.stderr)
        try:
            subprocess.run(["notify-send", "Google Workspace Auth Error", f"Failed to refresh token: {e}"], check=False)
            subprocess.run(["osascript", "-e", f'display notification "Failed to refresh token: {e}" with title "Google Workspace Auth Error"'], check=False)
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
