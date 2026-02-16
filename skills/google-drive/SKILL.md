---
name: google-drive
description: Full CRUD Google Drive interactions — list, search, upload, download, export, mkdir, move, copy, rename, trash, delete, share, and permissions.
---

# Google Drive Skill

Full CRUD Drive management for AI agents. List, search, upload, download, export, organize, and share files.

## Features

- **List**: Browse files in any folder (default: root), sorted by folders first then modified time.
- **Search**: Find files by name or full-text content, with optional MIME type filtering.
- **Get**: Fetch file metadata by ID.
- **Upload**: Upload local files to Drive (resumable, auto-detects MIME type).
- **Download**: Download files from Drive to local disk.
- **Export**: Export Google Workspace docs (Docs → DOCX/PDF/TXT, Sheets → XLSX/CSV, Slides → PPTX/PDF).
- **Mkdir**: Create folders.
- **Move**: Move files between folders.
- **Copy**: Duplicate files (optionally to a different folder with a new name).
- **Rename**: Rename files.
- **Trash / Untrash**: Reversible soft-delete.
- **Delete**: Permanent deletion (irreversible).
- **Share**: Share files with users, groups, domains, or make public. Supports reader/commenter/writer/owner roles.
- **Unshare**: Remove permissions.
- **Permissions**: List all permissions on a file.

## Prerequisites

1.  **Google Cloud Project** with **Google Drive API** enabled.
2.  **OAuth 2.0 Credentials** — either `gcloud` ADC or `credentials.json`.

## Setup

### ⚡ Quick Setup (Recommended)

Set up Gmail, Calendar, Contacts, and Drive all at once:

```bash
uv run ~/.agents/skills/gmail/scripts/setup_workspace.py
```

### Manual Setup

1.  **Using gcloud ADC**:

    ```bash
    gcloud auth application-default login \
      --scopes https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/cloud-platform
    ```

    Then verify:

    ```bash
    uv run skills/google-drive/scripts/google_drive.py verify
    ```

2.  **Alternative (credentials.json)**:
    - Place `credentials.json` in `~/.drive_credentials/`.
    - Run `uv run skills/google-drive/scripts/google_drive.py setup`

## Usage

### List Files

```bash
# Root folder
uv run skills/google-drive/scripts/google_drive.py list

# Specific folder
uv run skills/google-drive/scripts/google_drive.py list --folder "FOLDER_ID" --limit 20
```

### Search Files

```bash
# By name or content
uv run skills/google-drive/scripts/google_drive.py search --query "Death Star plans"

# Filter by type
uv run skills/google-drive/scripts/google_drive.py search --query "budget" --mime-type "application/vnd.google-apps.spreadsheet"
```

### Get File Metadata

```bash
uv run skills/google-drive/scripts/google_drive.py get --id "FILE_ID"
```

### Upload a File

```bash
uv run skills/google-drive/scripts/google_drive.py upload \
  --file "./blueprints.pdf" \
  --folder "FOLDER_ID" \
  --description "Thermal exhaust port schematics"
```

### Download a File

```bash
uv run skills/google-drive/scripts/google_drive.py download --id "FILE_ID" --output "./local_copy.pdf"
```

### Export a Google Workspace Doc

```bash
# Google Doc → DOCX
uv run skills/google-drive/scripts/google_drive.py export --id "DOC_ID" --output "./report.docx" --format docx

# Google Sheet → CSV
uv run skills/google-drive/scripts/google_drive.py export --id "SHEET_ID" --output "./data.csv" --format csv

# Google Slides → PDF
uv run skills/google-drive/scripts/google_drive.py export --id "SLIDES_ID" --output "./deck.pdf" --format pdf
```

### Create a Folder

```bash
uv run skills/google-drive/scripts/google_drive.py mkdir --name "Project Stardust" --parent "PARENT_FOLDER_ID"
```

### Move / Copy / Rename

```bash
# Move
uv run skills/google-drive/scripts/google_drive.py move --id "FILE_ID" --to "DEST_FOLDER_ID"

# Copy
uv run skills/google-drive/scripts/google_drive.py copy --id "FILE_ID" --name "Copy of Plans" --folder "DEST_FOLDER_ID"

# Rename
uv run skills/google-drive/scripts/google_drive.py rename --id "FILE_ID" --name "Updated Plans v2"
```

### Trash / Untrash / Delete

```bash
# Soft delete (reversible)
uv run skills/google-drive/scripts/google_drive.py trash --id "FILE_ID"

# Restore
uv run skills/google-drive/scripts/google_drive.py untrash --id "FILE_ID"

# Permanent delete (irreversible!)
uv run skills/google-drive/scripts/google_drive.py delete --id "FILE_ID"
```

### Share a File

```bash
# Share with a user
uv run skills/google-drive/scripts/google_drive.py share \
  --id "FILE_ID" --email "luke@tatooine.net" --role writer

# Make public (anyone with the link)
uv run skills/google-drive/scripts/google_drive.py share --id "FILE_ID" --type anyone --role reader

# Share with a domain
uv run skills/google-drive/scripts/google_drive.py share --id "FILE_ID" --domain "jedi.org" --role reader
```

### List / Remove Permissions

```bash
# List
uv run skills/google-drive/scripts/google_drive.py permissions --id "FILE_ID"

# Remove
uv run skills/google-drive/scripts/google_drive.py unshare --id "FILE_ID" --permission-id "PERM_ID"
```

## JSON Output

**File:**

```json
{
  "id": "1a2b3c...",
  "name": "Death Star Plans.pdf",
  "mimeType": "application/pdf",
  "size": "4200000",
  "modifiedTime": "2026-02-16T10:00:00.000Z",
  "parents": ["0B1234..."],
  "webViewLink": "https://drive.google.com/...",
  "trashed": false,
  "shared": true,
  "isFolder": false,
  "owner": "vader@empire.gov"
}
```
