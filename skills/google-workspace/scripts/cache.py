#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
#   "sqlite-utils>=3.35",
#   "requests>=2.28.0",
# ]
# ///

"""
Google Workspace Cache — Local SQLite index with incremental sync.

Caches metadata from Gmail, Calendar, Contacts, Drive, and Photos into a
local SQLite database for fast queries without hammering the API.

Commands:
  sync       Sync metadata from Google APIs (incremental after first run)
  search     Full-text search across cached metadata
  status     Show cache status (last sync, record counts)
  clear      Delete the cache database
"""

import argparse
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.auth
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    import sqlite_utils
except ImportError:
    print("Error: sqlite-utils is required. Install with: pip install sqlite-utils")
    sys.exit(1)

# --- Configuration ---

WORKSPACE_DIR = Path(
    os.environ.get("GOOGLE_WORKSPACE_DIR", Path.home() / ".google_workspace")
)
CACHE_DIR = Path(
    os.environ.get("WORKSPACE_CACHE_DIR", str(WORKSPACE_DIR))
)
DB_PATH = CACHE_DIR / "cache.db"

ALL_SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
    "https://www.googleapis.com/auth/cloud-platform",
]

PHOTOS_API_BASE = "https://photoslibrary.googleapis.com/v1"

SERVICES = ["gmail", "calendar", "contacts", "drive"]
# Photos only sees app-uploaded data since March 2025 API changes — opt-in only
ALL_SERVICES = SERVICES + ["photos"]

# Network errors that should fail gracefully (not crash the daemon)
NETWORK_ERRORS = (
    socket.timeout,
    socket.gaierror,
    ConnectionError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ReadTimeout,
)


# --- Auth ---


def _find_credentials_dir() -> Path:
    """Find credentials, checking unified then legacy dirs."""
    workspace = Path(
        os.environ.get("GOOGLE_WORKSPACE_DIR", Path.home() / ".google_workspace")
    )
    if (workspace / "token.json").exists():
        return workspace
    # Check legacy dirs
    for name in [
        ".gmail_credentials",
        ".calendar_credentials",
        ".drive_credentials",
    ]:
        legacy = Path.home() / name
        if (legacy / "token.json").exists():
            return legacy
    return workspace


def get_credentials() -> Credentials:
    """Authenticate and return credentials."""
    creds_dir = _find_credentials_dir()
    token_file = creds_dir / "token.json"
    creds = None

    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), ALL_SCOPES)
        except Exception:
            pass

    if not creds or not creds.valid:
        try:
            creds, _ = google.auth.default(scopes=ALL_SCOPES)
            if creds and creds.expired and getattr(creds, "refresh_token", None):
                creds.refresh(Request())
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and getattr(creds, "refresh_token", None):
            creds.refresh(Request())

    if not creds:
        print("Error: Not authenticated. Run setup_workspace.py first.")
        sys.exit(1)

    return creds


# --- Database ---


