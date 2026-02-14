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
- Parse simple time strings (via `dateutil` if available, or strict ISO)
"""

import argparse
import json
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

# --- Configuration ---

CREDENTIALS_DIR = Path(os.environ.get("CALENDAR_CREDENTIALS_DIR", Path.home() / ".calendar_credentials"))
TOKEN_FILE = CREDENTIALS_DIR / "token.pickle"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/calendar.readonly"],
    "events": ["https://www.googleapis.com/auth/calendar.events"],
    "full": ["https://www.googleapis.com/auth/calendar"],
}
DEFAULT_SCOPE = "events"

class CalendarTool:
    def __init__(self):
        self.service: Optional[Resource] = None
        self._authenticate()

    def _get_current_scope(self) -> str:
        if SCOPE_FILE.exists():
            return SCOPE_FILE.read_text().strip()
        return DEFAULT_SCOPE

    def _authenticate(self) -> None:
        creds = None
        scope = self._get_current_scope()
        scopes = SCOPES_MAP.get(scope, SCOPES_MAP[DEFAULT_SCOPE])

        # 1. Try Local Pickle
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, "rb") as token:
                    creds = pickle.load(token)
            except Exception:
                pass

        # 2. Try ADC
        if not creds or not creds.valid:
            try:
                creds, _ = google.auth.default(scopes=scopes)
                if creds and creds.expired and creds.refresh_token:
                     creds.refresh(Request())
            except Exception:
                 creds = None

        # 3. Fallback to Client Secrets
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    if TOKEN_FILE.exists():
                         with open(TOKEN_FILE, "wb") as token:
                            pickle.dump(creds, token)
                except Exception:
                    if TOKEN_FILE.exists():
                        TOKEN_FILE.unlink()
                    creds = None

            if not creds:
                if not CLIENT_SECRETS_FILE.exists():
                    print(f"Error: Credentials file not found at {CLIENT_SECRETS_FILE}")
                    print("To fix, either:")
                    print("1. Run: gcloud auth application-default login --scopes https://www.googleapis.com/auth/calendar.events")
                    print("2. OR download credentials.json to that location.")
                    return

                print(f"Starting authentication flow using {CLIENT_SECRETS_FILE}...")
                flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), scopes)
                creds = flow.run_local_server(port=0)

                CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
                with open(TOKEN_FILE, "wb") as token:
                    pickle.dump(creds, token)

        if creds:
             self.service = build("calendar", "v3", credentials=creds)

    def ensure_service(self):
        if not self.service:
            raise RuntimeError(
                f"Calendar API not authenticated. Please ensure '{CLIENT_SECRETS_FILE}' exists "
                "and run 'python3 calendar.py setup'."
            )

    def list_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """List upcoming 10 events."""
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
        tool = CalendarTool()
        if tool.service:
            print_json({"status": "success", "message": "Authenticated successfully"})
        else:
            print_json({"status": "error", "message": "Authentication failed or cancelled"})
        return

    try:
        tool = CalendarTool()
        
        if args.command == "verify":
            # If we got here, tool.ensure_service() would have succeeded during __init__ (sort of)
            # Actually __init__ just calls _authenticate. ensure_service checks self.service.
            tool.ensure_service()
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
