#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Gmail Skill - Full CRUD + Reply/Forward for AI agents.

Commands:
  verify         Check authentication status
  setup          Run interactive OAuth flow
  search         Search emails (Gmail query syntax)
  read           Read a single message by ID (full body)
  thread         Read an entire thread by thread ID
  draft          Create a draft email
  send           Send an email directly
  reply          Reply to a message (sender only)
  reply-all      Reply to all recipients
  forward        Forward a message to new recipients
  trash          Move a message to trash
  untrash        Remove a message from trash
  labels         List all labels
  modify-labels  Add/remove labels on a message
  attachments    Download attachments from a message
"""

import argparse
import base64
import json
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Any

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

# --- Configuration ---

CREDENTIALS_DIR = Path(
    os.environ.get("GMAIL_CREDENTIALS_DIR", Path.home() / ".gmail_credentials")
)
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/gmail.readonly"],
    "modify": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ],
    "full": ["https://mail.google.com/"],
}
# Default to full — required for send, trash, and label modifications
DEFAULT_SCOPE = "full"


class GmailTool:
    """Full CRUD Gmail wrapper for AI agents."""

    def __init__(self, skip_auth: bool = False):
        self.service: Optional[Resource] = None
        self._user_email: Optional[str] = None
        if not skip_auth:
            self._authenticate()

    def _get_current_scope(self) -> str:
        if SCOPE_FILE.exists():
            return SCOPE_FILE.read_text().strip()
        return DEFAULT_SCOPE

    def _authenticate(self) -> None:
        """Authenticate via token → ADC → client secrets fallback chain."""
        creds = None
        scope = self._get_current_scope()
        scopes = SCOPES_MAP.get(scope, SCOPES_MAP[DEFAULT_SCOPE])

        # 1. Try Local Token
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)
            except Exception:
                pass

        # 2. Try ADC
        if not creds or not creds.valid:
            try:
                creds, _ = google.auth.default(scopes=scopes)
                if creds and creds.expired and getattr(creds, "refresh_token", None):
                    creds.refresh(Request())
            except Exception:
                creds = None

        # 3. Refresh expired token
        if not creds or not creds.valid:
            if creds and creds.expired and getattr(creds, "refresh_token", None):
                try:
                    creds.refresh(Request())
                    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
                    TOKEN_FILE.write_text(creds.to_json())
                except Exception:
                    if TOKEN_FILE.exists():
                        TOKEN_FILE.unlink()
                    creds = None

            if not creds and CLIENT_SECRETS_FILE.exists():
                pass  # require explicit `setup` command

        if creds:
            self.service = build("gmail", "v1", credentials=creds)

    def setup_interactive(self) -> None:
        """Force interactive OAuth flow using credentials.json."""
        print("🔵 Starting Interactive Setup for Gmail...")
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

            self.service = build("gmail", "v1", credentials=creds)
            print(f"✅ Authentication successful! Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")

    def ensure_service(self) -> None:
        if not self.service:
            raise RuntimeError(
                "Gmail API not authenticated. Run 'setup' command or configure ADC."
            )

    # ────────────────────────────────────────────────────────────
    # Profile
    # ────────────────────────────────────────────────────────────

    def get_profile(self) -> Dict[str, Any]:
        """Get authenticated user's profile (email, messages total, etc.)."""
        self.ensure_service()
        return self.service.users().getProfile(userId="me").execute()

    def _get_user_email(self) -> str:
        """Cache and return the authenticated user's email address."""
        if not self._user_email:
            profile = self.get_profile()
            self._user_email = profile.get("emailAddress", "me")
        return self._user_email

    # ────────────────────────────────────────────────────────────
    # Labels
    # ────────────────────────────────────────────────────────────

    def list_labels(self) -> List[Dict[str, str]]:
        self.ensure_service()
        results = self.service.users().labels().list(userId="me").execute()
        return results.get("labels", [])

    def modify_labels(
        self,
        msg_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Add/remove labels on a message."""
        self.ensure_service()
        body: Dict[str, Any] = {}
        if add_labels:
            body["addLabelIds"] = add_labels
        if remove_labels:
            body["removeLabelIds"] = remove_labels
        return (
            self.service.users()
            .messages()
            .modify(userId="me", id=msg_id, body=body)
            .execute()
        )

    # ────────────────────────────────────────────────────────────
    # Search / Read
    # ────────────────────────────────────────────────────────────

    def search_messages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search messages and return summary details."""
        self.ensure_service()
        results = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=limit)
            .execute()
        )
        messages = results.get("messages", [])

        detailed = []
        for msg in messages:
            try:
                details = self._get_message_summary(msg["id"])
                detailed.append(details)
            except Exception:
                continue
        return detailed

    def _get_message_summary(self, msg_id: str) -> Dict[str, Any]:
        """Return a lightweight summary (no full body)."""
        msg = (
            self.service.users()
            .messages()
            .get(userId="me", id=msg_id, format="metadata",
                 metadataHeaders=["From", "To", "Cc", "Bcc", "Subject", "Date", "Message-ID", "In-Reply-To", "References"])
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        return {
            "id": msg_id,
            "threadId": msg.get("threadId"),
            "snippet": msg.get("snippet"),
            "from": headers.get("From"),
            "to": headers.get("To"),
            "cc": headers.get("Cc"),
            "bcc": headers.get("Bcc"),
            "subject": headers.get("Subject"),
            "date": headers.get("Date"),
            "messageId": headers.get("Message-ID"),
            "labels": msg.get("labelIds", []),
        }

    def read_message(self, msg_id: str) -> Dict[str, Any]:
        """Read a single message including full body text."""
        self.ensure_service()
        msg = (
            self.service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        body = self._extract_body(msg.get("payload", {}))
        attachments = self._list_attachments(msg.get("payload", {}))

        return {
            "id": msg_id,
            "threadId": msg.get("threadId"),
            "snippet": msg.get("snippet"),
            "from": headers.get("From"),
            "to": headers.get("To"),
            "cc": headers.get("Cc"),
            "bcc": headers.get("Bcc"),
            "subject": headers.get("Subject"),
            "date": headers.get("Date"),
            "messageId": headers.get("Message-ID"),
            "inReplyTo": headers.get("In-Reply-To"),
            "references": headers.get("References"),
            "labels": msg.get("labelIds", []),
            "body": body,
            "attachments": attachments,
        }

    def read_thread(self, thread_id: str) -> Dict[str, Any]:
        """Read all messages in a thread."""
        self.ensure_service()
        thread = (
            self.service.users()
            .threads()
            .get(userId="me", id=thread_id, format="full")
            .execute()
        )

        messages = []
        for msg in thread.get("messages", []):
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            body = self._extract_body(msg.get("payload", {}))
            messages.append({
                "id": msg["id"],
                "snippet": msg.get("snippet"),
                "from": headers.get("From"),
                "to": headers.get("To"),
                "cc": headers.get("Cc"),
                "subject": headers.get("Subject"),
                "date": headers.get("Date"),
                "messageId": headers.get("Message-ID"),
                "labels": msg.get("labelIds", []),
                "body": body,
            })

        return {
            "threadId": thread_id,
            "messageCount": len(messages),
            "messages": messages,
        }

    # ────────────────────────────────────────────────────────────
    # Body extraction helpers
    # ────────────────────────────────────────────────────────────

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Recursively extract text/plain body (fallback to text/html)."""
        mime_type = payload.get("mimeType", "")

        # Direct body data
        if mime_type == "text/plain" and payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

        # Multipart: recurse
        parts = payload.get("parts", [])
        plain_text = ""
        html_text = ""
        for part in parts:
            part_mime = part.get("mimeType", "")
            if part_mime == "text/plain" and part.get("body", {}).get("data"):
                plain_text += base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            elif part_mime == "text/html" and part.get("body", {}).get("data"):
                html_text += base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            elif part_mime.startswith("multipart/"):
                nested = self._extract_body(part)
                if nested:
                    plain_text += nested

        return plain_text if plain_text else html_text

    def _list_attachments(self, payload: Dict[str, Any]) -> List[Dict[str, str]]:
        """List attachment metadata (filename, mimeType, attachmentId)."""
        attachments: List[Dict[str, str]] = []
        parts = payload.get("parts", [])
        for part in parts:
            filename = part.get("filename")
            if filename:
                att_body = part.get("body", {})
                attachments.append({
                    "filename": filename,
                    "mimeType": part.get("mimeType", ""),
                    "size": str(att_body.get("size", 0)),
                    "attachmentId": att_body.get("attachmentId", ""),
                })
            # Recurse into nested multipart
            if part.get("parts"):
                attachments.extend(self._list_attachments(part))
        return attachments

    def download_attachment(
        self, msg_id: str, attachment_id: str, filename: str, output_dir: str = "."
    ) -> str:
        """Download an attachment and save it to disk."""
        self.ensure_service()
        att = (
            self.service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=msg_id, id=attachment_id)
            .execute()
        )
        data = base64.urlsafe_b64decode(att["data"])
        out_path = Path(output_dir) / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        return str(out_path)

    # ────────────────────────────────────────────────────────────
    # Compose / Draft / Send
    # ────────────────────────────────────────────────────────────

    def _build_mime(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
    ) -> str:
        """Build a MIME message and return urlsafe-b64 encoded raw string."""
        message = MIMEText(body, "plain", "utf-8")
        message["to"] = to
        message["from"] = self._get_user_email()
        message["subject"] = subject
        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc
        if in_reply_to:
            message["In-Reply-To"] = in_reply_to
            message["References"] = references or in_reply_to

        return base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a draft email (optionally threaded)."""
        self.ensure_service()
        raw = self._build_mime(to, subject, body, cc, bcc, in_reply_to, references)
        draft_body: Dict[str, Any] = {"message": {"raw": raw}}
        if thread_id:
            draft_body["message"]["threadId"] = thread_id
        return self.service.users().drafts().create(userId="me", body=draft_body).execute()

    def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send an email directly."""
        self.ensure_service()
        raw = self._build_mime(to, subject, body, cc, bcc, in_reply_to, references)
        msg_body: Dict[str, Any] = {"raw": raw}
        if thread_id:
            msg_body["threadId"] = thread_id
        return self.service.users().messages().send(userId="me", body=msg_body).execute()

    # ────────────────────────────────────────────────────────────
    # Reply / Reply All / Forward
    # ────────────────────────────────────────────────────────────

    def reply(self, msg_id: str, body: str, send: bool = False) -> Dict[str, Any]:
        """Reply to the sender of a message."""
        original = self.read_message(msg_id)
        to = original["from"]
        subject = original["subject"] or ""
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        method = self.send_message if send else self.create_draft
        return method(
            to=to,
            subject=subject,
            body=body,
            thread_id=original["threadId"],
            in_reply_to=original.get("messageId"),
            references=self._build_references(original),
        )

    def reply_all(self, msg_id: str, body: str, send: bool = False) -> Dict[str, Any]:
        """Reply to all recipients of a message (sender + To + Cc, minus self)."""
        original = self.read_message(msg_id)
        my_email = self._get_user_email().lower()

        # Collect all recipients
        all_addrs = set()
        if original.get("from"):
            all_addrs.add(original["from"])
        for field in ("to", "cc"):
            val = original.get(field)
            if val:
                for addr in val.split(","):
                    all_addrs.add(addr.strip())

        # Remove self
        filtered = [a for a in all_addrs if my_email not in a.lower()]

        # Original sender is the primary "To", everyone else goes to "Cc"
        to = original["from"]
        cc_list = [a for a in filtered if a != to]
        cc = ", ".join(cc_list) if cc_list else None

        subject = original["subject"] or ""
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        method = self.send_message if send else self.create_draft
        return method(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            thread_id=original["threadId"],
            in_reply_to=original.get("messageId"),
            references=self._build_references(original),
        )

    def forward(
        self,
        msg_id: str,
        to: str,
        body: Optional[str] = None,
        send: bool = False,
    ) -> Dict[str, Any]:
        """Forward a message (includes original body)."""
        original = self.read_message(msg_id)

        subject = original["subject"] or ""
        if not subject.lower().startswith("fwd:"):
            subject = f"Fwd: {subject}"

        # Build forwarded body with attribution
        fwd_header = (
            f"\n\n---------- Forwarded message ----------\n"
            f"From: {original.get('from', 'Unknown')}\n"
            f"Date: {original.get('date', 'Unknown')}\n"
            f"Subject: {original.get('subject', '(no subject)')}\n"
            f"To: {original.get('to', 'Unknown')}\n\n"
        )
        original_body = original.get("body", "")
        full_body = (body or "") + fwd_header + original_body

        method = self.send_message if send else self.create_draft
        return method(
            to=to,
            subject=subject,
            body=full_body,
            thread_id=original["threadId"],
            in_reply_to=original.get("messageId"),
            references=self._build_references(original),
        )

    def _build_references(self, msg: Dict[str, Any]) -> str:
        """Build the References header for proper threading."""
        refs = msg.get("references", "") or ""
        msg_id = msg.get("messageId", "")
        if msg_id:
            refs = f"{refs} {msg_id}".strip()
        return refs

    # ────────────────────────────────────────────────────────────
    # Trash / Untrash (Delete)
    # ────────────────────────────────────────────────────────────

    def trash_message(self, msg_id: str) -> Dict[str, Any]:
        """Move a message to the trash."""
        self.ensure_service()
        return self.service.users().messages().trash(userId="me", id=msg_id).execute()

    def untrash_message(self, msg_id: str) -> Dict[str, Any]:
        """Remove a message from the trash."""
        self.ensure_service()
        return self.service.users().messages().untrash(userId="me", id=msg_id).execute()


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description="Gmail AI Skill — Full CRUD + Reply/Forward")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # search
    sp = subparsers.add_parser("search", help="Search emails")
    sp.add_argument("--query", "-q", required=True, help="Gmail query string")
    sp.add_argument("--limit", type=int, default=10, help="Max results")

    # read
    sp = subparsers.add_parser("read", help="Read a single message (full body)")
    sp.add_argument("--id", required=True, help="Message ID")

    # thread
    sp = subparsers.add_parser("thread", help="Read all messages in a thread")
    sp.add_argument("--id", required=True, help="Thread ID")

    # draft
    sp = subparsers.add_parser("draft", help="Create a draft email")
    sp.add_argument("--to", required=True, help="Recipient email")
    sp.add_argument("--subject", required=True, help="Subject line")
    sp.add_argument("--body", required=True, help="Email body text")
    sp.add_argument("--cc", help="CC recipient(s)")
    sp.add_argument("--bcc", help="BCC recipient(s)")

    # send
    sp = subparsers.add_parser("send", help="Send an email directly")
    sp.add_argument("--to", required=True, help="Recipient email")
    sp.add_argument("--subject", required=True, help="Subject line")
    sp.add_argument("--body", required=True, help="Email body text")
    sp.add_argument("--cc", help="CC recipient(s)")
    sp.add_argument("--bcc", help="BCC recipient(s)")

    # reply
    sp = subparsers.add_parser("reply", help="Reply to a message (sender only)")
    sp.add_argument("--id", required=True, help="Message ID to reply to")
    sp.add_argument("--body", required=True, help="Reply body text")
    sp.add_argument("--send", action="store_true", help="Send immediately (default: draft)")

    # reply-all
    sp = subparsers.add_parser("reply-all", help="Reply to all recipients")
    sp.add_argument("--id", required=True, help="Message ID to reply to")
    sp.add_argument("--body", required=True, help="Reply body text")
    sp.add_argument("--send", action="store_true", help="Send immediately (default: draft)")

    # forward
    sp = subparsers.add_parser("forward", help="Forward a message")
    sp.add_argument("--id", required=True, help="Message ID to forward")
    sp.add_argument("--to", required=True, help="Forward recipient email")
    sp.add_argument("--body", help="Optional note above forwarded content")
    sp.add_argument("--send", action="store_true", help="Send immediately (default: draft)")

    # trash
    sp = subparsers.add_parser("trash", help="Move a message to trash")
    sp.add_argument("--id", required=True, help="Message ID")

    # untrash
    sp = subparsers.add_parser("untrash", help="Remove a message from trash")
    sp.add_argument("--id", required=True, help="Message ID")

    # labels
    subparsers.add_parser("labels", help="List all labels")

    # modify-labels
    sp = subparsers.add_parser("modify-labels", help="Add/remove labels on a message")
    sp.add_argument("--id", required=True, help="Message ID")
    sp.add_argument("--add", nargs="*", default=[], help="Label IDs to add")
    sp.add_argument("--remove", nargs="*", default=[], help="Label IDs to remove")

    # attachments
    sp = subparsers.add_parser("attachments", help="Download attachments from a message")
    sp.add_argument("--id", required=True, help="Message ID")
    sp.add_argument("--output-dir", default=".", help="Directory to save attachments")

    args = parser.parse_args()

    # Setup is special — skip auto-auth
    if args.command == "setup":
        tool = GmailTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = GmailTool()

        if args.command == "verify":
            print_json({"status": "authenticated", "profile": tool.get_profile()})

        elif args.command == "search":
            results = tool.search_messages(args.query, args.limit)
            print_json(results)

        elif args.command == "read":
            msg = tool.read_message(args.id)
            print_json(msg)

        elif args.command == "thread":
            thread = tool.read_thread(args.id)
            print_json(thread)

        elif args.command == "draft":
            draft = tool.create_draft(args.to, args.subject, args.body, args.cc, args.bcc)
            print_json({"status": "draft_created", "draft": draft})

        elif args.command == "send":
            result = tool.send_message(args.to, args.subject, args.body, args.cc, args.bcc)
            print_json({"status": "sent", "message": result})

        elif args.command == "reply":
            result = tool.reply(args.id, args.body, send=args.send)
            action = "sent" if args.send else "draft_created"
            print_json({"status": action, "result": result})

        elif args.command == "reply-all":
            result = tool.reply_all(args.id, args.body, send=args.send)
            action = "sent" if args.send else "draft_created"
            print_json({"status": action, "result": result})

        elif args.command == "forward":
            result = tool.forward(args.id, args.to, body=args.body, send=args.send)
            action = "sent" if args.send else "draft_created"
            print_json({"status": action, "result": result})

        elif args.command == "trash":
            result = tool.trash_message(args.id)
            print_json({"status": "trashed", "message": result})

        elif args.command == "untrash":
            result = tool.untrash_message(args.id)
            print_json({"status": "untrashed", "message": result})

        elif args.command == "labels":
            labels = tool.list_labels()
            print_json(labels)

        elif args.command == "modify-labels":
            result = tool.modify_labels(
                args.id,
                add_labels=args.add or None,
                remove_labels=args.remove or None,
            )
            print_json({"status": "labels_modified", "message": result})

        elif args.command == "attachments":
            msg = tool.read_message(args.id)
            downloaded = []
            for att in msg.get("attachments", []):
                if att.get("attachmentId"):
                    path = tool.download_attachment(
                        args.id, att["attachmentId"], att["filename"], args.output_dir
                    )
                    downloaded.append({"filename": att["filename"], "path": path})
            print_json({"status": "downloaded", "attachments": downloaded})

        else:
            parser.print_help()

    except Exception as e:
        print_json({"status": "error", "message": str(e), "type": type(e).__name__})


if __name__ == "__main__":
    main()
