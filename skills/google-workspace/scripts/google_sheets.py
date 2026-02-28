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
  add-tab        Add a new worksheet tab
  rename-tab     Rename an existing worksheet tab
  delete-tab     Delete a worksheet tab (by sheet ID)
  list-tabs      List all worksheet tabs
  format-range   Apply bold/background-color to a cell range
  freeze-panes   Freeze rows/columns
  auto-resize    Auto-resize columns in a range
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
            raise workspace_lib.AuthError(
                "Sheets API not authenticated.",
                fix="Run: uv run scripts/preflight.py  (to diagnose), then: uv run scripts/setup_workspace.py  (to authenticate)",
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
    # Tab management
    # ────────────────────────────────────────────────────────────

    def list_tabs(self, spreadsheet_id: str) -> Dict[str, Any]:
        """List all worksheet tabs."""
        self.ensure_service()
        result = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id, fields="sheets.properties"
        ).execute()
        sheets = [
            {"sheetId": s["properties"]["sheetId"], "title": s["properties"]["title"], "index": s["properties"]["index"]}
            for s in result.get("sheets", [])
        ]
        return {"spreadsheetId": spreadsheet_id, "tabs": sheets}

    def add_tab(self, spreadsheet_id: str, title: str) -> Dict[str, Any]:
        """Add a new worksheet tab."""
        self.ensure_service()
        body = {"requests": [{"addSheet": {"properties": {"title": title}}}]}
        result = self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        new_props = result.get("replies", [{}])[0].get("addSheet", {}).get("properties", {})
        return {"spreadsheetId": spreadsheet_id, "newTab": new_props}

    def rename_tab(self, spreadsheet_id: str, sheet_id: int, new_title: str) -> Dict[str, Any]:
        """Rename a worksheet tab by its numeric sheetId."""
        self.ensure_service()
        body = {
            "requests": [{
                "updateSheetProperties": {
                    "properties": {"sheetId": sheet_id, "title": new_title},
                    "fields": "title",
                }
            }]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "sheetId": sheet_id, "newTitle": new_title}

    def delete_tab(self, spreadsheet_id: str, sheet_id: int) -> Dict[str, Any]:
        """Delete a worksheet tab by its numeric sheetId."""
        self.ensure_service()
        body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "deletedSheetId": sheet_id}

    # ────────────────────────────────────────────────────────────
    # Formatting and layout
    # ────────────────────────────────────────────────────────────

    def freeze_panes(
        self, spreadsheet_id: str, sheet_id: int, frozen_rows: int = 0, frozen_cols: int = 0
    ) -> Dict[str, Any]:
        """Freeze the top N rows and/or left M columns of a sheet."""
        self.ensure_service()
        body = {
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {
                            "frozenRowCount": frozen_rows,
                            "frozenColumnCount": frozen_cols,
                        },
                    },
                    "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
                }
            }]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "sheetId": sheet_id, "frozenRows": frozen_rows, "frozenCols": frozen_cols}

    def auto_resize_columns(
        self, spreadsheet_id: str, sheet_id: int, start_col: int = 0, end_col: int = 26
    ) -> Dict[str, Any]:
        """Auto-resize a range of columns to fit their content."""
        self.ensure_service()
        body = {
            "requests": [{
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": start_col,
                        "endIndex": end_col,
                    }
                }
            }]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "sheetId": sheet_id, "resizedCols": f"{start_col}-{end_col}"}

    def format_range(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        start_col: int,
        end_col: int,
        bold: Optional[bool] = None,
        bg_color_hex: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Apply basic formatting (bold, background color) to a cell range."""
        self.ensure_service()
        cell_format: Dict[str, Any] = {}
        fields_parts: List[str] = []

        if bold is not None:
            cell_format.setdefault("textFormat", {})["bold"] = bold
            fields_parts.append("userEnteredFormat.textFormat.bold")

        if bg_color_hex:
            r, g, b = (
                int(bg_color_hex.lstrip("#")[i:i+2], 16) / 255.0
                for i in (0, 2, 4)
            )
            cell_format["backgroundColor"] = {"red": r, "green": g, "blue": b}
            fields_parts.append("userEnteredFormat.backgroundColor")

        if not fields_parts:
            raise ValueError("Specify at least one of --bold or --bg-color.")

        body = {
            "requests": [{
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col,
                    },
                    "cell": {"userEnteredFormat": cell_format},
                    "fields": ",".join(fields_parts),
                }
            }]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        return {"spreadsheetId": spreadsheet_id, "formatted": fields_parts}


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
    sp.add_argument("--values", required=True, nargs="+", help="JSON 2D array, e.g. [[A, B]]")

    # update
    sp = subparsers.add_parser("update", help="Update values in a range")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--range", required=True, help="A1 notation range (e.g. 'Sheet1!A1:D5')")
    sp.add_argument("--values", required=True, nargs="+", help="JSON string representing a 2D array of values")

    # clear
    sp = subparsers.add_parser("clear", help="Clear values in a range")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--range", required=True, help="A1 notation range (e.g. 'Sheet1!A1:D5')")

    # list-tabs
    sp = subparsers.add_parser("list-tabs", help="List all worksheet tabs")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")

    # add-tab
    sp = subparsers.add_parser("add-tab", help="Add a new worksheet tab")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--title", required=True, help="New tab name")

    # rename-tab
    sp = subparsers.add_parser("rename-tab", help="Rename a worksheet tab")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--sheet-id", required=True, type=int, help="Numeric sheet ID (from list-tabs)")
    sp.add_argument("--title", required=True, help="New tab name")

    # delete-tab
    sp = subparsers.add_parser("delete-tab", help="Delete a worksheet tab")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--sheet-id", required=True, type=int, help="Numeric sheet ID (from list-tabs)")

    # format-range
    sp = subparsers.add_parser("format-range", help="Apply bold/background-color to a range")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--sheet-id", required=True, type=int, help="Numeric sheet ID")
    sp.add_argument("--start-row", required=True, type=int, help="Start row index (0-based)")
    sp.add_argument("--end-row", required=True, type=int, help="End row index (exclusive, 0-based)")
    sp.add_argument("--start-col", required=True, type=int, help="Start col index (0-based)")
    sp.add_argument("--end-col", required=True, type=int, help="End col index (exclusive, 0-based)")
    sp.add_argument("--bold", action=argparse.BooleanOptionalAction, default=None)
    sp.add_argument("--bg-color", help="Background color hex (e.g. #4285F4)")

    # freeze-panes
    sp = subparsers.add_parser("freeze-panes", help="Freeze rows and/or columns")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--sheet-id", required=True, type=int, help="Numeric sheet ID")
    sp.add_argument("--rows", type=int, default=0, help="Number of rows to freeze")
    sp.add_argument("--cols", type=int, default=0, help="Number of columns to freeze")

    # auto-resize
    sp = subparsers.add_parser("auto-resize", help="Auto-resize columns to fit content")
    sp.add_argument("--id", required=True, help="Spreadsheet ID")
    sp.add_argument("--sheet-id", required=True, type=int, help="Numeric sheet ID")
    sp.add_argument("--start-col", type=int, default=0, help="Start col index (0-based)")
    sp.add_argument("--end-col", type=int, default=26, help="End col index (exclusive)")

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
                msg = "Failed to parse values JSON: " + str(e) + ". Provide a valid JSON 2D array."
                raise ValueError(msg)
            
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

        elif args.command == "list-tabs":
            result = tool.list_tabs(args.id)
            workspace_lib.print_json(result)

        elif args.command == "add-tab":
            result = tool.add_tab(args.id, args.title)
            workspace_lib.print_json({"status": "tab_added", "result": result})

        elif args.command == "rename-tab":
            result = tool.rename_tab(args.id, args.sheet_id, args.title)
            workspace_lib.print_json({"status": "tab_renamed", "result": result})

        elif args.command == "delete-tab":
            result = tool.delete_tab(args.id, args.sheet_id)
            workspace_lib.print_json({"status": "tab_deleted", "result": result})

        elif args.command == "format-range":
            result = tool.format_range(
                args.id, args.sheet_id,
                args.start_row, args.end_row,
                args.start_col, args.end_col,
                bold=args.bold, bg_color_hex=args.bg_color,
            )
            workspace_lib.print_json({"status": "formatted", "result": result})

        elif args.command == "freeze-panes":
            result = tool.freeze_panes(args.id, args.sheet_id, args.rows, args.cols)
            workspace_lib.print_json({"status": "frozen", "result": result})

        elif args.command == "auto-resize":
            result = tool.auto_resize_columns(args.id, args.sheet_id, args.start_col, args.end_col)
            workspace_lib.print_json({"status": "resized", "result": result})

        else:
            parser.print_help()

    except workspace_lib.AuthError as e:
        workspace_lib.json_error("google_sheets", str(e), fix=e.fix)
    except Exception as e:
        workspace_lib.report_crash("google_sheets.py", e)

if __name__ == "__main__":
    main()
