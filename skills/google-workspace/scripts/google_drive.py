#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
# ]
# ///

"""
Google Drive Skill - Full CRUD for AI agents.

Commands:
  verify             Check authentication status
  setup              Run interactive OAuth flow
  list               List files in a folder (default: root)
  search             Search files by name or full-text content
  get                Get file metadata by ID
  upload             Upload a local file to Drive
  download           Download a file from Drive to local disk
  mkdir              Create a folder
  move               Move a file to a different folder
  copy               Copy a file
  rename             Rename a file
  trash              Move a file to trash
  untrash            Restore a file from trash
  empty-trash        Permanently delete all trashed files
  delete             Permanently delete a specific file
  share              Share a file (add permission)
  unshare            Remove a permission from a file
  permissions        List permissions on a file
  export             Export a Google Workspace doc to a local format
  list-revisions     List revision history of a file
  restore-revision   Restore a file to a prior revision
  list-comments      List comments on a file
  add-comment        Add a comment to a file
"""

import argparse
import io
import json
import mimetypes
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
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import workspace_lib

# --- Configuration ---

def _find_credentials_dir() -> Path:
    return workspace_lib.find_credentials_dir(
        env_var="DRIVE_CREDENTIALS_DIR",
        legacy_dir_name=".drive_credentials"
    )

CREDENTIALS_DIR = _find_credentials_dir()
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    "readonly": ["https://www.googleapis.com/auth/drive.readonly"],
    "file": ["https://www.googleapis.com/auth/drive.file"],
    "full": ["https://www.googleapis.com/auth/drive"],
}
DEFAULT_SCOPE = "full"

# Google Workspace MIME type → export format mapping
EXPORT_MIME_MAP = {
    "application/vnd.google-apps.document": {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
        "html": "text/html",
        "md": "text/plain",
    },
    "application/vnd.google-apps.spreadsheet": {
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
    },
    "application/vnd.google-apps.presentation": {
        "pdf": "application/pdf",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    },
    "application/vnd.google-apps.drawing": {
        "pdf": "application/pdf",
        "png": "image/png",
        "svg": "image/svg+xml",
    },
}


