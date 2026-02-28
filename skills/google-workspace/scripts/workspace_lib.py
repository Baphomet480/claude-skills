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

LOG_DIR = WORKSPACE_DIR / "logs"


def report_crash(script_name: str, exc: Exception) -> None:
    """Log an unhandled exception to disk and emit an Agent Directive to stdout.

    Call this inside the outermost except block of a script's main().
    It writes the full traceback to ~/.google_workspace/logs/error.log and
    prints structured JSON that agents can parse and act on.
    """
    import traceback
    import time

    err_msg = str(exc) or repr(exc)
    tb = traceback.format_exc()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "error.log"

    with open(log_file, "a") as f:
        f.write(
            f"--- UNHANDLED EXCEPTION [{script_name}] ---\n"
            f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
            f"Command: {' '.join(sys.argv)}\n"
            f"{tb}\n"
        )

    print_json({
        "status": "error",
        "type": "UnhandledException",
        "message": err_msg,
        "fix": (
            f"AGENT DIRECTIVE: This is an internal bug in {script_name}. "
            "Document this failure in the skill's KNOWN_BUGS.md and notify the user."
        ),
        "logFile": str(log_file),
    })

# The superset of scopes for all skills
ALL_SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
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
WORKSPACE_DIR = Path(os.environ.get("GOOGLE_WORKSPACE_DIR", Path.home() / ".google_workspace"))

class AuthError(Exception):
    """Raised when authentication fails, with a machine-readable fix suggestion."""
    def __init__(self, message: str, fix: str = ""):
        super().__init__(message)
        self.fix = fix


def print_json(data: Any) -> None:
    """Print data as JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def json_error(service: str, error: str, fix: str = "", exit_code: int = 1) -> None:
    """Print a structured JSON error to stdout and exit.

    Agents can parse this to detect failures and take corrective action.
    """
    print_json({
        "status": "error",
        "service": service,
        "error": error,
        "fix": fix,
    })
    sys.exit(exit_code)


def ensure_authenticated(service_obj: Any, service_name: str) -> None:
    """Check that a service object was successfully built.

    Raises AuthError with a fix suggestion if auth failed.
    """
    if service_obj is None:
        raise AuthError(
            f"{service_name} API not authenticated.",
            fix="Run: uv run scripts/preflight.py  (to diagnose), then: uv run scripts/setup_workspace.py  (to authenticate)",
        )

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

    if (WORKSPACE_DIR / "token.json").exists():
        return WORKSPACE_DIR

    if legacy_dir_name:
        legacy = Path.home() / legacy_dir_name
        if (legacy / "token.json").exists():
            return legacy

    return WORKSPACE_DIR

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

    return creds



