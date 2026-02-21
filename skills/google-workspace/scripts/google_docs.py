#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Docs Skill - Content manipulation for AI agents.

Commands:
  verify         Check authentication status
  setup          Run interactive OAuth flow
  read           Get text content from a document
  create         Create a new document
  append         Append text to the end of a document
  replace        Replace all instances of text in a document
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
        env_var="DOCS_CREDENTIALS_DIR",
        legacy_dir_name=".docs_credentials"
    )

CREDENTIALS_DIR = _find_credentials_dir()
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/documents.readonly"],
    "full": ["https://www.googleapis.com/auth/documents"],
}
DEFAULT_SCOPE = "full"


class DocsTool:
    """Docs wrapper for AI agents."""

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
            service_name="Docs"
        )

        if creds and creds.valid:
            self.service = build("docs", "v1", credentials=creds)

    def setup_interactive(self) -> None:
        print("🔵 Starting Interactive Setup for Google Docs...")
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

            self.service = build("docs", "v1", credentials=creds)
            print(f"✅ Authentication successful! Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")

    def ensure_service(self) -> None:
        if not self.service:
            raise RuntimeError(
                "Docs API not authenticated. Run 'setup' command or configure ADC."
            )

    # ────────────────────────────────────────────────────────────
    # Read
    # ────────────────────────────────────────────────────────────

    def read_document(self, document_id: str) -> Dict[str, Any]:
        """Read text from a document."""
        self.ensure_service()
        doc = self.service.documents().get(documentId=document_id).execute()
        
        text_content = ""
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for p_element in element.get("paragraph", {}).get("elements", []):
                    if "textRun" in p_element:
                        text_content += p_element.get("textRun", {}).get("content", "")

        return {
            "documentId": document_id,
            "title": doc.get("title"),
            "text": text_content
        }

    # ────────────────────────────────────────────────────────────
    # Create
    # ────────────────────────────────────────────────────────────

    def create_document(self, title: str) -> Dict[str, Any]:
        """Create a new document."""
        self.ensure_service()
        doc = self.service.documents().create(body={"title": title}).execute()
        return {
            "documentId": doc.get("documentId"),
            "title": doc.get("title")
        }

    # ────────────────────────────────────────────────────────────
    # Update
    # ────────────────────────────────────────────────────────────

    def append_text(self, document_id: str, text: str) -> Dict[str, Any]:
        """Append text to the end of a document."""
        self.ensure_service()
        
        # Get the document to find the end index
        doc = self.service.documents().get(documentId=document_id).execute()
        
        # The content length is the end index minus 1 (the closing newline)
        content_length = doc.get("body", {}).get("content", [])[-1].get("endIndex", 1) - 1
        
        # Determine the insertion index. If the document is totally empty, it's 1.
        insert_index = max(1, content_length)

        requests = [
            {
                "insertText": {
                    "location": {
                        "index": insert_index,
                    },
                    "text": text
                }
            }
        ]

        result = self.service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        return {"documentId": document_id, "replies": result.get("replies", [])}

    def replace_text(self, document_id: str, old_text: str, new_text: str) -> Dict[str, Any]:
        """Replace all instances of old_text with new_text."""
        self.ensure_service()
        requests = [
            {
                "replaceAllText": {
                    "containsText": {
                        "text": old_text,
                        "matchCase": True,
                    },
                    "replaceText": new_text,
                }
            }
        ]

        result = self.service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        return {"documentId": document_id, "replies": result.get("replies", [])}


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Google Docs AI Skill")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # read
    sp = subparsers.add_parser("read", help="Get text content from a document")
    sp.add_argument("--id", required=True, help="Document ID")

    # create
    sp = subparparsers.add_parser("create", help="Create a new document")
    sp.add_argument("--title", required=True, help="Document title")

    # append
    sp = subparsers.add_parser("append", help="Append text to a document")
    sp.add_argument("--id", required=True, help="Document ID")
    sp.add_argument("--text", required=True, help="Text to append")

    # replace
    sp = subparsers.add_parser("replace", help="Replace all instances of text")
    sp.add_argument("--id", required=True, help="Document ID")
    sp.add_argument("--old", required=True, help="Text to replace")
    sp.add_argument("--new", required=True, help="New text")

    args = parser.parse_args()

    if args.command == "setup":
        tool = DocsTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = DocsTool()

        if args.command == "verify":
            tool.ensure_service()
            workspace_lib.print_json({"status": "authenticated", "message": "Docs API ready"})

        elif args.command == "read":
            doc = tool.read_document(args.id)
            workspace_lib.print_json(doc)

        elif args.command == "create":
            doc = tool.create_document(args.title)
            workspace_lib.print_json({"status": "created", "document": doc})

        elif args.command == "append":
            result = tool.append_text(args.id, args.text)
            workspace_lib.print_json({"status": "appended", "result": result})

        elif args.command == "replace":
            result = tool.replace_text(args.id, args.old, args.new)
            workspace_lib.print_json({"status": "replaced", "result": result})

        else:
            parser.print_help()

    except Exception as e:
        workspace_lib.print_json({"status": "error", "message": str(e), "type": type(e).__name__})

if __name__ == "__main__":
    main()