def get_db() -> sqlite_utils.Database:
    """Open (or create) the cache database."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite_utils.Database(str(DB_PATH))

    # Ensure sync_state table exists
    if "sync_state" not in db.table_names():
        db["sync_state"].create(
            {
                "service": str,
                "sync_token": str,
                "last_sync": str,
                "record_count": int,
            },
            pk="service",
        )

    return db


def get_sync_state(db: sqlite_utils.Database, service: str) -> Dict[str, Any]:
    """Get the sync state for a service."""
    try:
        return dict(db["sync_state"].get(service))
    except Exception:
        return {"service": service, "sync_token": None, "last_sync": None, "record_count": 0}


def set_sync_state(
    db: sqlite_utils.Database,
    service: str,
    sync_token: Optional[str] = None,
    record_count: int = 0,
) -> None:
    """Update sync state for a service."""
    db["sync_state"].upsert(
        {
            "service": service,
            "sync_token": sync_token or "",
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "record_count": record_count,
        },
        pk="service",
    )


# --- Gmail Sync ---


def sync_gmail(db: sqlite_utils.Database, creds: Credentials) -> int:
    """Sync Gmail message metadata using the History API for incremental updates."""
    service = build("gmail", "v1", credentials=creds)
    state = get_sync_state(db, "gmail")
    history_id = state.get("sync_token")

    if history_id:
        # Incremental sync via history.list
        try:
            count = _gmail_incremental(db, service, history_id)
        except Exception:
            # historyId expired — full sync
            count = _gmail_full(db, service)
    else:
        count = _gmail_full(db, service)

    # Get current historyId for next sync
    profile = service.users().getProfile(userId="me").execute()
    new_history_id = profile.get("historyId")
    total = db["gmail_messages"].count if "gmail_messages" in db.table_names() else 0
    set_sync_state(db, "gmail", sync_token=new_history_id, record_count=total)
    return count


def _gmail_full(db: sqlite_utils.Database, service) -> int:
    """Full sync — fetch all message metadata."""
    print("  Gmail: Full sync (first run)...")
    messages = []
    page_token = None
    while True:
        result = service.users().messages().list(
            userId="me", maxResults=500, pageToken=page_token
        ).execute()

        for msg_stub in result.get("messages", []):
            try:
                msg = service.users().messages().get(
                    userId="me",
                    id=msg_stub["id"],
                    format="metadata",
                    metadataHeaders=["From", "To", "Cc", "Subject", "Date"],
                ).execute()
                headers = {
                    h["name"]: h["value"]
                    for h in msg.get("payload", {}).get("headers", [])
                }
                messages.append({
                    "message_id": msg["id"],
                    "thread_id": msg.get("threadId"),
                    "snippet": msg.get("snippet", ""),
                    "sender": headers.get("From", ""),
                    "recipients": headers.get("To", ""),
                    "cc": headers.get("Cc", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "labels": json.dumps(msg.get("labelIds", [])),
                    "size": msg.get("sizeEstimate", 0),
                })
            except Exception:
                continue

            # Batch upsert every 100 messages
            if len(messages) >= 100:
                db["gmail_messages"].upsert_all(messages, pk="message_id", alter=True)
                messages = []

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    if messages:
        db["gmail_messages"].upsert_all(messages, pk="message_id", alter=True)

    # Enable FTS on first sync
    _ensure_fts(db, "gmail_messages", ["subject", "sender", "recipients", "snippet"])

    count = db["gmail_messages"].count
    print(f"  Gmail: {count} messages indexed")
    return count


def _gmail_incremental(db: sqlite_utils.Database, service, history_id: str) -> int:
    """Incremental sync using Gmail History API."""
    print(f"  Gmail: Incremental sync from historyId {history_id}...")
    changed_ids = set()
    page_token = None

    while True:
        result = service.users().history().list(
            userId="me",
            startHistoryId=history_id,
            historyTypes=["messageAdded", "messageDeleted", "labelAdded", "labelRemoved"],
            pageToken=page_token,
        ).execute()

        for record in result.get("history", []):
            for msg in record.get("messagesAdded", []):
                changed_ids.add(msg["message"]["id"])
            for msg in record.get("messagesDeleted", []):
                # Mark as deleted in cache
                try:
                    db["gmail_messages"].delete(msg["message"]["id"])
                except Exception:
                    pass
            for msg in record.get("labelsAdded", []):
                changed_ids.add(msg["message"]["id"])
            for msg in record.get("labelsRemoved", []):
                changed_ids.add(msg["message"]["id"])

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    # Fetch updated metadata for changed messages
    messages = []
    for msg_id in changed_ids:
        try:
            msg = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["From", "To", "Cc", "Subject", "Date"],
            ).execute()
            headers = {
                h["name"]: h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }
            messages.append({
                "message_id": msg["id"],
                "thread_id": msg.get("threadId"),
                "snippet": msg.get("snippet", ""),
                "sender": headers.get("From", ""),
                "recipients": headers.get("To", ""),
                "cc": headers.get("Cc", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "labels": json.dumps(msg.get("labelIds", [])),
                "size": msg.get("sizeEstimate", 0),
            })
        except Exception:
            continue

    if messages:
        db["gmail_messages"].upsert_all(messages, pk="message_id", alter=True)

    print(f"  Gmail: {len(changed_ids)} messages updated")
    return len(changed_ids)


# --- Calendar Sync ---


def sync_calendar(db: sqlite_utils.Database, creds: Credentials) -> int:
    """Sync Calendar events using syncToken for incremental updates."""
    service = build("calendar", "v3", credentials=creds)
    state = get_sync_state(db, "calendar")
    sync_token = state.get("sync_token")

    events = []
    page_token = None
    new_sync_token = None

    # Build base kwargs once — must stay consistent across all pages
    # Note: singleEvents=True is incompatible with syncToken, so we omit it
    base_kwargs: Dict[str, Any] = {
        "calendarId": "primary",
        "maxResults": 250,
    }
    if sync_token:
        base_kwargs["syncToken"] = sync_token
        print("  Calendar: Incremental sync...")
    else:
        print("  Calendar: Full sync (first run)...")
        base_kwargs["timeMin"] = "2020-01-01T00:00:00Z"

    try:
        while True:
            kwargs = dict(base_kwargs)
            if page_token:
                kwargs["pageToken"] = page_token

            result = service.events().list(**kwargs).execute()

            for event in result.get("items", []):
                if event.get("status") == "cancelled":
                    try:
                        db["calendar_events"].delete(event["id"])
                    except Exception:
                        pass
                    continue

                start = event.get("start", {})
                end = event.get("end", {})
                events.append({
                    "event_id": event["id"],
                    "summary": event.get("summary", ""),
                    "description": event.get("description", ""),
                    "location": event.get("location", ""),
                    "start_time": start.get("dateTime", start.get("date", "")),
                    "end_time": end.get("dateTime", end.get("date", "")),
                    "status": event.get("status", ""),
                    "attendees": json.dumps([
                        a.get("email") for a in event.get("attendees", [])
                    ]),
                    "html_link": event.get("htmlLink", ""),
                    "recurring_event_id": event.get("recurringEventId", ""),
                })

            page_token = result.get("nextPageToken")
            new_sync_token = result.get("nextSyncToken")

            if not page_token:
                break

    except Exception as e:
        if "410" in str(e):
            # Sync token expired, full resync
            print("  Calendar: Sync token expired, doing full resync...")
            if "calendar_events" in db.table_names():
                db["calendar_events"].drop()
            return sync_calendar(db, creds)
        raise

    if events:
        db["calendar_events"].upsert_all(events, pk="event_id", alter=True)

    _ensure_fts(db, "calendar_events", ["summary", "description", "location"])

    total = db["calendar_events"].count if "calendar_events" in db.table_names() else 0
    set_sync_state(db, "calendar", sync_token=new_sync_token, record_count=total)
    print(f"  Calendar: {total} events indexed")
    return len(events)


# --- Contacts Sync ---


def sync_contacts(db: sqlite_utils.Database, creds: Credentials) -> int:
    """Sync Contacts using People API syncToken for incremental updates."""
    service = build("people", "v1", credentials=creds)
    state = get_sync_state(db, "contacts")
    sync_token = state.get("sync_token")
    person_fields = "names,emailAddresses,phoneNumbers,organizations"

    contacts = []
    page_token = None

    try:
        while True:
            kwargs: Dict[str, Any] = {
                "resourceName": "people/me",
                "pageSize": 1000,
                "personFields": person_fields,
                "requestSyncToken": True,
            }
            if sync_token and not page_token:
                kwargs["syncToken"] = sync_token
                print("  Contacts: Incremental sync...")
            elif not page_token:
                print("  Contacts: Full sync (first run)...")
                kwargs["sortOrder"] = "LAST_NAME_ASCENDING"
            if page_token:
                kwargs["pageToken"] = page_token

            result = service.people().connections().list(**kwargs).execute()

            for person in result.get("connections", []):
                # Check if deleted
                metadata = person.get("metadata", {})
                if metadata.get("deleted"):
                    resource_name = person.get("resourceName")
                    if resource_name:
                        try:
                            db["contacts"].delete(resource_name)
                        except Exception:
                            pass
                    continue

                names = person.get("names", [])
                emails = person.get("emailAddresses", [])
                phones = person.get("phoneNumbers", [])
                orgs = person.get("organizations", [])

                contacts.append({
                    "resource_name": person.get("resourceName"),
                    "name": names[0].get("displayName", "") if names else "",
                    "given_name": names[0].get("givenName", "") if names else "",
                    "family_name": names[0].get("familyName", "") if names else "",
                    "email": emails[0].get("value", "") if emails else "",
                    "phone": phones[0].get("value", "") if phones else "",
                    "organization": orgs[0].get("name", "") if orgs else "",
                    "title": orgs[0].get("title", "") if orgs else "",
                })

            page_token = result.get("nextPageToken")
            new_sync_token = result.get("nextSyncToken")

            if not page_token:
                break

    except Exception as e:
        if "EXPIRED_SYNC_TOKEN" in str(e) or "syncToken" in str(e).lower():
            print("  Contacts: Sync token expired, doing full resync...")
            if "contacts" in db.table_names():
                db["contacts"].drop()
            return sync_contacts(db, creds)
        raise

    if contacts:
        db["contacts"].upsert_all(contacts, pk="resource_name", alter=True)

    _ensure_fts(db, "contacts", ["name", "email", "organization", "title"])

    total = db["contacts"].count if "contacts" in db.table_names() else 0
    set_sync_state(db, "contacts", sync_token=new_sync_token, record_count=total)
    print(f"  Contacts: {total} contacts indexed")
    return len(contacts)


# --- Drive Sync ---


def sync_drive(db: sqlite_utils.Database, creds: Credentials) -> int:
    """Sync Drive file metadata using the Changes API for incremental updates."""
    service = build("drive", "v3", credentials=creds)
    state = get_sync_state(db, "drive")
    start_page_token = state.get("sync_token")

    file_fields = "id,name,mimeType,size,modifiedTime,parents,trashed,shared,owners"

    if not start_page_token:
        # Full sync
        print("  Drive: Full sync (first run)...")
        count = _drive_full(db, service, file_fields)

        # Get start page token for future incremental syncs
        token_result = service.changes().getStartPageToken().execute()
        new_token = token_result.get("startPageToken")
    else:
        # Incremental sync via Changes API
        print("  Drive: Incremental sync...")
        count, new_token = _drive_incremental(db, service, start_page_token, file_fields)

    total = db["drive_files"].count if "drive_files" in db.table_names() else 0
    set_sync_state(db, "drive", sync_token=new_token, record_count=total)
    print(f"  Drive: {total} files indexed")
    return count


def _drive_full(db: sqlite_utils.Database, service, file_fields: str) -> int:
    """Full Drive file listing."""
    files = []
    page_token = None

    while True:
        result = service.files().list(
            pageSize=1000,
            fields=f"nextPageToken,files({file_fields})",
            q="trashed = false",
            orderBy="modifiedTime desc",
            pageToken=page_token,
        ).execute()

        for f in result.get("files", []):
            owners = f.get("owners", [])
            files.append({
                "file_id": f["id"],
                "name": f.get("name", ""),
                "mime_type": f.get("mimeType", ""),
                "size": f.get("size", ""),
                "modified_time": f.get("modifiedTime", ""),
                "parents": json.dumps(f.get("parents", [])),
                "trashed": f.get("trashed", False),
                "shared": f.get("shared", False),
                "owner": owners[0].get("emailAddress", "") if owners else "",
                "is_folder": f.get("mimeType") == "application/vnd.google-apps.folder",
            })

        if len(files) >= 500:
            db["drive_files"].upsert_all(files, pk="file_id", alter=True)
            files = []

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    if files:
        db["drive_files"].upsert_all(files, pk="file_id", alter=True)

    _ensure_fts(db, "drive_files", ["name", "owner"])
    return db["drive_files"].count


def _drive_incremental(
    db: sqlite_utils.Database, service, page_token: str, file_fields: str
) -> tuple:
    """Incremental Drive sync using Changes API."""
    changed = 0
    new_token = page_token

    while True:
        result = service.changes().list(
            pageToken=page_token,
            fields=f"nextPageToken,newStartPageToken,changes(fileId,removed,file({file_fields}))",
            pageSize=1000,
        ).execute()

        for change in result.get("changes", []):
            file_id = change.get("fileId")
            if change.get("removed"):
                try:
                    db["drive_files"].delete(file_id)
                except Exception:
                    pass
            else:
                f = change.get("file", {})
                if f:
                    owners = f.get("owners", [])
                    db["drive_files"].upsert(
                        {
                            "file_id": f.get("id", file_id),
                            "name": f.get("name", ""),
                            "mime_type": f.get("mimeType", ""),
                            "size": f.get("size", ""),
                            "modified_time": f.get("modifiedTime", ""),
                            "parents": json.dumps(f.get("parents", [])),
                            "trashed": f.get("trashed", False),
                            "shared": f.get("shared", False),
                            "owner": owners[0].get("emailAddress", "") if owners else "",
                            "is_folder": f.get("mimeType") == "application/vnd.google-apps.folder",
                        },
                        pk="file_id",
                        alter=True,
                    )
            changed += 1

        page_token = result.get("nextPageToken")
        if result.get("newStartPageToken"):
            new_token = result["newStartPageToken"]

        if not page_token:
            break

    print(f"  Drive: {changed} changes processed")
    return changed, new_token


# --- Photos Sync ---


def sync_photos(db: sqlite_utils.Database, creds: Credentials) -> int:
    """Sync Photos metadata. No change detection API — re-lists by creation time."""
    print("  Photos: Syncing media items...")

    # Refresh token if needed
    if creds.expired and getattr(creds, "refresh_token", None):
        creds.refresh(Request())

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    })

    state = get_sync_state(db, "photos")
    last_sync = state.get("last_sync")

    items = []
    page_token = None

    while True:
        params: Dict[str, Any] = {"pageSize": 100}
        if page_token:
            params["pageToken"] = page_token

        resp = session.get(f"{PHOTOS_API_BASE}/mediaItems", params=params)
        if resp.status_code != 200:
            print(f"  Photos: API error {resp.status_code}: {resp.text[:200]}")
            break

        result = resp.json()

        for item in result.get("mediaItems", []):
            meta = item.get("mediaMetadata", {})
            items.append({
                "item_id": item["id"],
                "filename": item.get("filename", ""),
                "mime_type": item.get("mimeType", ""),
                "description": item.get("description", ""),
                "creation_time": meta.get("creationTime", ""),
                "width": meta.get("width", ""),
                "height": meta.get("height", ""),
                "is_video": "video" in meta,
            })

        if len(items) >= 500:
            db["photos_media"].upsert_all(items, pk="item_id", alter=True)
            items = []

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    if items:
        db["photos_media"].upsert_all(items, pk="item_id", alter=True)

    _ensure_fts(db, "photos_media", ["filename", "description"])

    total = db["photos_media"].count if "photos_media" in db.table_names() else 0
    set_sync_state(db, "photos", record_count=total)
    print(f"  Photos: {total} media items indexed")
    return total


# --- Full-Text Search ---


def _ensure_fts(db: sqlite_utils.Database, table: str, columns: List[str]) -> None:
    """Enable FTS5 on a table if not already enabled."""
    fts_table = f"{table}_fts"
    if fts_table not in db.table_names():
        try:
            db[table].enable_fts(columns, create_triggers=True)
        except Exception:
            pass  # FTS already set up or table doesn't exist yet


def search_cache(
    db: sqlite_utils.Database, query: str, service: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Full-text search across cached data."""
    results = []
    tables = {
        "gmail": "gmail_messages",
        "calendar": "calendar_events",
        "contacts": "contacts",
        "drive": "drive_files",
        "photos": "photos_media",
    }

    targets = {service: tables[service]} if service and service in tables else tables

    for svc, table in targets.items():
        fts_table = f"{table}_fts"
        if fts_table in db.table_names():
            try:
                for row in db[table].search(query, limit=20):
                    row["_service"] = svc
                    results.append(dict(row))
            except Exception:
                pass

    return results


