---
name: google-workspace
description: Unified Google Workspace skill — Gmail, Calendar, Contacts, Drive, and Photos with local SQLite cache/index for fast queries.
---

# Google Workspace Skill

Unified Google Workspace management for AI agents. One skill, one auth, five services.

> **Replaces**: `gmail`, `google-calendar`, `google-contacts`, `google-drive`, `google-photos`
> Run `scripts/upgrade.sh` to migrate from the old per-service skills.

## Services

| Service      | Script                | Capabilities                                                              |
| ------------ | --------------------- | ------------------------------------------------------------------------- |
| **Gmail**    | `scripts/gmail.py`    | Search, read, thread, draft, send, reply, reply-all, forward, trash, labels, attachments |
| **Calendar** | `scripts/google_calendar.py` | List, get, search, create, update, delete events, quick-add, calendars  |
| **Contacts** | `scripts/contacts.py` | Search, list, get, create, update, delete contacts                        |
| **Drive**    | `scripts/google_drive.py` | List, search, upload, download, export, mkdir, move, copy, rename, trash, delete, share |
| **Photos**   | `scripts/google_photos.py` | List, search, download, upload media, manage albums                     |
| **Cache**    | `scripts/cache.py`    | Local SQLite index with incremental sync and full-text search             |

## Prerequisites

1. **Google Cloud Project** with these APIs enabled:
   - Gmail API
   - Google Calendar API
   - Google People API
   - Google Drive API
   - Photos Library API
2. **OAuth 2.0 Credentials** — Desktop app client (`credentials.json`).

## Setup

### One-Time Setup (all services at once)

```bash
uv run scripts/setup_workspace.py
```

This authenticates once with all scopes and stores a unified token at `~/.google_workspace/`.

### Manual Setup (gcloud ADC)

```bash
gcloud auth application-default login \
  --scopes https://mail.google.com/,\
https://www.googleapis.com/auth/calendar,\
https://www.googleapis.com/auth/contacts,\
https://www.googleapis.com/auth/drive,\
https://www.googleapis.com/auth/photoslibrary,\
https://www.googleapis.com/auth/photoslibrary.sharing,\
https://www.googleapis.com/auth/cloud-platform
```

### Verify

```bash
uv run scripts/gmail.py verify
uv run scripts/google_calendar.py verify
uv run scripts/contacts.py verify
uv run scripts/google_drive.py verify
uv run scripts/google_photos.py verify
```

## Credential Lookup Order

Every script checks credentials in this order:

1. **Service-specific env var** (e.g., `GMAIL_CREDENTIALS_DIR`) — for overrides.
2. **Unified directory** `~/.google_workspace/` — primary location.
3. **Legacy per-service directory** (e.g., `~/.gmail_credentials/`) — backward compat.

No migration required. If you already have legacy credentials, they still work.

---

## Cache / Index

The cache provides a local SQLite index of your Google Workspace data. This lets the agent answer queries like "find my recent emails about invoices" or "what files are in my project folder" without API calls on every request.

### How It Works

- **SQLite database** at `~/.google_workspace/cache.db` with FTS5 full-text search.
- **Incremental sync** using each service's change detection API (Gmail historyId, Calendar syncToken, Drive startPageToken, Contacts syncToken).
- **Photos**: Full re-list by creation time (no change detection API available).
- **Metadata only** — message bodies, file contents, and photos are fetched on demand, not cached.

### Cache Commands

```bash
# Sync all services (incremental if previously synced, full on first run)
uv run scripts/cache.py sync

# Sync a specific service
uv run scripts/cache.py sync --service gmail
uv run scripts/cache.py sync --service drive
uv run scripts/cache.py sync --service calendar
uv run scripts/cache.py sync --service contacts
uv run scripts/cache.py sync --service photos

# Full-text search across all cached data
uv run scripts/cache.py search "quarterly report"

# Search within a specific service
uv run scripts/cache.py search "invoice" --service gmail

# Show cache status (last sync times, record counts)
uv run scripts/cache.py status

# Clear the entire cache (does not affect credentials)
uv run scripts/cache.py clear
```

### When to Use the Cache

- **Use cache** for browsing, searching, and getting an overview of what's available.
- **Use service scripts directly** for CRUD operations (send email, create event, upload file).
- **Sync before searching** if data freshness matters — `cache.py sync` takes seconds for incremental updates.

---

## Gmail

Full CRUD Gmail management. Search, read, compose, reply, forward, and manage messages.

### Search for Emails

