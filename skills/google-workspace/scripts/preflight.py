#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Workspace Preflight Check.

Single command to verify that all Google Workspace services are ready.
Agents should run this FIRST before calling any other service script.

Usage:
  uv run scripts/preflight.py          # Full check (all services)
  uv run scripts/preflight.py --quick  # Just credentials + token (no API pings)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Add script directory to path to import workspace_lib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import workspace_lib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def _check(ok: bool, error: str = "", fix: str = "", **extra: Any) -> Dict[str, Any]:
    """Build a check result dict."""
    result: Dict[str, Any] = {"ok": ok}
    if not ok:
        if error:
            result["error"] = error
        if fix:
            result["fix"] = fix
    result.update(extra)
    return result


def check_credentials_file() -> Dict[str, Any]:
    """Check that credentials.json (OAuth client secret) exists."""
    search_paths = [
        workspace_lib.WORKSPACE_DIR / "credentials.json",
        Path.home() / ".gemini/credentials/google_client_secret.json",
        Path.home() / "Downloads/credentials.json",
        Path.cwd() / "credentials.json",
    ]
    for p in search_paths:
        if p.exists():
            return _check(True, path=str(p))

    return _check(
        False,
        error="credentials.json not found in any expected location",
        fix=(
            "Download OAuth client secret from Google Cloud Console > APIs & Services > Credentials, "
            f"then save to: {workspace_lib.WORKSPACE_DIR / 'credentials.json'}"
        ),
        searched=[str(p) for p in search_paths],
    )


def check_token_file() -> Dict[str, Any]:
    """Check that token.json exists."""
    token_file = workspace_lib.WORKSPACE_DIR / "token.json"

    # Also check legacy dirs
    legacy_dirs = [
        Path.home() / ".gmail_credentials",
        Path.home() / ".calendar_credentials",
        Path.home() / ".google_contacts_credentials",
        Path.home() / ".google_drive_credentials",
        Path.home() / ".google_photos_credentials",
    ]

    if token_file.exists():
        return _check(True, path=str(token_file))

    for legacy in legacy_dirs:
        legacy_token = legacy / "token.json"
        if legacy_token.exists():
            return _check(
                True,
                path=str(legacy_token),
                warning=f"Using legacy token from {legacy}. Run setup_workspace.py to consolidate.",
            )

    return _check(
        False,
        error="No token.json found. Authentication has never been completed.",
        fix="Run: uv run scripts/setup_workspace.py",
    )


def check_token_validity() -> Dict[str, Any]:
    """Check that the token is valid and has the right scopes."""
    creds_dir = workspace_lib.find_credentials_dir()
    token_file = creds_dir / "token.json"

    if not token_file.exists():
        return _check(False, error="No token file", fix="Run: uv run scripts/setup_workspace.py")

    try:
        creds = Credentials.from_authorized_user_file(str(token_file))
    except Exception as e:
        return _check(
            False,
            error=f"Token file is corrupted: {e}",
            fix="Delete the token and re-authenticate: rm {token_file} && uv run scripts/setup_workspace.py",
        )

    # Check scopes
    granted = set(creds.scopes or [])
    required = set(workspace_lib.ALL_SCOPES)
    missing = required - granted
    if missing:
        return _check(
            False,
            error="Token is missing required scopes",
            fix="Re-run setup to request all scopes: uv run scripts/setup_workspace.py",
            missing_scopes=sorted(missing),
            granted_scopes=sorted(granted),
        )

    # Check expiry
    if creds.expired:
        if getattr(creds, "refresh_token", None):
            try:
                creds.refresh(Request())
                token_file.write_text(creds.to_json())
                return _check(
                    True,
                    warning="Token was expired but was refreshed successfully.",
                    refreshed=True,
                )
            except Exception as e:
                return _check(
                    False,
                    error=f"Token expired and refresh failed: {e}",
                    fix="Re-authenticate: uv run scripts/setup_workspace.py",
                )
        else:
            return _check(
                False,
                error="Token expired and has no refresh token",
                fix="Re-authenticate: uv run scripts/setup_workspace.py",
            )

    # Compute time until access token expires
    expiry_info: Dict[str, Any] = {}
    if creds.expiry:
        now = datetime.now(timezone.utc)
        # Ensure expiry is timezone-aware
        expiry = creds.expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        remaining = (expiry - now).total_seconds()
        expiry_info["expires_in_seconds"] = int(remaining)
        expiry_info["expires_in_minutes"] = round(remaining / 60, 1)

    return _check(True, **expiry_info)


