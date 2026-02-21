#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Sheets Skill - Content manipulation for AI agents.

Commands:
  verify         Check authentication status
  setup          Run interactive OAuth flow
  read           Read values from a range
  create         Create a new spreadsheet
  append         Append a row of values to a range
  update         Update values in a range
  clear          Clear values in a range
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

import workspace_lib

# --- Configuration ---

def _find_credentials_dir() -> Path:
    return workspace_lib.find_credentials_dir(
        env_var="SHEETS_CREDENTIALS_DIR",
        legacy_dir_name=".sheets_credentials"
    )

CREDENTIALS_DIR = _find_credentials_dir()
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/spreadsheets.readonly"],
    "full": ["https://www.googleapis.com/auth/spreadsheets"],
}
DEFAULT_SCOPE = "full"


class SheetsTool:
    """Sheets wrapper for AI agents."""

    def __init__(self, skip_auth: bool = False):
        self.service: Optional[Resource] = None
        if not skip_auth:
            self._authenticate()

    def _get_current_scope(self) -> str:
        if SCOPE_FILE.exists():
            return SCOPE_FILE.read_text().strip()
        return DEFAULT_SCOPE

    def _authenticate(self) -> None:
        """Authenticate using shared workspace library."""
        scope = self._get_current_scope()
        scopes = SCOPES_MAP.get(scope, SCOPES_MAP[DEFAULT_SCOPE])
        
        creds = workspace_lib.authenticate(
            scopes=scopes,
            token_file=TOKEN_FILE,
            client_secrets_file=CLIENT_SECRETS_FILE,
            service_name="Sheets"
        )

        if creds and creds.valid:
            self.service = build("sheets", "v4", credentials=creds)

    def setup_interactive(self) -> None:
        print("🔵 Starting Interactive Setup for Google Sheets...")
        print(f"   Credentials file: {CLIENT_SECRETS_FILE}")

        if not CLIENT_SECRETS_FILE.exists():
            print(f"\n❌ Error: '{CLIENT_SECRETS_FILE}' not found.")
            print("\nTo fix this:")
            print("1. Go to Google Cloud Console > APIs & Services > Credentials.")
            print("2. Create 'OAuth 2.0 Client IDs' (Application type: Desktop app).")
            print("3. Download the JSON file.")
            print(f"4. Rename it to 'credentials.json' and place it in: {CREDENTIALS_DIR}")
            return

        scope = self._get_current_scope()
        scopes = SCOPES_MAP.get(scope, SCOPES_MAP[DEFAULT_SCOPE])

        print(f"   Requesting scopes: {scopes}")
        print("👉 A browser window will open. Please log in and allow access.")

        try:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), scopes)
            creds = flow.run_local_server(port=0)

            CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
            TOKEN_FILE.write_text(creds.to_json())

            self.service = build("sheets", "v4", credentials=creds)
            print(f"✅ Authentication successful! Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")

    def ensure_service(self) -> None:
        if not self.service:
            raise RuntimeError(
                "Sheets API not authenticated. Run 'setup' command or configure ADC."
            )

    # ────────────────────────────────────────────────────────────
    # Read
    # ────────────────────────────────────────────────────────────

    def read_values(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """Read values from a range."""
        self.ensure_service()
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
        return {
            "spreadsheetId": spreadsheet_id,
            "range": range_name,
            "values": result.get("values", [])
        }

    # ────────────────────────────────────────────────────────────
    # Create
    # ────────────────────────────────────────────────────────────

    def create_spreadsheet(self, title: str) -> Dict[str, Any]:
        """Create a new spreadsheet."""
        self.ensure_service()
        spreadsheet = {
            "properties": {
                "title": title
            }
        }
        result = self.service.spreadsheets().create(
            body=spreadsheet,
            fields="spreadsheetId,properties.title"
        ).execute()
        return {
            "spreadsheetId": result.get("spreadsheetId"),
            "title": result.get("properties", {}).get("title")
        }

    # ────────────────────────────────────────────────────────────
    # Update
    # ────────────────────────────────────────────────────────────

    def append_values(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Append a row of values to a range."""
        self.ensure_service()
        body = {
            "values": values
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "updates": result.get("updates", {})}

    def update_values(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Update values in a range."""
        self.ensure_service()
        body = {
            "values": values
        }
        result = self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "updatedCells": result.get("updatedCells")}

    def clear_values(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """Clear values in a range."""
        self.ensure_service()
        result = self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body={}
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "clearedRange": result.get("clearedRange")}


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Google Sheets AI Skill")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # read
    sp = subparsers.add_parser("read", help="Read values from a range")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--range", required=True, help="A1 notation range (e.g. 'Sheet1!A1:D5')")

    # create
    sp = subparsers.add_parser("create", help="Create a new spreadsheet")
    sp.add_argument("--title", required=True, help="Spreadsheet title")

    # append
    sp = subparsers.add_parser("append", help="Append a row of values to a range")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--range", required=True, help="A1 notation range (e.g. 'Sheet1!A1:D5')")
    sp.add_argument("--values", required=True, nargs="+", help="JSON string representing a 2D array of values (e.g. '[["A", "B"]]')")

    # update
    sp = subparsers.add_parser("update", help="Update values in a range")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--range", required=True, help="A1 notation range (e.g. 'Sheet1!A1:D5')")
    sp.add_argument("--values", required=True, nargs="+", help="JSON string representing a 2D array of values")

    # clear
    sp = subparsers.add_parser("clear", help="Clear values in a range")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--range", required=True, help="A1 notation range (e.g. 'Sheet1!A1:D5')")

    args = parser.parse_args()

    if args.command == "setup":
        tool = SheetsTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = SheetsTool()

        if args.command == "verify":
            tool.ensure_service()
            workspace_lib.print_json({"status": "authenticated", "message": "Sheets API ready"})

        elif args.command == "read":
            values = tool.read_values(args.id, args.range)
            workspace_lib.print_json(values)

        elif args.command == "create":
            sheet = tool.create_spreadsheet(args.title)
            workspace_lib.print_json({"status": "created", "spreadsheet": sheet})

        elif args.command in ["append", "update"]:
            # Parse the JSON values string. Join arguments back into a single string first in case of unquoted spaces.
            values_str = " ".join(args.values)
            try:
                values_array = json.loads(values_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse values JSON: {e}. Please provide a valid JSON array like '[["A", "B"]]'")
            
            if not isinstance(values_array, list) or not all(isinstance(row, list) for row in values_array):
                raise ValueError("Values must be a 2D array (a list of lists).")

            if args.command == "append":
                result = tool.append_values(args.id, args.range, values_array)
                workspace_lib.print_json({"status": "appended", "result": result})
            elif args.command == "update":
                result = tool.update_values(args.id, args.range, values_array)
                workspace_lib.print_json({"status": "updated", "result": result})

        elif args.command == "clear":
            result = tool.clear_values(args.id, args.range)
            workspace_lib.print_json({"status": "cleared", "result": result})

        else:
            parser.print_help()

    except Exception as e:
        workspace_lib.print_json({"status": "error", "message": str(e), "type": type(e).__name__})

if __name__ == "__main__":
    main()
