#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.0.0",
#   "google-auth-oauthlib>=1.0.0",
#   "requests>=2.28.0",
# ]
# ///

"""
Google Photos Skill - Full read + upload for AI agents.

NOTE: The Google Photos Library API has limited write capabilities by design.
Only media uploaded by this app can be moved or deleted. The API does not
support deleting media uploaded by other apps or via the Photos UI.

Commands:
  verify         Check authentication status
  setup          Run interactive OAuth flow
  list           List media items (photos/videos)
  search         Search media by date range, category, or content
  get            Get media item metadata by ID
  download       Download a media item to local disk
  upload         Upload a local photo/video to Google Photos
  albums         List all albums
  album-get      Get album details and contents
  album-create   Create a new album
  album-add      Add media items to an album
  album-remove   Remove media items from an album (app-uploaded only)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

import workspace_lib

# --- Configuration ---

def _find_credentials_dir() -> Path:
    return workspace_lib.find_credentials_dir(
        env_var="PHOTOS_CREDENTIALS_DIR",
        legacy_dir_name=".photos_credentials"
    )

CREDENTIALS_DIR = _find_credentials_dir()
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "credentials.json"
SCOPE_FILE = CREDENTIALS_DIR / "scope.txt"

SCOPES_MAP = {
    # Post-March 2025: old photoslibrary/photoslibrary.readonly scopes are dead.
    # These scopes only cover app-uploaded content.
    "readonly": ["https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata"],
    "appendonly": ["https://www.googleapis.com/auth/photoslibrary.appendonly"],
    "full": [
        "https://www.googleapis.com/auth/photoslibrary.appendonly",
        "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
        "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata",
    ],
}
DEFAULT_SCOPE = "full"

# Content categories supported by the Photos API
CONTENT_CATEGORIES = [
    "ANIMALS", "ARTS", "BIRTHDAYS", "CITYSCAPES", "CRAFTS", "DOCUMENTS",
    "FASHION", "FLOWERS", "FOOD", "GARDENS", "HOLIDAYS", "HOUSES",
    "LANDMARKS", "LANDSCAPES", "NIGHT", "PEOPLE", "PERFORMANCES", "PETS",
    "RECEIPTS", "SCREENSHOTS", "SELFIES", "SPORT", "TRAVEL", "UTILITY",
    "WEDDINGS", "WHITEBOARDS",
]

# Photos Library API base URL (no discovery doc — uses REST directly)
PHOTOS_API_BASE = "https://photoslibrary.googleapis.com/v1"


class PhotosTool:
    """Google Photos wrapper for AI agents."""

    def __init__(self, skip_auth: bool = False):
        self.creds: Optional[Credentials] = None
        self._session: Optional[requests.Session] = None
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
        
        self.creds = workspace_lib.authenticate(
            scopes=scopes,
            token_file=TOKEN_FILE,
            client_secrets_file=CLIENT_SECRETS_FILE,
            service_name="Photos"
        )

        if self.creds:
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"Bearer {self.creds.token}",
                "Content-Type": "application/json",
            })

    def _ensure_fresh_token(self) -> None:
        """Refresh the token if expired and update session headers."""
        if self.creds and self.creds.expired and getattr(self.creds, "refresh_token", None):
            self.creds.refresh(Request())
            if self._session:
                self._session.headers["Authorization"] = f"Bearer {self.creds.token}"

    def setup_interactive(self) -> None:
        print("🔵 Starting Interactive Setup for Google Photos...")
        print(f"   Credentials file: {CLIENT_SECRETS_FILE}")

        if not CLIENT_SECRETS_FILE.exists():
            print(f"\n❌ Error: '{CLIENT_SECRETS_FILE}' not found.")
            print("\nTo fix this:")
            print("1. Go to Google Cloud Console > APIs & Services > Credentials.")
            print("2. Create 'OAuth 2.0 Client IDs' (Application type: Desktop app).")
            print("3. Download the JSON file.")
            print(f"4. Rename it to 'credentials.json' and place it in: {CREDENTIALS_DIR}")
            print("\nAlso enable the 'Photos Library API' in your GCP project.")
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

            self.creds = creds
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"Bearer {creds.token}",
                "Content-Type": "application/json",
            })
            print(f"✅ Authentication successful! Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")

    def ensure_service(self) -> None:
        if not self._session or not self.creds:
            raise workspace_lib.AuthError(
                "Photos API not authenticated.",
                fix="Run: uv run scripts/preflight.py  (to diagnose), then: uv run scripts/setup_workspace.py  (to authenticate)",
            )
        self._ensure_fresh_token()

    def _api_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        self.ensure_service()
        resp = self._session.get(f"{PHOTOS_API_BASE}/{endpoint}", params=params)
        resp.raise_for_status()
        return resp.json()

    def _api_post(self, endpoint: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        self.ensure_service()
        resp = self._session.post(f"{PHOTOS_API_BASE}/{endpoint}", json=body or {})
        resp.raise_for_status()
        return resp.json()

    # ────────────────────────────────────────────────────────────
    # Normalization
    # ────────────────────────────────────────────────────────────

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        meta = item.get("mediaMetadata", {})
        return {
            "id": item.get("id"),
            "filename": item.get("filename"),
            "mimeType": item.get("mimeType"),
            "description": item.get("description"),
            "baseUrl": item.get("baseUrl"),
            "productUrl": item.get("productUrl"),
            "creationTime": meta.get("creationTime"),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "isVideo": "video" in meta,
            "cameraMake": meta.get("photo", {}).get("cameraMake"),
            "cameraModel": meta.get("photo", {}).get("cameraModel"),
        }

    def _normalize_album(self, album: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": album.get("id"),
            "title": album.get("title"),
            "productUrl": album.get("productUrl"),
            "mediaItemsCount": album.get("mediaItemsCount", "0"),
            "coverPhotoBaseUrl": album.get("coverPhotoBaseUrl"),
            "coverPhotoMediaItemId": album.get("coverPhotoMediaItemId"),
            "isWriteable": album.get("isWriteable", False),
        }

    # ────────────────────────────────────────────────────────────
    # Media Items
    # ────────────────────────────────────────────────────────────

    def list_items(self, limit: int = 25, page_token: Optional[str] = None) -> Dict[str, Any]:
        """List media items (most recent first)."""
        params: Dict[str, Any] = {"pageSize": min(limit, 100)}
        if page_token:
            params["pageToken"] = page_token

        result = self._api_get("mediaItems", params=params)
        items = [self._normalize_item(i) for i in result.get("mediaItems", [])]
        return {
            "items": items,
            "nextPageToken": result.get("nextPageToken"),
        }

    def search_items(
        self,
        limit: int = 25,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        categories: Optional[List[str]] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search media items by date range and/or content category."""
        body: Dict[str, Any] = {"pageSize": min(limit, 100)}
        filters: Dict[str, Any] = {}

        if date_start or date_end:
            date_filter: Dict[str, Any] = {"ranges": [{}]}
            r = date_filter["ranges"][0]
            if date_start:
                parts = date_start.split("-")
                r["startDate"] = {"year": int(parts[0]), "month": int(parts[1]), "day": int(parts[2])}
            if date_end:
                parts = date_end.split("-")
                r["endDate"] = {"year": int(parts[0]), "month": int(parts[1]), "day": int(parts[2])}
            filters["dateFilter"] = date_filter

        if categories:
            filters["contentFilter"] = {
                "includedContentCategories": [c.upper() for c in categories]
            }

        if filters:
            body["filters"] = filters
        if page_token:
            body["pageToken"] = page_token

        result = self._api_post("mediaItems:search", body=body)
        items = [self._normalize_item(i) for i in result.get("mediaItems", [])]
        return {
            "items": items,
            "nextPageToken": result.get("nextPageToken"),
        }

    def get_item(self, item_id: str) -> Dict[str, Any]:
        """Get a single media item by ID."""
        result = self._api_get(f"mediaItems/{item_id}")
        return self._normalize_item(result)

    def download_item(self, item_id: str, output_path: str) -> str:
        """Download a media item to local disk."""
        self.ensure_service()
        item = self._api_get(f"mediaItems/{item_id}")
        base_url = item.get("baseUrl", "")
        meta = item.get("mediaMetadata", {})

        # Append download parameters for full resolution
        if "video" in meta:
            download_url = f"{base_url}=dv"  # download video
        else:
            download_url = f"{base_url}=d"  # download original

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        resp = self._session.get(download_url, stream=True)
        resp.raise_for_status()
        with open(str(out), "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)

        return str(out)

    # ────────────────────────────────────────────────────────────
    # Upload
    # ────────────────────────────────────────────────────────────

    def upload_item(
        self,
        local_path: str,
        description: str = "",
        album_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a photo or video to Google Photos.

        Two-step process:
        1. Upload bytes to get an upload token.
        2. Create a media item using the token.
        """
        self.ensure_service()
        path = Path(local_path)
        if not path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        # Step 1: Raw upload
        upload_url = f"{PHOTOS_API_BASE}/uploads"
        with open(str(path), "rb") as fh:
            resp = self._session.post(
                upload_url,
                data=fh,
                headers={
                    "Authorization": f"Bearer {self.creds.token}",
                    "Content-Type": "application/octet-stream",
                    "X-Goog-Upload-File-Name": path.name,
                    "X-Goog-Upload-Protocol": "raw",
                },
            )
            resp.raise_for_status()
            upload_token = resp.text

        # Step 2: Create media item
        new_item: Dict[str, Any] = {"uploadToken": upload_token}
        if description:
            new_item["description"] = description

        body: Dict[str, Any] = {"newMediaItems": [{"simpleMediaItem": new_item}]}
        if album_id:
            body["albumId"] = album_id

        result = self._api_post("mediaItems:batchCreate", body=body)
        results = result.get("newMediaItemResults", [])
        if results:
            status = results[0]
            if status.get("status", {}).get("message") == "Success":
                return self._normalize_item(status.get("mediaItem", {}))
            else:
                raise RuntimeError(f"Upload failed: {status.get('status')}")
        raise RuntimeError("Upload returned no results")

    # ────────────────────────────────────────────────────────────
    # Albums
    # ────────────────────────────────────────────────────────────

    def list_albums(self, limit: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]:
        """List all albums."""
        params: Dict[str, Any] = {"pageSize": min(limit, 50)}
        if page_token:
            params["pageToken"] = page_token

        result = self._api_get("albums", params=params)
        albums = [self._normalize_album(a) for a in result.get("albums", [])]
        return {
            "albums": albums,
            "nextPageToken": result.get("nextPageToken"),
        }

    def get_album(self, album_id: str) -> Dict[str, Any]:
        """Get album details."""
        result = self._api_get(f"albums/{album_id}")
        return self._normalize_album(result)

    def get_album_contents(
        self, album_id: str, limit: int = 25, page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """List media items in an album."""
        body: Dict[str, Any] = {
            "albumId": album_id,
            "pageSize": min(limit, 100),
        }
        if page_token:
            body["pageToken"] = page_token

        result = self._api_post("mediaItems:search", body=body)
        items = [self._normalize_item(i) for i in result.get("mediaItems", [])]
        return {
            "items": items,
            "nextPageToken": result.get("nextPageToken"),
        }

    def create_album(self, title: str) -> Dict[str, Any]:
        """Create a new album."""
        result = self._api_post("albums", body={"album": {"title": title}})
        return self._normalize_album(result)

    def add_to_album(self, album_id: str, media_item_ids: List[str]) -> Dict[str, str]:
        """Add media items to an album (album must be created by this app)."""
        self.ensure_service()
        body = {"mediaItemIds": media_item_ids}
        resp = self._session.post(
            f"{PHOTOS_API_BASE}/albums/{album_id}:batchAddMediaItems",
            json=body,
        )
        resp.raise_for_status()
        return {"status": "added", "albumId": album_id, "count": str(len(media_item_ids))}

    def remove_from_album(self, album_id: str, media_item_ids: List[str]) -> Dict[str, str]:
        """Remove media items from an album (items must be uploaded by this app)."""
        self.ensure_service()
        body = {"mediaItemIds": media_item_ids}
        resp = self._session.post(
            f"{PHOTOS_API_BASE}/albums/{album_id}:batchRemoveMediaItems",
            json=body,
        )
        resp.raise_for_status()
        return {"status": "removed", "albumId": album_id, "count": str(len(media_item_ids))}


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Photos AI Skill")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # verify
    subparsers.add_parser("verify", help="Check authentication status")

    # setup
    subparsers.add_parser("setup", help="Run interactive authentication flow")

    # list
    sp = subparsers.add_parser("list", help="List media items")
    sp.add_argument("--limit", type=int, default=25, help="Max results")
    sp.add_argument("--page-token", help="Page token for pagination")

    # search
    sp = subparsers.add_parser("search", help="Search media items")
    sp.add_argument("--date-start", help="Start date (YYYY-MM-DD)")
    sp.add_argument("--date-end", help="End date (YYYY-MM-DD)")
    sp.add_argument("--categories", nargs="*", help=f"Content categories: {', '.join(CONTENT_CATEGORIES[:8])}...")
    sp.add_argument("--limit", type=int, default=25, help="Max results")
    sp.add_argument("--page-token", help="Page token for pagination")

    # get
    sp = subparsers.add_parser("get", help="Get media item by ID")
    sp.add_argument("--id", required=True, help="Media item ID")

    # download
    sp = subparsers.add_parser("download", help="Download a media item")
    sp.add_argument("--id", required=True, help="Media item ID")
    sp.add_argument("--output", required=True, help="Local output path")

    # upload
    sp = subparsers.add_parser("upload", help="Upload a photo/video")
    sp.add_argument("--file", required=True, help="Local file path")
    sp.add_argument("--description", default="", help="Description")
    sp.add_argument("--album", help="Album ID to add to")

    # albums
    sp = subparsers.add_parser("albums", help="List all albums")
    sp.add_argument("--limit", type=int, default=50, help="Max results")
    sp.add_argument("--page-token", help="Page token for pagination")

    # album-get
    sp = subparsers.add_parser("album-get", help="Get album details and contents")
    sp.add_argument("--id", required=True, help="Album ID")
    sp.add_argument("--limit", type=int, default=25, help="Max items to show")
    sp.add_argument("--page-token", help="Page token for pagination")

    # album-create
    sp = subparsers.add_parser("album-create", help="Create a new album")
    sp.add_argument("--title", required=True, help="Album title")

    # album-add
    sp = subparsers.add_parser("album-add", help="Add media items to an album")
    sp.add_argument("--album", required=True, help="Album ID")
    sp.add_argument("--items", nargs="+", required=True, help="Media item IDs")

    # album-remove
    sp = subparsers.add_parser("album-remove", help="Remove media items from an album")
    sp.add_argument("--album", required=True, help="Album ID")
    sp.add_argument("--items", nargs="+", required=True, help="Media item IDs")

    args = parser.parse_args()

    if args.command == "setup":
        tool = PhotosTool(skip_auth=True)
        tool.setup_interactive()
        return

    try:
        tool = PhotosTool()

        if args.command == "verify":
            tool.ensure_service()
            tool.list_items(limit=1)
            workspace_lib.print_json({"status": "authenticated", "message": "Photos API ready"})

        elif args.command == "list":
            result = tool.list_items(limit=args.limit, page_token=args.page_token)
            workspace_lib.print_json(result)

        elif args.command == "search":
            result = tool.search_items(
                limit=args.limit,
                date_start=args.date_start,
                date_end=args.date_end,
                categories=args.categories,
                page_token=args.page_token,
            )
            workspace_lib.print_json(result)

        elif args.command == "get":
            item = tool.get_item(args.id)
            workspace_lib.print_json(item)

        elif args.command == "download":
            path = tool.download_item(args.id, args.output)
            workspace_lib.print_json({"status": "downloaded", "path": path})

        elif args.command == "upload":
            item = tool.upload_item(
                local_path=args.file,
                description=args.description,
                album_id=args.album,
            )
            workspace_lib.print_json({"status": "uploaded", "item": item})

        elif args.command == "albums":
            result = tool.list_albums(limit=args.limit, page_token=args.page_token)
            workspace_lib.print_json(result)

        elif args.command == "album-get":
            album = tool.get_album(args.id)
            contents = tool.get_album_contents(
                args.id, limit=args.limit, page_token=args.page_token
            )
            workspace_lib.print_json({"album": album, **contents})

        elif args.command == "album-create":
            album = tool.create_album(args.title)
            workspace_lib.print_json({"status": "created", "album": album})

        elif args.command == "album-add":
            result = tool.add_to_album(args.album, args.items)
            workspace_lib.print_json(result)

        elif args.command == "album-remove":
            result = tool.remove_from_album(args.album, args.items)
            workspace_lib.print_json(result)

        else:
            parser.print_help()

    except Exception as e:
        workspace_lib.print_json({"status": "error", "message": str(e), "type": type(e).__name__})


if __name__ == "__main__":
    main()
