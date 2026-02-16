---
name: google-photos
description: Google Photos interactions — list, search, download, upload media items, and manage albums.
---

# Google Photos Skill

Google Photos management for AI agents. Browse, search, download, upload, and organize photos and videos.

## Features

- **List**: Browse media items (most recent first), paginated.
- **Search**: Filter by date range and/or content category (landscapes, food, selfies, etc.).
- **Get**: Fetch media item metadata by ID.
- **Download**: Download full-resolution photos/videos to local disk.
- **Upload**: Upload local photos/videos to Google Photos (with optional album placement).
- **Albums**: List, create, get details, view contents.
- **Album Management**: Add/remove media items from albums.

> **API Limitation**: The Photos Library API only allows modifying media items that were uploaded by this application. You cannot delete or reorganize media uploaded via the Photos web/mobile UI.

## Prerequisites

1.  **Google Cloud Project** with **Photos Library API** enabled.
2.  **OAuth 2.0 Credentials** — either `gcloud` ADC or `credentials.json`.

## Setup

### ⚡ Quick Setup (Recommended)

Set up Gmail, Calendar, Contacts, Drive, and Photos all at once:

```bash
uv run ~/.agents/skills/gmail/scripts/setup_workspace.py
```

### Manual Setup

1.  **Using gcloud ADC**:

    ```bash
    gcloud auth application-default login \
      --scopes https://www.googleapis.com/auth/photoslibrary,https://www.googleapis.com/auth/photoslibrary.sharing,https://www.googleapis.com/auth/cloud-platform
    ```

    Then verify:

    ```bash
    uv run skills/google-photos/scripts/google_photos.py verify
    ```

2.  **Alternative (credentials.json)**:
    - Place `credentials.json` in `~/.photos_credentials/`.
    - Run `uv run skills/google-photos/scripts/google_photos.py setup`

## Usage

### List Media Items

```bash
# Most recent 25 items
uv run skills/google-photos/scripts/google_photos.py list

# With pagination
uv run skills/google-photos/scripts/google_photos.py list --limit 50 --page-token "TOKEN"
```

### Search Media

```bash
# By date range
uv run skills/google-photos/scripts/google_photos.py search \
  --date-start "2026-01-01" --date-end "2026-02-16"

# By content category
uv run skills/google-photos/scripts/google_photos.py search --categories LANDSCAPES FOOD

# Combined
uv run skills/google-photos/scripts/google_photos.py search \
  --date-start "2025-12-25" --date-end "2025-12-26" \
  --categories HOLIDAYS
```

**Available Categories**: ANIMALS, ARTS, BIRTHDAYS, CITYSCAPES, CRAFTS, DOCUMENTS, FASHION, FLOWERS, FOOD, GARDENS, HOLIDAYS, HOUSES, LANDMARKS, LANDSCAPES, NIGHT, PEOPLE, PERFORMANCES, PETS, RECEIPTS, SCREENSHOTS, SELFIES, SPORT, TRAVEL, UTILITY, WEDDINGS, WHITEBOARDS

### Get Media Item

```bash
uv run skills/google-photos/scripts/google_photos.py get --id "MEDIA_ID"
```

### Download a Photo/Video

```bash
uv run skills/google-photos/scripts/google_photos.py download --id "MEDIA_ID" --output "./sunset.jpg"
```

### Upload a Photo/Video

```bash
uv run skills/google-photos/scripts/google_photos.py upload \
  --file "./hologram.jpg" \
  --description "Leia's holographic message" \
  --album "ALBUM_ID"
```

### Albums

```bash
# List all albums
uv run skills/google-photos/scripts/google_photos.py albums

# Get album details and contents
uv run skills/google-photos/scripts/google_photos.py album-get --id "ALBUM_ID"

# Create an album
uv run skills/google-photos/scripts/google_photos.py album-create --title "Tatooine Sunsets"

# Add items to an album
uv run skills/google-photos/scripts/google_photos.py album-add --album "ALBUM_ID" --items "ITEM_1" "ITEM_2"

# Remove items from an album (app-uploaded only)
uv run skills/google-photos/scripts/google_photos.py album-remove --album "ALBUM_ID" --items "ITEM_1"
```

## JSON Output

**Media Item:**

```json
{
  "id": "ABC123...",
  "filename": "sunset_tatooine.jpg",
  "mimeType": "image/jpeg",
  "description": "Binary sunset over the Jundland Wastes",
  "baseUrl": "https://lh3.googleusercontent.com/...",
  "productUrl": "https://photos.google.com/...",
  "creationTime": "2026-02-14T18:30:00Z",
  "width": "4032",
  "height": "3024",
  "isVideo": false,
  "cameraMake": "Google",
  "cameraModel": "Pixel 9 Pro"
}
```

**Album:**

```json
{
  "id": "ALB123...",
  "title": "Tatooine Sunsets",
  "mediaItemsCount": "42",
  "isWriteable": true,
  "coverPhotoBaseUrl": "https://lh3.googleusercontent.com/..."
}
```