```bash
# Unread emails from a sender
uv run scripts/gmail.py search --query "from:obiwan@jedi.org is:unread"

# Emails with attachments
uv run scripts/gmail.py search --query "has:attachment subject:plans" --limit 5
```

### Read a Message / Thread

```bash
uv run scripts/gmail.py read --id "18e..."
uv run scripts/gmail.py thread --id "18e..."
```

### Create a Draft

**Safest option** — creates a draft for the user to review before sending.

```bash
uv run scripts/gmail.py draft \
  --to "yoda@dagobah.net" \
  --subject "Training Schedule" \
  --body "Master, when shall we begin the next session?" \
  --cc "mace@jedi.org"
```

### Send an Email

```bash
uv run scripts/gmail.py send \
  --to "yoda@dagobah.net" \
  --subject "Urgent: Sith Sighting" \
  --body "Master, I sense a disturbance in the Force."
```

### Reply / Reply All / Forward

```bash
# Reply (draft by default, --send for immediate)
uv run scripts/gmail.py reply --id "18e..." --body "Acknowledged, Master."
uv run scripts/gmail.py reply --id "18e..." --body "Acknowledged." --send

# Reply all
uv run scripts/gmail.py reply-all --id "18e..." --body "Council noted." --send

# Forward
uv run scripts/gmail.py forward --id "18e..." --to "luke@tatooine.net" --body "FYI"
uv run scripts/gmail.py forward --id "18e..." --to "luke@tatooine.net" --send
```

### Trash / Labels / Attachments

```bash
uv run scripts/gmail.py trash --id "18e..."
uv run scripts/gmail.py untrash --id "18e..."

uv run scripts/gmail.py labels
uv run scripts/gmail.py modify-labels --id "18e..." --add STARRED --remove UNREAD

uv run scripts/gmail.py attachments --id "18e..." --output-dir ./downloads
```

### Safety Guidelines

1. **Prefer `draft` over `send`** for new compositions — let the user review first.
2. **Reply/Forward defaults to draft** — use `--send` only when explicitly requested.
3. **Trash is reversible** — permanent deletion is not exposed.

---

## Calendar

Full CRUD Calendar management. List, create, update, delete, and search events.

### List / Search Events

```bash
# Next 5 events
uv run scripts/google_calendar.py list --limit 5

# Events in a date range
uv run scripts/google_calendar.py list \
  --after "2026-02-16T00:00:00Z" --before "2026-02-22T23:59:59Z"

# Search by text
uv run scripts/google_calendar.py search --query "Training" --limit 5
```

### Create / Update / Delete Events

```bash
# Timed event
uv run scripts/google_calendar.py create \
  --summary "Jedi Council Meeting" \
  --start "2026-05-04T10:00:00" --end "2026-05-04T11:00:00" \
  --location "Council Chamber, Coruscant" \
  --attendees yoda@dagobah.net mace@jedi.org

# All-day event
uv run scripts/google_calendar.py create \
  --summary "May the 4th" --start "2026-05-04" --end "2026-05-05" --all-day

# Update (patch semantics — only provided fields change)
uv run scripts/google_calendar.py update --id "abc123" --summary "Updated Meeting"

# Delete
uv run scripts/google_calendar.py delete --id "abc123"
```

### Quick Add / Calendars

```bash
uv run scripts/google_calendar.py quick --text "Lunch with Padme tomorrow at noon"
uv run scripts/google_calendar.py calendars
```

---

## Contacts

Full CRUD Contacts management via the People API.

### Search / List / Get

```bash
uv run scripts/contacts.py search --query "Han Solo"
uv run scripts/contacts.py list --limit 50
uv run scripts/contacts.py get --id "people/c12345"
```

### Create / Update / Delete

```bash
uv run scripts/contacts.py create \
  --first "Lando" --last "Calrissian" \
  --email "lando@cloudcity.com" --phone "555-0123" \
  --org "Cloud City Administration" --title "Baron Administrator"

# Update (patch semantics, etag-based conflict detection)
uv run scripts/contacts.py update --id "people/c12345" --phone "555-9999" --title "General"

uv run scripts/contacts.py delete --id "people/c12345"
```

---

## Drive

Full CRUD Drive management. List, search, upload, download, export, organize, and share files.

### List / Search / Get

```bash
uv run scripts/google_drive.py list
uv run scripts/google_drive.py list --folder "FOLDER_ID" --limit 20
uv run scripts/google_drive.py search --query "Death Star plans"
uv run scripts/google_drive.py search --query "budget" --mime-type "application/vnd.google-apps.spreadsheet"
uv run scripts/google_drive.py get --id "FILE_ID"
```

