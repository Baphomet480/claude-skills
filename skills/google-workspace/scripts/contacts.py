#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Contacts Skill - Full CRUD for AI agents.

Commands:
  verify         Check authentication status
  setup          Run interactive OAuth flow
  search         Search contacts by name, email, or phone
  list           List all contacts (paginated)
  get            Get a single contact by resource name
  create         Create a new contact
  update         Update an existing contact
  delete         Delete a contact
"""

import argparse
import json
import os
import sys
from datetime import datetime
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
        env_var="CONTACTS_CREDENTIALS_DIR",
        legacy_dir_name=".contacts_credentials"
    )

CREDENTIALS_DIR = _find_credentials_dir()
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/contacts.readonly"],
    "full": ["https://www.googleapis.com/auth/contacts"],
}
DEFAULT_SCOPE = "full"

# Fields we request from the People API
PERSON_FIELDS = "names,emailAddresses,phoneNumbers,organizations,addresses,biographies,urls,birthdays"


class ContactsTool:
    """Full CRUD Contacts wrapper for AI agents."""

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
            service_name="Contacts"
        )

        if creds and creds.valid:
            self.service = build("people", "v1", credentials=creds)

    def setup_interactive(self) -> None:
        print("🔵 Starting Interactive Setup for Google Contacts...")
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

            self.service = build("people", "v1", credentials=creds)
            print(f"✅ Authentication successful! Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")

    def ensure_service(self) -> None:
        if not self.service:
            raise workspace_lib.AuthError(
                "Contacts API not authenticated.",
                fix="Run: uv run scripts/preflight.py  (to diagnose), then: uv run scripts/setup_workspace.py  (to authenticate)",
            )

    # ────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────

    @staticmethod
    def _safe_first(items: List, key: str, default: str = "") -> str:
        if not items:
            return default
        return items[0].get(key, default)

    def _normalize_person(self, person: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a People API person resource into a flat dict."""
        names = person.get("names", [])
        emails = person.get("emailAddresses", [])
        phones = person.get("phoneNumbers", [])
        orgs = person.get("organizations", [])
        addrs = person.get("addresses", [])
        bios = person.get("biographies", [])
        urls = person.get("urls", [])
        bdays = person.get("birthdays", [])

        return {
            "resourceName": person.get("resourceName"),
            "etag": person.get("etag"),
            "name": self._safe_first(names, "displayName", "Unknown"),
            "givenName": self._safe_first(names, "givenName"),
            "familyName": self._safe_first(names, "familyName"),
            "emails": [{"value": e.get("value"), "type": e.get("type")} for e in emails],
            "phones": [{"value": p.get("value"), "type": p.get("type")} for p in phones],
            "organizations": [
                {"name": o.get("name"), "title": o.get("title"), "department": o.get("department")}
                for o in orgs
            ],
            "addresses": [
                {"formatted": a.get("formattedValue"), "type": a.get("type")}
                for a in addrs
            ],
            "biography": self._safe_first(bios, "value"),
            "urls": [{"value": u.get("value"), "type": u.get("type")} for u in urls],
            "birthday": bdays[0].get("date") if bdays else None,
        }

    # ────────────────────────────────────────────────────────────
    # CRUD
    # ────────────────────────────────────────────────────────────

    def search_contacts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search contacts by name, email, or phone."""
        self.ensure_service()
        results = self.service.people().searchContacts(
            query=query,
            readMask=PERSON_FIELDS,
            pageSize=limit,
        ).execute()

        return [
            self._normalize_person(r.get("person", {}))
            for r in results.get("results", [])
        ]

    def list_contacts(self, limit: int = 100, page_token: Optional[str] = None) -> Dict[str, Any]:
        """List all contacts (paginated)."""
        self.ensure_service()
        result = self.service.people().connections().list(
            resourceName="people/me",
            pageSize=min(limit, 1000),
            personFields=PERSON_FIELDS,
            sortOrder="LAST_NAME_ASCENDING",
            pageToken=page_token or "",
        ).execute()

        contacts = [
            self._normalize_person(p)
            for p in result.get("connections", [])
        ]

        return {
            "contacts": contacts,
            "totalItems": result.get("totalItems", len(contacts)),
            "nextPageToken": result.get("nextPageToken"),
        }

    def get_contact(self, resource_name: str) -> Dict[str, Any]:
        """Get a single contact by resource name (e.g. 'people/c12345')."""
        self.ensure_service()
        person = self.service.people().get(
            resourceName=resource_name,
            personFields=PERSON_FIELDS,
        ).execute()
        return self._normalize_person(person)

    def create_contact(
        self,
        given_name: str,
        family_name: str = "",
        email: str = "",
        phone: str = "",
        organization: str = "",
        title: str = "",
        notes: str = "",
    ) -> Dict[str, Any]:
        """Create a new contact."""
        self.ensure_service()

        body: Dict[str, Any] = {
            "names": [{"givenName": given_name, "familyName": family_name}],
        }
        if email:
            body["emailAddresses"] = [{"value": email}]
        if phone:
            body["phoneNumbers"] = [{"value": phone}]
        if organization or title:
            body["organizations"] = [{"name": organization, "title": title}]
        if notes:
            body["biographies"] = [{"value": notes, "contentType": "TEXT_PLAIN"}]

        contact = self.service.people().createContact(body=body).execute()
        return self._normalize_person(contact)

    def update_contact(
        self,
        resource_name: str,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        organization: Optional[str] = None,
        title: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing contact. Fetches current etag, applies changes."""
        self.ensure_service()

        # Fetch current state to get etag and merge
        current = self.service.people().get(
            resourceName=resource_name,
            personFields=PERSON_FIELDS,
        ).execute()

        # Build update mask and body
        update_fields: List[str] = []
        body: Dict[str, Any] = {"etag": current["etag"]}

        if given_name is not None or family_name is not None:
            update_fields.append("names")
            current_names = current.get("names", [{}])
            name_entry = current_names[0] if current_names else {}
            if given_name is not None:
                name_entry["givenName"] = given_name
            if family_name is not None:
                name_entry["familyName"] = family_name
            body["names"] = [name_entry]

        if email is not None:
            update_fields.append("emailAddresses")
            body["emailAddresses"] = [{"value": email}]

        if phone is not None:
            update_fields.append("phoneNumbers")
            body["phoneNumbers"] = [{"value": phone}]

        if organization is not None or title is not None:
            update_fields.append("organizations")
            org_entry: Dict[str, str] = {}
            if organization is not None:
                org_entry["name"] = organization
            if title is not None:
                org_entry["title"] = title
            body["organizations"] = [org_entry]

        if notes is not None:
            update_fields.append("biographies")
            body["biographies"] = [{"value": notes, "contentType": "TEXT_PLAIN"}]

        if not update_fields:
            raise ValueError("No fields provided to update.")

        result = self.service.people().updateContact(
            resourceName=resource_name,
            body=body,
            updatePersonFields=",".join(update_fields),
        ).execute()
        return self._normalize_person(result)

    def delete_contact(self, resource_name: str) -> Dict[str, str]:
        """Delete a contact by resource name."""
        self.ensure_service()
        self.service.people().deleteContact(resourceName=resource_name).execute()
        return {"status": "deleted", "resourceName": resource_name}


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Contacts AI Skill — Full CRUD")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # search
    sp = subparsers.add_parser("search", help="Search contacts")
    sp.add_argument("--query", "-q", required=True, help="Name, email, or phone to search")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    # list
    sp = subparsers.add_parser("list", help="List all contacts")
    sp.add_argument("--limit", type=int, default=100, help="Max results per page")
    sp.add_argument("--page-token", help="Page token for pagination")

    # get
    sp = subparsers.add_parser("get", help="Get a contact by resource name")
    sp.add_argument("--id", required=True, help="Resource name (e.g. 'people/c12345')")

    # create
    sp = subparsers.add_parser("create", help="Create a new contact")
    sp.add_argument("--first", required=True, help="First name")
    sp.add_argument("--last", default="", help="Last name")
    sp.add_argument("--email", default="", help="Email address")
    sp.add_argument("--phone", default="", help="Phone number")
    sp.add_argument("--org", default="", help="Organization name")
    sp.add_argument("--title", default="", help="Job title")
    sp.add_argument("--notes", default="", help="Notes / biography")

    # update
    sp = subparsers.add_parser("update", help="Update an existing contact")
    sp.add_argument("--id", required=True, help="Resource name (e.g. 'people/c12345')")
    sp.add_argument("--first", help="New first name")
    sp.add_argument("--last", help="New last name")
    sp.add_argument("--email", help="New email address")
    sp.add_argument("--phone", help="New phone number")
    sp.add_argument("--org", help="New organization name")
    sp.add_argument("--title", help="New job title")
    sp.add_argument("--notes", help="New notes / biography")

    # delete
    sp = subparsers.add_parser("delete", help="Delete a contact")
    sp.add_argument("--id", required=True, help="Resource name (e.g. 'people/c12345')")

    args = parser.parse_args()

    if args.command == "setup":
        tool = ContactsTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = ContactsTool()

        if args.command == "verify":
            tool.ensure_service()
            tool.service.people().connections().list(
                resourceName="people/me",
                pageSize=1,
                personFields="names",
            ).execute()
            workspace_lib.print_json({"status": "authenticated", "message": "Contacts API ready"})

        elif args.command == "search":
            contacts = tool.search_contacts(args.query, limit=args.limit)
            workspace_lib.print_json(contacts)

        elif args.command == "list":
            result = tool.list_contacts(limit=args.limit, page_token=args.page_token)
            workspace_lib.print_json(result)

        elif args.command == "get":
            contact = tool.get_contact(args.id)
            workspace_lib.print_json(contact)

        elif args.command == "create":
            contact = tool.create_contact(
                given_name=args.first,
                family_name=args.last,
                email=args.email,
                phone=args.phone,
                organization=args.org,
                title=args.title,
                notes=args.notes,
            )
            workspace_lib.print_json({"status": "created", "contact": contact})

        elif args.command == "update":
            contact = tool.update_contact(
                resource_name=args.id,
                given_name=args.first,
                family_name=args.last,
                email=args.email,
                phone=args.phone,
                organization=args.org,
                title=args.title,
                notes=args.notes,
            )
            workspace_lib.print_json({"status": "updated", "contact": contact})

        elif args.command == "delete":
            result = tool.delete_contact(args.id)
            workspace_lib.print_json(result)

        else:
            parser.print_help()

    except Exception as e:
        workspace_lib.print_json({"status": "error", "message": str(e), "type": type(e).__name__})


if __name__ == "__main__":
    main()