# --- CLI ---


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Google Workspace Cache — Local SQLite index"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # sync
    sp = subparsers.add_parser("sync", help="Sync metadata from Google APIs")
    sp.add_argument(
        "--service",
        choices=ALL_SERVICES,
        help="Sync a specific service (default: gmail, calendar, contacts, drive)",
    )

    # search
    sp = subparsers.add_parser("search", help="Full-text search across cached data")
    sp.add_argument("query", help="Search query")
    sp.add_argument(
        "--service",
        choices=ALL_SERVICES,
        help="Search within a specific service",
    )

    # last-sync
    sp = subparsers.add_parser("last-sync", help="Show last sync time (for use in prompts)")
    sp.add_argument(
        "--service",
        choices=ALL_SERVICES,
        help="Check a specific service",
    )

    # status
    subparsers.add_parser("status", help="Show cache status")

    # clear
    subparsers.add_parser("clear", help="Delete the cache database")

    args = parser.parse_args()

    if args.command == "sync":
        try:
            creds = get_credentials()
        except NETWORK_ERRORS as e:
            print(f"Network unavailable, skipping sync: {e}")
            sys.exit(0)

        db = get_db()
        services_to_sync = [args.service] if args.service else SERVICES

        sync_map = {
            "gmail": sync_gmail,
            "calendar": sync_calendar,
            "contacts": sync_contacts,
            "drive": sync_drive,
            "photos": sync_photos,
        }

        print(f"Syncing: {', '.join(services_to_sync)}")
        print()

        errors = 0
        for svc in services_to_sync:
            try:
                sync_map[svc](db, creds)
            except NETWORK_ERRORS as e:
                print(f"  {svc.capitalize()}: Network error, skipping — {type(e).__name__}")
                errors += 1
            except Exception as e:
                print(f"  {svc.capitalize()}: Error — {e}")
                errors += 1
            print()

        print("Sync complete.")
        # Exit 0 even on partial failures so systemd doesn't mark as failed
        sys.exit(0)

    elif args.command == "search":
        db = get_db()
        results = search_cache(db, args.query, service=args.service)
        if results:
            print_json(results)
        else:
            print_json({"results": [], "message": "No matches found"})

    elif args.command == "last-sync":
        if not DB_PATH.exists():
            print("No cache. Run: uv run scripts/cache.py sync")
        else:
            db = get_db()
            targets = [args.service] if args.service else SERVICES
            for svc in targets:
                state = get_sync_state(db, svc)
                last = state.get("last_sync")
                count = state.get("record_count", 0)
                if last:
                    # Parse and show relative time
                    try:
                        dt = datetime.fromisoformat(last)
                        delta = datetime.now(timezone.utc) - dt
                        mins = int(delta.total_seconds() / 60)
                        if mins < 1:
                            ago = "just now"
                        elif mins < 60:
                            ago = f"{mins}m ago"
                        elif mins < 1440:
                            ago = f"{mins // 60}h ago"
                        else:
                            ago = f"{mins // 1440}d ago"
                    except Exception:
                        ago = last
                    print(f"  {svc}: {count} records, synced {ago}")
                else:
                    print(f"  {svc}: never synced")

    elif args.command == "status":
        db = get_db()
        status = {}
        for svc in SERVICES:
            state = get_sync_state(db, svc)
            status[svc] = {
                "last_sync": state.get("last_sync"),
                "record_count": state.get("record_count", 0),
                "has_sync_token": bool(state.get("sync_token")),
            }
        status["database"] = str(DB_PATH)
        status["database_exists"] = DB_PATH.exists()
        if DB_PATH.exists():
            status["database_size_mb"] = round(DB_PATH.stat().st_size / 1048576, 2)
        print_json(status)

    elif args.command == "clear":
        if DB_PATH.exists():
            DB_PATH.unlink()
            # Also remove FTS shadow tables
            for suffix in ["-wal", "-shm"]:
                p = DB_PATH.parent / (DB_PATH.name + suffix)
                if p.exists():
                    p.unlink()
            print(f"Cache cleared: {DB_PATH}")
        else:
            print("No cache database found.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