def check_systemd_timer() -> Dict[str, Any]:
    """Check if the token maintainer timer is installed and active."""
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "workspace-token-maintainer.timer"],
            capture_output=True,
            text=True,
        )
        is_active = result.stdout.strip() == "active"
        if is_active:
            return _check(True, state="active")
        else:
            return _check(
                False,
                error=f"Timer state: {result.stdout.strip() or 'not found'}",
                fix="Run: bash scripts/install_services.sh && systemctl --user enable --now workspace-token-maintainer.timer",
            )
    except FileNotFoundError:
        return _check(
            False,
            error="systemctl not found (not a systemd system)",
            fix="Token refresh must be done manually or via cron.",
        )


def check_uv() -> Dict[str, Any]:
    """Check that uv is installed and in PATH."""
    uv_path = shutil.which("uv")
    if uv_path:
        return _check(True, path=uv_path)
    return _check(
        False,
        error="uv not found in PATH",
        fix="Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh",
    )


def check_service_api(service_name: str, api_name: str, api_version: str) -> Dict[str, Any]:
    """Ping a Google API to verify it is reachable and auth works."""
    creds_dir = workspace_lib.find_credentials_dir()
    token_file = creds_dir / "token.json"

    if not token_file.exists():
        return _check(False, error="No token", fix="Run: uv run scripts/setup_workspace.py")

    try:
        creds = Credentials.from_authorized_user_file(str(token_file))
        if creds.expired and getattr(creds, "refresh_token", None):
            creds.refresh(Request())

        from googleapiclient.discovery import build

        service = build(api_name, api_version, credentials=creds)

        # Quick smoke test per service
        if api_name == "gmail":
            service.users().getProfile(userId="me").execute()
        elif api_name == "calendar":
            service.calendarList().list(maxResults=1).execute()
        elif api_name == "people":
            service.people().connections().list(
                resourceName="people/me", pageSize=1, personFields="names"
            ).execute()
        elif api_name == "drive":
            service.files().list(pageSize=1).execute()
        elif api_name == "docs":
            # Docs has no list, so we just build the service (already done)
            pass
        elif api_name == "sheets":
            # Sheets has no list, so we just build the service (already done)
            pass

        return _check(True)

    except Exception as e:
        error_str = str(e)
        # Truncate long Google API errors
        if len(error_str) > 200:
            error_str = error_str[:200] + "..."
        return _check(False, error=error_str)


def run_preflight(quick: bool = False) -> Dict[str, Any]:
    """Run all preflight checks and return structured results."""
    checks: Dict[str, Any] = {}

    checks["uv"] = check_uv()
    checks["credentials_file"] = check_credentials_file()
    checks["token_file"] = check_token_file()
    checks["token_validity"] = check_token_validity()
    checks["systemd_timer"] = check_systemd_timer()

    if not quick:
        # Only ping APIs if we have a valid token
        if checks["token_validity"].get("ok"):
            service_checks = [
                ("gmail", "gmail", "v1"),
                ("calendar", "calendar", "v3"),
                ("contacts", "people", "v1"),
                ("drive", "drive", "v3"),
                ("docs", "docs", "v1"),
                ("sheets", "sheets", "v4"),
            ]
            for name, api, version in service_checks:
                checks[name] = check_service_api(name, api, version)
        else:
            for name in ("gmail", "calendar", "contacts", "drive", "docs", "sheets"):
                checks[name] = _check(False, error="Skipped: token is invalid", fix="Fix token issues first")

    all_ok = all(c.get("ok") for c in checks.values())

    return {"ok": all_ok, "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Google Workspace Preflight Check — run this before using any service script."
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Only check credentials and token, skip API pings",
    )
    args = parser.parse_args()

    result = run_preflight(quick=args.quick)
    print(json.dumps(result, indent=2, default=str))

    # Exit with non-zero if any check failed
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