class DriveTool:
    """Full CRUD Google Drive wrapper for AI agents."""

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
            service_name="Drive"
        )

        if creds and creds.valid:
            self.service = build("drive", "v3", credentials=creds)

    def setup_interactive(self) -> None:
        print("🔵 Starting Interactive Setup for Google Drive...")
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

            self.service = build("drive", "v3", credentials=creds)
            print(f"✅ Authentication successful! Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")

    def ensure_service(self) -> None:
        if not self.service:
            raise workspace_lib.AuthError(
                "Drive API not authenticated.",
                fix="Run: uv run scripts/preflight.py  (to diagnose), then: uv run scripts/setup_workspace.py  (to authenticate)",
            )

    # ────────────────────────────────────────────────────────────
    # Normalization
    # ────────────────────────────────────────────────────────────

    FILE_FIELDS = (
        "id,name,mimeType,size,createdTime,modifiedTime,parents,"
        "webViewLink,webContentLink,trashed,shared,owners,permissions,"
        "description,starred"
    )

    def _normalize_file(self, f: Dict[str, Any]) -> Dict[str, Any]:
        owners = f.get("owners", [])
        return {
            "id": f.get("id"),
            "name": f.get("name"),
            "mimeType": f.get("mimeType"),
            "size": f.get("size"),
            "createdTime": f.get("createdTime"),
            "modifiedTime": f.get("modifiedTime"),
            "parents": f.get("parents"),
            "webViewLink": f.get("webViewLink"),
            "webContentLink": f.get("webContentLink"),
            "trashed": f.get("trashed", False),
            "shared": f.get("shared", False),
            "starred": f.get("starred", False),
            "description": f.get("description"),
            "owner": owners[0].get("emailAddress") if owners else None,
            "isFolder": f.get("mimeType") == "application/vnd.google-apps.folder",
        }

    # ────────────────────────────────────────────────────────────
    # List / Search / Get
    # ────────────────────────────────────────────────────────────

    def list_files(
        self,
        folder_id: str = "root",
        limit: int = 50,
        order_by: str = "folder,modifiedTime desc",
        include_trashed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List files in a specific folder."""
        self.ensure_service()
        q = f"'{folder_id}' in parents"
        if not include_trashed:
            q += " and trashed = false"

        result = self.service.files().list(
            q=q,
            pageSize=min(limit, 1000),
            fields=f"files({self.FILE_FIELDS})",
            orderBy=order_by,
        ).execute()

        return [self._normalize_file(f) for f in result.get("files", [])]

    def search_files(
        self,
        query: str,
        limit: int = 20,
        mime_type: Optional[str] = None,
        include_trashed: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search files by name or full-text content."""
        self.ensure_service()

        # Build query: supports both name search and fullText search
        parts: List[str] = []
        if query:
            parts.append(f"(name contains '{query}' or fullText contains '{query}')")
        if mime_type:
            parts.append(f"mimeType = '{mime_type}'")
        if not include_trashed:
            parts.append("trashed = false")

        q = " and ".join(parts) if parts else None

        result = self.service.files().list(
            q=q,
            pageSize=min(limit, 1000),
            fields=f"files({self.FILE_FIELDS})",
            orderBy="modifiedTime desc",
        ).execute()

        return [self._normalize_file(f) for f in result.get("files", [])]

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata by ID."""
        self.ensure_service()
        f = self.service.files().get(
            fileId=file_id, fields=self.FILE_FIELDS
        ).execute()
        return self._normalize_file(f)

    # ────────────────────────────────────────────────────────────
    # Upload / Download / Export
    # ────────────────────────────────────────────────────────────

    def upload_file(
        self,
        local_path: str,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
        description: str = "",
    ) -> Dict[str, Any]:
        """Upload a local file to Google Drive."""
        self.ensure_service()
        path = Path(local_path)
        if not path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        file_name = name or path.name
        mime_type, _ = mimetypes.guess_type(str(path))
        mime_type = mime_type or "application/octet-stream"

        metadata: Dict[str, Any] = {
            "name": file_name,
            "description": description,
        }
        if folder_id:
            metadata["parents"] = [folder_id]

        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=True)
        result = self.service.files().create(
            body=metadata, media_body=media, fields=self.FILE_FIELDS
        ).execute()

        return self._normalize_file(result)

    def download_file(
        self, file_id: str, output_path: str
    ) -> str:
        """Download a file from Drive to local disk."""
        self.ensure_service()
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        request = self.service.files().get_media(fileId=file_id)
        with open(str(out), "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        return str(out)

    def export_file(
        self, file_id: str, output_path: str, export_format: str = "pdf"
    ) -> str:
        """Export a Google Workspace document (Docs/Sheets/Slides) to a local format."""
        self.ensure_service()

        # Get the file's MIME type to determine export options
        file_meta = self.service.files().get(fileId=file_id, fields="mimeType,name").execute()
        source_mime = file_meta.get("mimeType", "")

        export_map = EXPORT_MIME_MAP.get(source_mime)
        if not export_map:
            raise ValueError(
                f"File type '{source_mime}' is not a Google Workspace doc. Use 'download' instead."
            )

        target_mime = export_map.get(export_format)
        if not target_mime:
            available = ", ".join(export_map.keys())
            raise ValueError(
                f"Unsupported export format '{export_format}' for {source_mime}. "
                f"Available: {available}"
            )

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        request = self.service.files().export_media(fileId=file_id, mimeType=target_mime)
        with open(str(out), "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        return str(out)

    # ────────────────────────────────────────────────────────────
    # Create Folder
    # ────────────────────────────────────────────────────────────

    def create_folder(
        self, name: str, parent_id: Optional[str] = None, description: str = ""
    ) -> Dict[str, Any]:
        """Create a folder in Drive."""
        self.ensure_service()
        metadata: Dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "description": description,
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        result = self.service.files().create(
            body=metadata, fields=self.FILE_FIELDS
        ).execute()
        return self._normalize_file(result)

    # ────────────────────────────────────────────────────────────
    # Move / Copy / Rename
    # ────────────────────────────────────────────────────────────

    def move_file(self, file_id: str, new_parent_id: str) -> Dict[str, Any]:
        """Move a file to a different folder."""
        self.ensure_service()
        # Get current parents to remove
        current = self.service.files().get(fileId=file_id, fields="parents").execute()
        previous_parents = ",".join(current.get("parents", []))

        result = self.service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields=self.FILE_FIELDS,
        ).execute()
        return self._normalize_file(result)

    def copy_file(
        self, file_id: str, name: Optional[str] = None, folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Copy a file (optionally to a different folder with a new name)."""
        self.ensure_service()
        body: Dict[str, Any] = {}
        if name:
            body["name"] = name
        if folder_id:
            body["parents"] = [folder_id]

        result = self.service.files().copy(
            fileId=file_id, body=body, fields=self.FILE_FIELDS
        ).execute()
        return self._normalize_file(result)

    def rename_file(self, file_id: str, new_name: str) -> Dict[str, Any]:
        """Rename a file."""
        self.ensure_service()
        result = self.service.files().update(
            fileId=file_id, body={"name": new_name}, fields=self.FILE_FIELDS
        ).execute()
        return self._normalize_file(result)

    # ────────────────────────────────────────────────────────────
    # Trash / Untrash / Delete
    # ────────────────────────────────────────────────────────────

    def trash_file(self, file_id: str) -> Dict[str, Any]:
        """Move a file to trash (reversible)."""
        self.ensure_service()
        result = self.service.files().update(
            fileId=file_id, body={"trashed": True}, fields=self.FILE_FIELDS
        ).execute()
        return self._normalize_file(result)

    def untrash_file(self, file_id: str) -> Dict[str, Any]:
        """Restore a file from trash."""
        self.ensure_service()
        result = self.service.files().update(
            fileId=file_id, body={"trashed": False}, fields=self.FILE_FIELDS
        ).execute()
        return self._normalize_file(result)

    def delete_file(self, file_id: str) -> Dict[str, str]:
        """Permanently delete a file (irreversible)."""
        self.ensure_service()
        self.service.files().delete(fileId=file_id).execute()
        return {"status": "permanently_deleted", "fileId": file_id}

    # ────────────────────────────────────────────────────────────
    # Sharing / Permissions
    # ────────────────────────────────────────────────────────────

    def list_permissions(self, file_id: str) -> List[Dict[str, Any]]:
        """List all permissions on a file."""
        self.ensure_service()
        result = self.service.permissions().list(
            fileId=file_id,
            fields="permissions(id,type,role,emailAddress,displayName,domain)",
        ).execute()
        return result.get("permissions", [])

    def share_file(
        self,
        file_id: str,
        email: Optional[str] = None,
        domain: Optional[str] = None,
        role: str = "reader",
        share_type: Optional[str] = None,
        send_notification: bool = True,
        message: str = "",
    ) -> Dict[str, Any]:
        """Share a file with a user, group, domain, or make it public.

        Args:
            file_id: The file to share.
            email: Email address for 'user' or 'group' type.
            domain: Domain for 'domain' type.
            role: 'reader', 'commenter', 'writer', or 'owner'.
            share_type: 'user', 'group', 'domain', or 'anyone'. Auto-detected if omitted.
            send_notification: Send email notification (user/group only).
            message: Custom notification message.
        """
        self.ensure_service()

        # Auto-detect type
        if not share_type:
            if email:
                share_type = "user"
            elif domain:
                share_type = "domain"
            else:
                share_type = "anyone"

        perm: Dict[str, Any] = {
            "type": share_type,
            "role": role,
        }
        if email:
            perm["emailAddress"] = email
        if domain:
            perm["domain"] = domain

        result = self.service.permissions().create(
            fileId=file_id,
            body=perm,
            sendNotificationEmail=send_notification,
            emailMessage=message if message else None,
            fields="id,type,role,emailAddress,displayName",
        ).execute()
        return result

    def unshare_file(self, file_id: str, permission_id: str) -> Dict[str, str]:
        """Remove a permission from a file."""
        self.ensure_service()
        self.service.permissions().delete(
            fileId=file_id, permissionId=permission_id
        ).execute()
        return {"status": "permission_removed", "permissionId": permission_id}

    # ────────────────────────────────────────────────────────────
    # Trash management
    # ────────────────────────────────────────────────────────────

    def empty_trash(self) -> Dict[str, str]:
        """Permanently delete all files in the user's Drive trash."""
        self.ensure_service()
        self.service.files().emptyTrash().execute()
        return {"status": "trash_emptied"}

    # ────────────────────────────────────────────────────────────
    # Revisions
    # ────────────────────────────────────────────────────────────

    def list_revisions(self, file_id: str) -> List[Dict[str, Any]]:
        """List revision history of a file."""
        self.ensure_service()
        result = self.service.revisions().list(
            fileId=file_id,
            fields="revisions(id,modifiedTime,lastModifyingUser,keepForever,size)",
        ).execute()
        return result.get("revisions", [])

    def restore_revision(
        self, file_id: str, revision_id: str, keep_forever: bool = False
    ) -> Dict[str, Any]:
        """Restore a file to a revision by marking it as keepForever and downloading it.

        Note: Drive v3 does not directly 'restore' revisions via API.
        The pattern is: (1) mark the target revision keepForever, (2) export/download it,
        (3) re-upload as the current version. This method marks the revision
        keepForever and returns its download URI for the caller to act on.
        """
        self.ensure_service()
        result = self.service.revisions().update(
            fileId=file_id,
            revisionId=revision_id,
            body={"keepForever": True},
            fields="id,modifiedTime,keepForever",
        ).execute()
        return {
            "fileId": file_id,
            "revision": result,
            "note": "Revision marked keepForever. Download with: drive download --id FILE_ID then re-upload.",
        }

    # ────────────────────────────────────────────────────────────
    # File Comments
    # ────────────────────────────────────────────────────────────

    def list_comments(self, file_id: str) -> List[Dict[str, Any]]:
        """List all comments on a file."""
        self.ensure_service()
        result = self.service.comments().list(
            fileId=file_id,
            fields="comments(id,content,author,createdTime,resolved)",
        ).execute()
        return result.get("comments", [])

    def add_comment(self, file_id: str, content: str) -> Dict[str, Any]:
        """Add a top-level comment to a file."""
        self.ensure_service()
        result = self.service.comments().create(
            fileId=file_id,
            body={"content": content},
            fields="id,content,author,createdTime",
        ).execute()
        return result


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Drive AI Skill — Full CRUD")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # list
    sp = subparsers.add_parser("list", help="List files in a folder")
    sp.add_argument("--folder", default="root", help="Folder ID (default: root)")
    sp.add_argument("--limit", type=int, default=50, help="Max results")
    sp.add_argument("--include-trashed", action="store_true", help="Include trashed files")

    # search
    sp = subparsers.add_parser("search", help="Search files")
    sp.add_argument("--query", "-q", required=True, help="Search query (name or content)")
    sp.add_argument("--limit", type=int, default=20, help="Max results")
    sp.add_argument("--mime-type", help="Filter by MIME type")
    sp.add_argument("--include-trashed", action="store_true", help="Include trashed files")

    # get
    sp = subparsers.add_parser("get", help="Get file metadata by ID")
    sp.add_argument("--id", required=True, help="File ID")

    # upload
    sp = subparsers.add_parser("upload", help="Upload a local file to Drive")
    sp.add_argument("--file", required=True, help="Local file path")
    sp.add_argument("--name", help="Name in Drive (default: local filename)")
    sp.add_argument("--folder", help="Parent folder ID")
    sp.add_argument("--description", default="", help="File description")

    # download
    sp = subparsers.add_parser("download", help="Download a file from Drive")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--output", required=True, help="Local output path")

    # export
    sp = subparsers.add_parser("export", help="Export a Google Workspace doc")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--output", required=True, help="Local output path")
    sp.add_argument("--format", default="pdf", help="Export format (pdf, docx, txt, csv, xlsx, pptx, png, svg)")

    # mkdir
    sp = subparsers.add_parser("mkdir", help="Create a folder")
    sp.add_argument("--name", required=True, help="Folder name")
    sp.add_argument("--parent", help="Parent folder ID")
    sp.add_argument("--description", default="", help="Folder description")

    # move
    sp = subparsers.add_parser("move", help="Move a file to a different folder")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--to", required=True, help="Destination folder ID")

    # copy
    sp = subparsers.add_parser("copy", help="Copy a file")
    sp.add_argument("--id", required=True, help="File ID to copy")
    sp.add_argument("--name", help="Name for the copy")
    sp.add_argument("--folder", help="Destination folder ID")

    # rename
    sp = subparsers.add_parser("rename", help="Rename a file")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--name", required=True, help="New name")

    # trash
    sp = subparsers.add_parser("trash", help="Move a file to trash")
    sp.add_argument("--id", required=True, help="File ID")

    # untrash
    sp = subparsers.add_parser("untrash", help="Restore a file from trash")
    sp.add_argument("--id", required=True, help="File ID")

    # delete
    sp = subparsers.add_parser("delete", help="Permanently delete a file")
    sp.add_argument("--id", required=True, help="File ID")

    # share
    sp = subparsers.add_parser("share", help="Share a file")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--email", help="Email address to share with")
    sp.add_argument("--domain", help="Domain to share with")
    sp.add_argument("--role", default="reader", choices=["reader", "commenter", "writer", "owner"], help="Permission role")
    sp.add_argument("--type", dest="share_type", choices=["user", "group", "domain", "anyone"], help="Permission type (auto-detected if omitted)")
    sp.add_argument("--no-notify", action="store_true", help="Don't send notification email")
    sp.add_argument("--message", default="", help="Notification message")

    # unshare
    sp = subparsers.add_parser("unshare", help="Remove a permission")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--permission-id", required=True, help="Permission ID to remove")

    # permissions
    sp = subparsers.add_parser("permissions", help="List permissions on a file")
    sp.add_argument("--id", required=True, help="File ID")

    # empty-trash
    subparsers.add_parser("empty-trash", help="Permanently delete all trashed files")

    # list-revisions
    sp = subparsers.add_parser("list-revisions", help="List revision history of a file")
    sp.add_argument("--id", required=True, help="File ID")

    # restore-revision
    sp = subparsers.add_parser("restore-revision", help="Mark a revision keepForever")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--revision-id", required=True, help="Revision ID (from list-revisions)")

    # list-comments
    sp = subparsers.add_parser("list-comments", help="List comments on a file")
    sp.add_argument("--id", required=True, help="File ID")

    # add-comment
    sp = subparsers.add_parser("add-comment", help="Add a comment to a file")
    sp.add_argument("--id", required=True, help="File ID")
    sp.add_argument("--content", required=True, help="Comment text")

    args = parser.parse_args()

    if args.command == "setup":
        tool = DriveTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = DriveTool()

        if args.command == "verify":
            tool.ensure_service()
            tool.list_files(limit=1)
            workspace_lib.print_json({"status": "authenticated", "message": "Drive API ready"})

        elif args.command == "list":
            files = tool.list_files(
                folder_id=args.folder,
                limit=args.limit,
                include_trashed=args.include_trashed,
            )
            workspace_lib.print_json(files)

        elif args.command == "search":
            files = tool.search_files(
                query=args.query,
                limit=args.limit,
                mime_type=args.mime_type,
                include_trashed=args.include_trashed,
            )
            workspace_lib.print_json(files)

        elif args.command == "get":
            f = tool.get_file(args.id)
            workspace_lib.print_json(f)

        elif args.command == "upload":
            f = tool.upload_file(
                local_path=args.file,
                name=args.name,
                folder_id=args.folder,
                description=args.description,
            )
            workspace_lib.print_json({"status": "uploaded", "file": f})

        elif args.command == "download":
            path = tool.download_file(args.id, args.output)
            workspace_lib.print_json({"status": "downloaded", "path": path})

        elif args.command == "export":
            path = tool.export_file(args.id, args.output, export_format=args.format)
            workspace_lib.print_json({"status": "exported", "path": path, "format": args.format})

        elif args.command == "mkdir":
            folder = tool.create_folder(
                name=args.name,
                parent_id=args.parent,
                description=args.description,
            )
            workspace_lib.print_json({"status": "created", "folder": folder})

        elif args.command == "move":
            f = tool.move_file(args.id, args.to)
            workspace_lib.print_json({"status": "moved", "file": f})

        elif args.command == "copy":
            f = tool.copy_file(args.id, name=args.name, folder_id=args.folder)
            workspace_lib.print_json({"status": "copied", "file": f})

        elif args.command == "rename":
            f = tool.rename_file(args.id, args.name)
            workspace_lib.print_json({"status": "renamed", "file": f})

        elif args.command == "trash":
            f = tool.trash_file(args.id)
            workspace_lib.print_json({"status": "trashed", "file": f})

        elif args.command == "untrash":
            f = tool.untrash_file(args.id)
            workspace_lib.print_json({"status": "untrashed", "file": f})

        elif args.command == "delete":
            result = tool.delete_file(args.id)
            workspace_lib.print_json(result)

        elif args.command == "share":
            result = tool.share_file(
                file_id=args.id,
                email=args.email,
                domain=args.domain,
                role=args.role,
                share_type=args.share_type,
                send_notification=not args.no_notify,
                message=args.message,
            )
            workspace_lib.print_json({"status": "shared", "permission": result})

        elif args.command == "unshare":
            result = tool.unshare_file(args.id, args.permission_id)
            workspace_lib.print_json(result)

        elif args.command == "permissions":
            perms = tool.list_permissions(args.id)
            workspace_lib.print_json(perms)

        elif args.command == "empty-trash":
            result = tool.empty_trash()
            workspace_lib.print_json(result)

        elif args.command == "list-revisions":
            revisions = tool.list_revisions(args.id)
            workspace_lib.print_json(revisions)

        elif args.command == "restore-revision":
            result = tool.restore_revision(args.id, args.revision_id)
            workspace_lib.print_json(result)

        elif args.command == "list-comments":
            comments = tool.list_comments(args.id)
            workspace_lib.print_json(comments)

        elif args.command == "add-comment":
            comment = tool.add_comment(args.id, args.content)
            workspace_lib.print_json({"status": "commented", "comment": comment})

        else:
            parser.print_help()

    except Exception as e:
        workspace_lib.print_json({"status": "error", "message": str(e), "type": type(e).__name__})


if __name__ == "__main__":
    main()
