#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Contacts Skill - AI-powered Contacts interactions.

Features:
- Search for contacts
- Create new contacts
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

# --- Configuration ---

CREDENTIALS_DIR = Path(os.environ.get("CONTACTS_CREDENTIALS_DIR", Path.home() / ".contacts_credentials"))
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/contacts.readonly"],
    "full": ["https://www.googleapis.com/auth/contacts"],
}
DEFAULT_SCOPE = "full"

class ContactsTool:
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
        print(f"🔵 Starting Interactive Setup for Google Contacts...")
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

        # 3. Fallback to Client Secrets (Auto-UI for existing refresh token)
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
            
            if not creds and CLIENT_SECRETS_FILE.exists():
                pass

        if creds:
             self.service = build("people", "v1", credentials=creds)

    def ensure_service(self):
        if not self.service:
            raise RuntimeError(
                f"Contacts API not authenticated. Please run 'uv run contacts.py setup'."
            )

    def _safe_first(self, items: List, key: str, default: str = "") -> str:
        """Safely get a value from the first item of a list, handling missing keys and empty lists."""
        if not items:
            return default
        return items[0].get(key, default)

    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts."""
        self.ensure_service()
        results = self.service.people().searchContacts(
            query=query,
            readMask="names,emailAddresses,phoneNumbers"
        ).execute()
        
        normalized = []
        for result in results.get("results", []):
            person = result.get("person", {})
            name = self._safe_first(person.get("names", []), "displayName", "Unknown")
            email = self._safe_first(person.get("emailAddresses", []), "value")
            phone = self._safe_first(person.get("phoneNumbers", []), "value")
            resource_name = person.get("resourceName")
            
            normalized.append({
                "name": name,
                "email": email,
                "phone": phone,
                "resourceName": resource_name
            })
            
        return normalized

    def create_contact(self, given_name: str, family_name: str = "", email: str = "", phone: str = "") -> Dict[str, Any]:
        """Create a new contact."""
        self.ensure_service()
        
        body = {
            "names": [{"givenName": given_name, "familyName": family_name}],
        }
        if email:
            body["emailAddresses"] = [{"value": email}]
        if phone:
            body["phoneNumbers"] = [{"value": phone}]

        contact = self.service.people().createContact(body=body).execute()
        return contact

def print_json(data: Any):
    print(json.dumps(data, indent=2, default=str))

def main():
    parser = argparse.ArgumentParser(description="Google Contacts AI Skill")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # search
    search_parser = subparsers.add_parser("search", help="Search contacts")
    search_parser.add_argument("--query", "-q", required=True, help="Name or email to search")

    # create
    create_parser = subparsers.add_parser("create", help="Create a contact")
    create_parser.add_argument("--first", required=True, help="First Name")
    create_parser.add_argument("--last", default="", help="Last Name")
    create_parser.add_argument("--email", default="", help="Email Address")
    create_parser.add_argument("--phone", default="", help="Phone Number")

    args = parser.parse_args()

    if args.command == "setup":
        tool = ContactsTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = ContactsTool()
        
        if args.command == "verify":
            tool.ensure_service()
            # Real API check: list connections to validate token usability
            tool.service.people().connections().list(
                resourceName="people/me",
                pageSize=1,
                personFields="names"
            ).execute()
            print_json({"status": "authenticated", "message": "Contacts API ready"})

        elif args.command == "search":
            contacts = tool.search_contacts(args.query)
            print_json(contacts)

        elif args.command == "create":
            contact = tool.create_contact(args.first, args.last, args.email, args.phone)
            print_json({"status": "created", "contact": contact})
            
        else:
            parser.print_help()

    except Exception as e:
        print_json({"status": "error", "message": str(e), "type": type(e).__name__})

if __name__ == "__main__":
    main()
