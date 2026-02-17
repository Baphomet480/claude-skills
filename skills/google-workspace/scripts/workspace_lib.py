"""
Shared library for Google Workspace skills.
Handles robust authentication, token management, and common utilities.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, List, Optional, Set, Union

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

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

def print_json(data: Any) -> None:
    """Print data as JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))

def find_credentials_dir(
    env_var: Optional[str] = None,
    legacy_dir_name: Optional[str] = None
) -> Path:
    """
    Locate the credentials directory.
    Priority:
    1. Environment variable (e.g. GMAIL_CREDENTIALS_DIR)
    2. Unified workspace directory (~/.google_workspace) if token exists
    3. Legacy directory (~/.gmail_credentials) if token exists
    4. Default to unified workspace directory
    """
    if env_var and os.environ.get(env_var):
        return Path(os.environ[env_var])

    workspace = Path(os.environ.get("GOOGLE_WORKSPACE_DIR", Path.home() / ".google_workspace"))
    if (workspace / "token.json").exists():
        return workspace

    if legacy_dir_name:
        legacy = Path.home() / legacy_dir_name
        if (legacy / "token.json").exists():
            return legacy

    return workspace

def authenticate(
    scopes: Union[List[str], Set[str]],
    token_file: Path,
    client_secrets_file: Optional[Path] = None,
    service_name: str = "Service"
) -> Optional[Credentials]:
    """
    Authenticate with robust fallback and scope checking.
    
    Flow:
    1. Load local token (if exists).
    2. Verify scopes. If mismatch, warn and discard.
    3. Refresh if expired. Save to disk.
    4. If local failed/missing, try ADC (Application Default Credentials).
    
    Returns:
        Credentials object if successful, None otherwise.
    """
    creds = None
    required_scopes = set(scopes)

    # 1. Try Local Token
    if token_file.exists():
        try:
            # Load without scopes first to verify permissions
            creds = Credentials.from_authorized_user_file(str(token_file))
            
            if creds:
                granted_scopes = set(creds.scopes or [])
                if not required_scopes.issubset(granted_scopes):
                    print(f"⚠️  Warning: Token in {token_file} lacks required scopes.", file=sys.stderr)
                    print(f"    Have: {granted_scopes}", file=sys.stderr)
                    print(f"    Need: {required_scopes}", file=sys.stderr)
                    print("    Ignoring local token. Run 'setup' to refresh permissions.", file=sys.stderr)
                    return None
            
            # Refresh if expired
            if creds and creds.expired and getattr(creds, "refresh_token", None):
                try:
                    creds.refresh(Request())
                    # Save refreshed token
                    token_file.parent.mkdir(parents=True, exist_ok=True)
                    token_file.write_text(creds.to_json())
                except Exception as e:
                    print(f"⚠️  Token refresh failed: {e}", file=sys.stderr)
                    print("    Please re-run setup to generate a new token.", file=sys.stderr)
                    return None

            return creds

        except Exception as e:
            print(f"⚠️  Error loading local token: {e}", file=sys.stderr)
            return None

    # 2. Try ADC (Only if local token does not exist)
    if not creds or not creds.valid:
        try:
            creds, _ = google.auth.default(scopes=list(required_scopes))
            if creds and creds.expired and getattr(creds, "refresh_token", None):
                creds.refresh(Request())
        except Exception:
            creds = None

    # 3. Fallback / Manual Setup Hint
    if not creds or not creds.valid:
        # If we have a client secrets file but no valid token, the user likely needs to run setup
        if client_secrets_file and client_secrets_file.exists() and not token_file.exists():
            # This is a passive check, we don't trigger interactive flow here
            pass

    return creds
