#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Calendar Skill - Full CRUD for AI agents.

Commands:
  verify              Check authentication status
  setup               Run interactive OAuth flow
  list                List upcoming events
  get                 Get a single event by ID
  search              Search events by text query
  create              Create a new event (supports RRULE for recurring)
  update              Update an existing event
  delete              Delete an event
  calendars           List all available calendars
  add-calendar        Subscribe to a secondary calendar by ID
  remove-calendar     Unsubscribe from a secondary calendar
  quick               Quick-add an event from natural language
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
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
        env_var="CALENDAR_CREDENTIALS_DIR",
        legacy_dir_name=".calendar_credentials"
    )

CREDENTIALS_DIR = _find_credentials_dir()
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/calendar.readonly"],
    "events": ["https://www.googleapis.com/auth/calendar.events"],
    "full": ["https://www.googleapis.com/auth/calendar"],
}
DEFAULT_SCOPE = "full"


class CalendarTool:
    """Full CRUD Calendar wrapper for AI agents."""

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
            service_name="Calendar"
        )

        if creds and creds.valid:
            self.service = build("calendar", "v3", credentials=creds)

    def setup_interactive(self) -> None:
        print("🔵 Starting Interactive Setup for Google Calendar...")
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

    def ensure_service(self) -> None:
        if not self.service:
            raise RuntimeError(
                "Calendar API not authenticated. Run 'setup' command or configure ADC."
            )

    # ────────────────────────────────────────────────────────────
    # List Calendars
    # ────────────────────────────────────────────────────────────

    def list_calendars(self) -> List[Dict[str, Any]]:
        """List all calendars the user has access to."""
        self.ensure_service()
        result = self.service.calendarList().list().execute()
        calendars = []
        for cal in result.get("items", []):
            calendars.append({
                "id": cal.get("id"),
                "summary": cal.get("summary"),
                "primary": cal.get("primary", False),
                "accessRole": cal.get("accessRole"),
                "backgroundColor": cal.get("backgroundColor"),
                "timeZone": cal.get("timeZone"),
            })
        return calendars

    # ────────────────────────────────────────────────────────────
    # CRUD
    # ────────────────────────────────────────────────────────────

    def list_events(
        self,
        max_results: int = 10,
        calendar_id: str = "primary",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List upcoming events, optionally filtered by time range and text query."""
        self.ensure_service()
        if not time_min:
            time_min = datetime.now(timezone.utc).isoformat()

        kwargs: Dict[str, Any] = {
            "calendarId": calendar_id,
            "timeMin": time_min,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        if time_max:
            kwargs["timeMax"] = time_max
        if query:
            kwargs["q"] = query

        result = self.service.events().list(**kwargs).execute()
        return self._normalize_events(result.get("items", []))

    def get_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Get a single event by ID."""
        self.ensure_service()
        event = self.service.events().get(
            calendarId=calendar_id, eventId=event_id
        ).execute()
        return self._normalize_event(event)

    def search_events(
        self, query: str, max_results: int = 10, calendar_id: str = "primary"
    ) -> List[Dict[str, Any]]:
        """Search events by free-text query."""
        return self.list_events(max_results=max_results, calendar_id=calendar_id, query=query)

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: str = "",
        location: str = "",
        attendees: Optional[List[str]] = None,
        calendar_id: str = "primary",
        timezone_str: str = "America/Phoenix",
        all_day: bool = False,
        rrule: Optional[str] = None,
        drive_file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new calendar event.

        Args:
            rrule: RFC 5545 recurrence rule string, e.g.
                'RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR'
                'RRULE:FREQ=MONTHLY;BYMONTHDAY=1;COUNT=12'
            drive_file_ids: List of Drive file IDs to attach to the event.
        """
        self.ensure_service()

        if all_day:
            event: Dict[str, Any] = {
                "summary": summary,
                "description": description,
                "location": location,
                "start": {"date": start_time},
                "end": {"date": end_time},
            }
        else:
            event = {
                "summary": summary,
                "description": description,
                "location": location,
                "start": {"dateTime": start_time, "timeZone": timezone_str},
                "end": {"dateTime": end_time, "timeZone": timezone_str},
            }

        if attendees:
            event["attendees"] = [{"email": a} for a in attendees]

        if rrule:
            # rrule should be a full RRULE string, e.g. "RRULE:FREQ=DAILY;COUNT=5"
            event["recurrence"] = [rrule if rrule.startswith("RRULE:") else f"RRULE:{rrule}"]

        if drive_file_ids:
            event["attachments"] = [
                {"fileUrl": f"https://drive.google.com/open?id={fid}"}
                for fid in drive_file_ids
            ]

        kwargs: Dict[str, Any] = {"calendarId": calendar_id, "body": event}
        if drive_file_ids:
            kwargs["supportsAttachments"] = True

        result = self.service.events().insert(**kwargs).execute()
        return self._normalize_event(result)

    def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        timezone_str: str = "America/Phoenix",
    ) -> Dict[str, Any]:
        """Update an existing event (patch semantics — only provided fields change)."""
        self.ensure_service()
        patch: Dict[str, Any] = {}

        if summary is not None:
            patch["summary"] = summary
        if description is not None:
            patch["description"] = description
        if location is not None:
            patch["location"] = location
        if start_time is not None:
            patch["start"] = {"dateTime": start_time, "timeZone": timezone_str}
        if end_time is not None:
            patch["end"] = {"dateTime": end_time, "timeZone": timezone_str}
        if attendees is not None:
            patch["attendees"] = [{"email": a} for a in attendees]

        if not patch:
            raise ValueError("No fields provided to update.")

        result = self.service.events().patch(
            calendarId=calendar_id, eventId=event_id, body=patch
        ).execute()
        return self._normalize_event(result)

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, str]:
        """Delete an event."""
        self.ensure_service()
        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return {"status": "deleted", "eventId": event_id}

    def quick_add(self, text: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Quick-add an event from natural language (e.g. 'Lunch with Yoda tomorrow noon')."""
        self.ensure_service()
        result = self.service.events().quickAdd(
            calendarId=calendar_id, text=text
        ).execute()
        return self._normalize_event(result)

    # ────────────────────────────────────────────────────────────
    # Normalization helpers
    # ────────────────────────────────────────────────────────────

    def _normalize_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self._normalize_event(e) for e in events]

    def _normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": event.get("id"),
            "summary": event.get("summary"),
            "description": event.get("description"),
            "location": event.get("location"),
            "start": event.get("start"),
            "end": event.get("end"),
            "status": event.get("status"),
            "htmlLink": event.get("htmlLink"),
            "attendees": [
                {"email": a.get("email"), "responseStatus": a.get("responseStatus")}
                for a in event.get("attendees", [])
            ],
            "creator": event.get("creator"),
            "organizer": event.get("organizer"),
            "recurrence": event.get("recurrence"),
            "recurringEventId": event.get("recurringEventId"),
            "attachments": event.get("attachments"),
        }

    # ────────────────────────────────────────────────────────────
    # Secondary calendar management
    # ────────────────────────────────────────────────────────────

    def add_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """Subscribe to a secondary calendar by its calendar ID."""
        self.ensure_service()
        result = self.service.calendarList().insert(
            body={"id": calendar_id}
        ).execute()
        return {
            "id": result.get("id"),
            "summary": result.get("summary"),
            "accessRole": result.get("accessRole"),
        }

    def remove_calendar(self, calendar_id: str) -> Dict[str, str]:
        """Unsubscribe from a secondary calendar."""
        self.ensure_service()
        self.service.calendarList().delete(calendarId=calendar_id).execute()
        return {"status": "removed", "calendarId": calendar_id}


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Calendar AI Skill — Full CRUD")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # calendars
    subparsers.add_parser("calendars", help="List all calendars")

    # list
    sp = subparsers.add_parser("list", help="List upcoming events")
    sp.add_argument("--limit", type=int, default=10, help="Max results")
    sp.add_argument("--calendar", default="primary", help="Calendar ID")
    sp.add_argument("--after", help="ISO datetime — only events after this time")
    sp.add_argument("--before", help="ISO datetime — only events before this time")
    sp.add_argument("--query", "-q", help="Free-text search filter")

    # get
    sp = subparsers.add_parser("get", help="Get a single event by ID")
    sp.add_argument("--id", required=True, help="Event ID")
    sp.add_argument("--calendar", default="primary", help="Calendar ID")

    # search
    sp = subparsers.add_parser("search", help="Search events by text query")
    sp.add_argument("--query", "-q", required=True, help="Search query")
    sp.add_argument("--limit", type=int, default=10, help="Max results")
    sp.add_argument("--calendar", default="primary", help="Calendar ID")

    # create
    sp = subparsers.add_parser("create", help="Create a new event")
    sp.add_argument("--summary", required=True, help="Event title")
    sp.add_argument("--start", required=True, help="ISO start time (or YYYY-MM-DD for all-day)")
    sp.add_argument("--end", required=True, help="ISO end time (or YYYY-MM-DD for all-day)")
    sp.add_argument("--description", default="", help="Description")
    sp.add_argument("--location", default="", help="Location")
    sp.add_argument("--attendees", nargs="*", help="Attendee email addresses")
    sp.add_argument("--calendar", default="primary", help="Calendar ID")
    sp.add_argument("--timezone", default="America/Phoenix", help="Timezone")
    sp.add_argument("--all-day", action="store_true", help="Create as all-day event")
    sp.add_argument(
        "--rrule",
        help="RFC 5545 recurrence rule, e.g. 'RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR'",
    )
    sp.add_argument("--drive-files", nargs="*", help="Drive file IDs to attach")

    # add-calendar
    sp = subparsers.add_parser("add-calendar", help="Subscribe to a secondary calendar")
    sp.add_argument("--calendar-id", required=True, help="Calendar ID to subscribe to")

    # remove-calendar
    sp = subparsers.add_parser("remove-calendar", help="Unsubscribe from a secondary calendar")
    sp.add_argument("--calendar-id", required=True, help="Calendar ID to remove")

    # update
    sp = subparsers.add_parser("update", help="Update an existing event")
    sp.add_argument("--id", required=True, help="Event ID")
    sp.add_argument("--summary", help="New title")
    sp.add_argument("--start", help="New ISO start time")
    sp.add_argument("--end", help="New ISO end time")
    sp.add_argument("--description", help="New description")
    sp.add_argument("--location", help="New location")
    sp.add_argument("--attendees", nargs="*", help="New attendee emails (replaces existing)")
    sp.add_argument("--calendar", default="primary", help="Calendar ID")
    sp.add_argument("--timezone", default="America/Phoenix", help="Timezone")

    # delete
    sp = subparsers.add_parser("delete", help="Delete an event")
    sp.add_argument("--id", required=True, help="Event ID")
    sp.add_argument("--calendar", default="primary", help="Calendar ID")

    # quick
    sp = subparsers.add_parser("quick", help="Quick-add from natural language")
    sp.add_argument("--text", required=True, help="Natural language event description")
    sp.add_argument("--calendar", default="primary", help="Calendar ID")

    args = parser.parse_args()

    if args.command == "setup":
        tool = CalendarTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = CalendarTool()

        if args.command == "verify":
            tool.ensure_service()
            tool.list_events(max_results=1)
            workspace_lib.print_json({"status": "authenticated", "message": "Calendar API ready"})

        elif args.command == "calendars":
            cals = tool.list_calendars()
            workspace_lib.print_json(cals)

        elif args.command == "list":
            events = tool.list_events(
                max_results=args.limit,
                calendar_id=args.calendar,
                time_min=args.after,
                time_max=args.before,
                query=args.query,
            )
            workspace_lib.print_json(events)

        elif args.command == "get":
            event = tool.get_event(args.id, calendar_id=args.calendar)
            workspace_lib.print_json(event)

        elif args.command == "search":
            events = tool.search_events(args.query, max_results=args.limit, calendar_id=args.calendar)
            workspace_lib.print_json(events)

        elif args.command == "create":
            event = tool.create_event(
                summary=args.summary,
                start_time=args.start,
                end_time=args.end,
                description=args.description,
                location=args.location,
                attendees=args.attendees,
                calendar_id=args.calendar,
                timezone_str=args.timezone,
                all_day=args.all_day,
                rrule=args.rrule,
                drive_file_ids=args.drive_files,
            )
            workspace_lib.print_json({"status": "created", "event": event})

        elif args.command == "update":
            event = tool.update_event(
                event_id=args.id,
                calendar_id=args.calendar,
                summary=args.summary,
                start_time=args.start,
                end_time=args.end,
                description=args.description,
                location=args.location,
                attendees=args.attendees,
                timezone_str=args.timezone,
            )
            workspace_lib.print_json({"status": "updated", "event": event})

        elif args.command == "delete":
            result = tool.delete_event(args.id, calendar_id=args.calendar)
            workspace_lib.print_json(result)

        elif args.command == "quick":
            event = tool.quick_add(args.text, calendar_id=args.calendar)
            workspace_lib.print_json({"status": "created", "event": event})

        elif args.command == "add-calendar":
            result = tool.add_calendar(args.calendar_id)
            workspace_lib.print_json({"status": "subscribed", "calendar": result})

        elif args.command == "remove-calendar":
            result = tool.remove_calendar(args.calendar_id)
            workspace_lib.print_json(result)

        else:
            parser.print_help()

    except Exception as e:
        workspace_lib.print_json({"status": "error", "message": str(e), "type": type(e).__name__})


if __name__ == "__main__":
    main()
