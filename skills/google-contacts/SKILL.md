---
name: google-contacts
description: Interact with Google Contacts to search and create contacts.
---

# Google Contacts Skill

This skill allows the AI to manage the user's Google Contacts.

## Features

- **Search**: Find people by name, email, or phone.
- **Create**: Add new contacts to the address book.

## Prerequisites

1.  **Google Cloud Project** with **Google People API** enabled.
2.  **OAuth 2.0 Credentials** (`credentials.json`) in `~/.contacts_credentials/`.

## Setup

1.  **Recommended (gcloud ADC)**:

    ```bash
    gcloud auth application-default login --scopes https://www.googleapis.com/auth/contacts
    ```

    Then verify:

    ```bash
    uv run skills/google-contacts/scripts/contacts.py search --query "Test"
    ```

2.  **Alternative (credentials.json)**:
    - Place `credentials.json` in `~/.contacts_credentials/`.
    - Run `uv run skills/google-contacts/scripts/contacts.py setup`

## Usage

### 1. Search Contacts

```bash
# Find Han Solo
uv run skills/google-contacts/scripts/contacts.py search --query "Han Solo"
```

### 2. Create Contact

```bash
uv run skills/google-contacts/scripts/contacts.py create \
  --first "Lando" \
  --last "Calrissian" \
  --email "lando@cloudcity.com" \
  --phone "555-0123"
```

## JSON Output

```json
[
  {
    "name": "Han Solo",
    "email": "captain@falcon.net",
    "phone": "555-0987",
    "resourceName": "people/123456789"
  }
]
```
