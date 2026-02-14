---
name: gmail
description: Interact with Gmail to search messages, read threads, and create drafts.
---

# Gmail Skill

This skill allows the AI to interact with the user's Gmail account.

## Features

- **Search**: Advanced filtering using Gmail query syntax (from, to, subjects, labels).
- **Read**: Fetch full message details, snippets, and bodies.
- **Draft**: Create draft emails for the user to review and send (safe mode).
- **Labels**: List available labels for filtering.

## Prerequisites

1.  **Google Cloud Project** with **Gmail API** enabled.
2.  **OAuth 2.0 Credentials** (`credentials.json`) downloaded from Google Cloud Console.

## Setup

1.  **Recommended (gcloud ADC)**:
    This method allows you to use your Google account without managing file paths.

    ```bash
    # Login with specific scopes for Gmail
    gcloud auth application-default login --scopes https://www.googleapis.com/auth/gmail.modify
    ```

    Then run the script:

    ```bash
    uv run skills/gmail/scripts/gmail.py verify
    ```

2.  **Alternative (credentials.json)**:
    - Place `credentials.json` in `~/.gmail_credentials/`.
    - Run `uv run skills/gmail/scripts/gmail.py setup`

## Usage

### 1. Search for Emails

Find emails matching specific criteria.

```bash
# Find unread emails from Obi-Wan
uv run skills/gmail/scripts/gmail.py search --query "from:obiwan@jedi.org is:unread"

# Find emails with attachments about plans
uv run skills/gmail/scripts/gmail.py search --query "has:attachment subject:plans"
```

### 2. Read Email Details

The search command returns a JSON list of messages. To read a specific message, the script fetches details automatically during search, but specific ID retrieval can be added if needed.

### 3. Create a Draft

**Always** use this instead of sending directly.

```bash
uv run skills/gmail/scripts/gmail.py draft \
  --to "yoda@dagobah.net" \
  --subject "Training Schedule" \
  --body "Master, when shall we begin the next session?"
```

## JSON Output Structure

The script outputs JSON for easy parsing.

**Search Result Example:**

```json
[
  {
    "id": "18e...",
    "snippet": "Help me, Obi-Wan Kenobi...",
    "from": "Leia Organa <leia@alderaan.gov>",
    "subject": "Urgent Message",
    "date": "Mon, 13 Feb 2026 10:00:00 -0700"
  }
]
```
