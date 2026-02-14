---
name: google-calendar
description: Interact with Google Calendar to list and create events.
---

# Google Calendar Skill

This skill allows the AI to manage the user's Google Calendar.

## Features

- **List**: See upcoming events to avoid conflicts.
- **Create**: Schedule new events (meetings, reminders).

## Prerequisites

1.  **Google Cloud Project** with **Google Calendar API** enabled.
2.  **OAuth 2.0 Credentials** (`credentials.json`) in `~/.calendar_credentials/`.

## Setup

1.  Place `credentials.json` in `~/.calendar_credentials/`.
2.  **Recommended (Zero Setup)**:

    ```bash
    uv run skills/google-calendar/scripts/calendar.py setup
    ```

    _Alternatively (Standard PiP)_:

    ```bash
    pip install -r skills/google-calendar/requirements.txt
    python3 skills/google-calendar/scripts/calendar.py setup
    ```

## Usage

### 1. List Upcoming Events

```bash
uv run skills/google-calendar/scripts/calendar.py list --limit 5
```

### 2. Create Event

```bash
# Schedule a Council Meeting
uv run skills/google-calendar/scripts/calendar.py create \
  --summary "Jedi Council Meeting" \
  --start "2026-05-04T10:00:00" \
  --end "2026-05-04T11:00:00" \
  --description "Discussing the prophecy."
```

## JSON Output

```json
[
  {
    "summary": "Podrace",
    "start": { "dateTime": "2026-05-04T14:00:00Z" },
    "end": { "dateTime": "2026-05-04T16:00:00Z" }
  }
]
```
