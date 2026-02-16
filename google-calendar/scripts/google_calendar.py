#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Calendar Skill - AI-powered Calendar interactions.

Features:
- List upcoming events
- Create new events
- Accept ISO8601 date-time strings for event start/end
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

# --- Configuration ---

CREDENTIALS_DIR = Path(os.environ.get("CALENDAR_CREDENTIALS_DIR", Path.home() / ".calendar_credentials"))
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/calendar.readonly"],
    "events": ["https://www.googleapis.com/auth/calendar.events"],
    "full": ["https://www.googleapis.com/auth/calendar"],
}
DEFAULT_SCOPE = "events"

class CalendarTool:
    def __init__(self, skip_auth=False):
        self.service: Optional[Resource] = None
        if not skip_auth:
            self._authenticate()

    def _get_current_scope(self) -> str:
        if SCOPE_FILE.exists():
            return SCOPE_FILE.read_text().strip()
        return DEFAULT_SCOPE

    def setup_interactive(self):
        """Forces interactive authentication using credentials.json."""
        print(f"🔵 Starting Interactive Setup for Google Calendar...")
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
            
            self.service = build("calendar", "v3", credentials=creds)
            print(f"✅ Authentication successful! Token saved to {TOKEN_FILE}")
            
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")

    def _authenticate(self) -> None:
        creds = None
        scope = self._get_current_scope()
        scopes = SCOPES_MAP.get(scope, SCOPES_MAP[DEFAULT_SCOPE])

        # 1. Try Local Token (JSON)
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)
            except Exception:
                pass

        # 2. Try ADC (Application Default Credentials)
        # Note: We prioritize this only if explicitly set up, but for this skill, 
        # a specific token from setup() is usually preferred to avoid scope issues.
        if not creds or not creds.valid:
            try:
                creds, _ = google.auth.default(scopes=scopes)
                if (
                    creds
                    and creds.expired
                    and getattr(creds, "refresh_token", None)
                ):
                    creds.refresh(Request())
            except Exception:
                 creds = None

        # 3. Fallback to Client Secrets (Auto-UI)
        if not creds or not creds.valid:
            if (
                creds
                and creds.expired
                and getattr(creds, "refresh_token", None)
            ):
                try:
                    creds.refresh(Request())
                    if TOKEN_FILE.exists():
                        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
                        TOKEN_FILE.write_text(creds.to_json())
                except Exception:
                    if TOKEN_FILE.exists():
                        TOKEN_FILE.unlink()
                    creds = None

            # If we still don't have creds, we can't proceed automatically without UI in a non-setup command.
            if not creds and CLIENT_SECRETS_FILE.exists():
                # We could trigger the flow here, but it's better to ask user to run setup
                pass

        if creds:
             self.service = build("calendar", "v3", credentials=creds)

    def ensure_service(self):
        if not self.service:
            raise RuntimeError(
                f"Calendar API not authenticated. Please run 'uv run google_calendar.py setup'."
            )

    def list_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """List upcoming events."""
        self.ensure_service()
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return events_result.get("items", [])

    def create_event(self, summary: str, start_time: str, end_time: str, description: str = "") -> Dict[str, Any]:
        """Create a new event."""
        self.ensure_service()
        
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "UTC"},  # Expecting ISO strings
            "end": {"dateTime": end_time, "timeZone": "UTC"},
        }

        return self.service.events().insert(calendarId="primary", body=event).execute()

def print_json(data: Any):
    print(json.dumps(data, indent=2, default=str))

def main():
    parser = argparse.ArgumentParser(description="Google Calendar AI Skill")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # list
    list_parser = subparsers.add_parser("list", help="List upcoming events")
    list_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # create
    create_parser = subparsers.add_parser("create", help="Create an event")
    create_parser.add_argument("--summary", required=True, help="Event title")
    create_parser.add_argument("--start", required=True, help="ISO Start time (e.g. 2026-02-14T10:00:00)")
    create_parser.add_argument("--end", required=True, help="ISO End time")
    create_parser.add_argument("--description", help="Description")

    args = parser.parse_args()

    if args.command == "setup":
        # Force a fresh setup skipping auto-auth
        tool = CalendarTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = CalendarTool()
        
        if args.command == "verify":
            tool.ensure_service()
            # Real API check: attempt to list 1 event to validate token usability
            tool.list_events(max_results=1)
            print_json({"status": "authenticated", "message": "Calendar API ready"})

        elif args.command == "list":
            events = tool.list_events(args.limit)
            print_json(events)
        
        elif args.command == "create":
            event = tool.create_event(args.summary, args.start, args.end, args.description or "")
            print_json({"status": "created", "event": event})
            
        else:
            parser.print_help()

    except Exception as e:
        print_json({"status": "error", "message": str(e), "type": type(e).__name__})

if __name__ == "__main__":
    main()