### Upload / Download / Export

```bash
uv run scripts/google_drive.py upload --file "./blueprints.pdf" --folder "FOLDER_ID"
uv run scripts/google_drive.py download --id "FILE_ID" --output "./local_copy.pdf"

# Export Google Workspace docs
uv run scripts/google_drive.py export --id "DOC_ID" --output "./report.docx" --format docx
uv run scripts/google_drive.py export --id "SHEET_ID" --output "./data.csv" --format csv
```

**Export Formats**: Google Docs (pdf, docx, txt, html, md), Sheets (pdf, xlsx, csv), Slides (pdf, pptx), Drawings (pdf, png, svg).

### Organize (mkdir, move, copy, rename)

```bash
uv run scripts/google_drive.py mkdir --name "Project Stardust" --parent "PARENT_ID"
uv run scripts/google_drive.py move --id "FILE_ID" --to "DEST_FOLDER_ID"
uv run scripts/google_drive.py copy --id "FILE_ID" --name "Copy of Plans"
uv run scripts/google_drive.py rename --id "FILE_ID" --name "Updated Plans v2"
```

### Trash / Delete / Share

```bash
# Soft delete (reversible)
uv run scripts/google_drive.py trash --id "FILE_ID"
uv run scripts/google_drive.py untrash --id "FILE_ID"

# Permanent delete (irreversible!)
uv run scripts/google_drive.py delete --id "FILE_ID"

# Share
uv run scripts/google_drive.py share --id "FILE_ID" --email "luke@tatooine.net" --role writer
uv run scripts/google_drive.py share --id "FILE_ID" --type anyone --role reader
uv run scripts/google_drive.py permissions --id "FILE_ID"
uv run scripts/google_drive.py unshare --id "FILE_ID" --permission-id "PERM_ID"
```

---

## Photos

Google Photos management. Browse, search, download, upload, and organize albums.

> **API Limitation**: The Photos Library API only allows modifying media items uploaded by this application.

### List / Search / Get / Download

```bash
uv run scripts/google_photos.py list
uv run scripts/google_photos.py search --date-start "2026-01-01" --date-end "2026-02-16"
uv run scripts/google_photos.py search --categories LANDSCAPES FOOD
uv run scripts/google_photos.py get --id "MEDIA_ID"
uv run scripts/google_photos.py download --id "MEDIA_ID" --output "./sunset.jpg"
```

**Search Categories**: ANIMALS, ARTS, BIRTHDAYS, CITYSCAPES, CRAFTS, DOCUMENTS, FASHION, FLOWERS, FOOD, GARDENS, HOLIDAYS, HOUSES, LANDMARKS, LANDSCAPES, NIGHT, PEOPLE, PERFORMANCES, PETS, RECEIPTS, SCREENSHOTS, SELFIES, SPORT, TRAVEL, UTILITY, WEDDINGS, WHITEBOARDS.

### Upload

```bash
uv run scripts/google_photos.py upload \
  --file "./hologram.jpg" --description "Leia's holographic message" --album "ALBUM_ID"
```

### Albums

```bash
uv run scripts/google_photos.py albums
uv run scripts/google_photos.py album-get --id "ALBUM_ID"
uv run scripts/google_photos.py album-create --title "Tatooine Sunsets"
uv run scripts/google_photos.py album-add --album "ALBUM_ID" --items "ITEM_1" "ITEM_2"
uv run scripts/google_photos.py album-remove --album "ALBUM_ID" --items "ITEM_1"
```

---

## Upgrading from v1 (per-service skills)

If you previously installed the separate `gmail`, `google-calendar`, `google-contacts`, `google-drive`, and/or `google-photos` skills:

```bash
# Dry run — shows what will change without modifying anything
bash scripts/upgrade.sh --dry-run

# Run the migration
bash scripts/upgrade.sh
```

The upgrade script:

1. **Consolidates credentials** — copies `token.json` and `credentials.json` from any legacy dir (`~/.gmail_credentials/`, etc.) into `~/.google_workspace/`.
2. **Removes old skill installations** — deletes old per-service skill directories from `.agent/skills/` if present.
3. **Preserves legacy dirs** — does not delete `~/.gmail_credentials/` etc., so existing tools that depend on them still work.
4. **Verifies auth** — confirms the unified token works for all services.

---

## JSON Output

All commands produce JSON for easy parsing. See the individual service sections above for output schemas.
