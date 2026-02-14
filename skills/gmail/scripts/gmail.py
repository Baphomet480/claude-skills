#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Gmail Skill - AI-powered Gmail interactions.

Features:
- Search emails using full Gmail query syntax
- Read email details and attachments
- Create DRAFTS (safer than direct sending)
- Manage labels (basic listing)
"""

import argparse
import base64
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

# --- Configuration ---

# Allow overriding the credentials directory via environment variable
CREDENTIALS_DIR = Path(os.environ.get("GMAIL_CREDENTIALS_DIR", Path.home() / ".gmail_credentials"))
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

# Scopes
SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/gmail.readonly"],
    "modify": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ],
    "full": ["https://mail.google.com/"],
}
DEFAULT_SCOPE = "modify"  # Default to modify to allow draft creation/read modification


class GmailTool:
    """
    A class-based wrapper for Gmail API operations tailored for AI agents.
    """

    def __init__(self):
        self.service: Optional[Resource] = None
        self._authenticate()

    def _get_current_scope(self) -> str:
        """Get currently configured scope."""
        if SCOPE_FILE.exists():
            return SCOPE_FILE.read_text().strip()
        return DEFAULT_SCOPE

    def _authenticate(self) -> None:
        """Authenticate with Gmail API and store service object."""
        creds = None
        scope = self._get_current_scope()
        scopes = SCOPES_MAP.get(scope, SCOPES_MAP[DEFAULT_SCOPE])

        # 1. Try Local Token (JSON)
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)
            except Exception:
                pass

        # 2. Try ADC (gcloud auth application-default login)
        if not creds or not creds.valid:
            try:
                creds, project_id = google.auth.default(scopes=scopes)
                if (
                    creds
                    and creds.expired
                    and getattr(creds, "refresh_token", None)
                ):
                    creds.refresh(Request())
            except Exception:
                 # ADC failed or not configured
                 creds = None

        # 3. Fallback to Client Secrets (credentials.json)
        if not creds or not creds.valid:
            if (
                creds
                and creds.expired
                and getattr(creds, "refresh_token", None)
            ):
                try:
                    creds.refresh(Request())
                    # Save refreshed token
                    if TOKEN_FILE.exists():
                        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
                        TOKEN_FILE.write_text(creds.to_json())
                except Exception:
                    # Token invalid/revoked, delete and re-auth
                    if TOKEN_FILE.exists():
                        TOKEN_FILE.unlink()
                    creds = None

            if not creds:
                if not CLIENT_SECRETS_FILE.exists():
                    print(f"Error: Credentials file not found at {CLIENT_SECRETS_FILE}")
                    print("To fix, either:")
                    print("1. Run: gcloud auth application-default login --scopes https://www.googleapis.com/auth/gmail.modify")
                    print("2. OR download credentials.json to that location.")
                    return

                print(f"Starting authentication flow using {CLIENT_SECRETS_FILE}...")
                flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), scopes)
                creds = flow.run_local_server(port=0)
                
                # Save token as JSON
                CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
                TOKEN_FILE.write_text(creds.to_json())

        if creds:
             self.service = build("gmail", "v1", credentials=creds)

    def ensure_service(self):
        """Raises exception if service is not available."""
        if not self.service:
            raise RuntimeError(
                f"Gmail API not authenticated. Please ensure '{CLIENT_SECRETS_FILE}' exists "
                "and run 'python3 gmail.py setup'."
            )

    def get_profile(self) -> Dict[str, Any]:
        """Get the authenticated user's profile."""
        self.ensure_service()
        return self.service.users().getProfile(userId="me").execute()

    def list_labels(self) -> List[Dict[str, str]]:
        """List available labels."""
        self.ensure_service()
        results = self.service.users().labels().list(userId="me").execute()
        return results.get("labels", [])

    def create_draft(self, to_addr: str, subject: str, body: str, cc_addr: Optional[str] = None) -> Dict[str, Any]:
        """Create a draft email."""
        self.ensure_service()

        message = MIMEText(body)
        message["to"] = to_addr
        message["from"] = "me"
        message["subject"] = subject
        if cc_addr:
            message["cc"] = cc_addr

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        body_payload = {"message": {"raw": raw_message}}

        draft = self.service.users().drafts().create(userId="me", body=body_payload).execute()
        return draft

    def search_messages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search messages."""
        self.ensure_service()
        results = self.service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
        messages = results.get("messages", [])
        
        detailed_messages = []
        for msg in messages:
            try:
                details = self._get_message_details(msg["id"])
                detailed_messages.append(details)
            except Exception:
                # Skip individual failures in batch
                continue
        
        return detailed_messages

    def _get_message_details(self, msg_id: str) -> Dict[str, Any]:
        """Fetch full message details."""
        # Using format='full' to get body snippet and payload
        msg = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        
        return {
            "id": msg_id,
            "threadId": msg.get("threadId"),
            "snippet": msg.get("snippet"),
            "from": headers.get("From"),
            "to": headers.get("To"),
            "subject": headers.get("Subject"),
            "date": headers.get("Date"),
            "internalDate": msg.get("internalDate"),  # timestamp in ms
            "labels": msg.get("labelIds", []),
        }

def print_json(data: Any):
    """Refined JSON printer."""
    print(json.dumps(data, indent=2, default=str))

def main():
    parser = argparse.ArgumentParser(description="Gmail AI Skill")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status and print profile")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # search
    search_parser = subparsers.add_parser("search", help="Search emails")
    search_parser.add_argument("--query", "-q", required=True, help="Gmail query string (e.g. 'is:unread from:x')")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # draft
    draft_parser = subparsers.add_parser("draft", help="Create a draft email")
    draft_parser.add_argument("--to", required=True, help="Recipient email")
    draft_parser.add_argument("--subject", required=True, help="Subject line")
    draft_parser.add_argument("--body", required=True, help="Email body text")
    draft_parser.add_argument("--cc", help="CC recipient email")

    # labels
    subparsers.add_parser("labels", help="List all labels")

    args = parser.parse_args()
    
    # Handle 'setup' explicitly to ensure flow runs if needed
    if args.command == "setup":
        tool = GmailTool()
        if tool.service:
            print_json({"status": "success", "message": "Authenticated successfully", "profile": tool.get_profile()})
        else:
            print_json({"status": "error", "message": "Authentication failed or cancelled"})
        return

    # Use tool for other commands
    try:
        tool = GmailTool()
        
        if args.command == "verify":
            print_json({"status": "authenticated", "profile": tool.get_profile()})

        elif args.command == "search":
            results = tool.search_messages(args.query, args.limit)
            print_json(results)

        elif args.command == "draft":
            draft = tool.create_draft(args.to, args.subject, args.body, args.cc)
            print_json({"status": "created", "draft": draft})

        elif args.command == "labels":
            labels = tool.list_labels()
            print_json(labels)
            
        else:
            parser.print_help()

    except Exception as e:
        print_json({"status": "error", "message": str(e), "type": type(e).__name__})

if __name__ == "__main__":
    main()
