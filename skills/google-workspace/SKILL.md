---
name: google-workspace
version: 1.0.0
description: "Access Google Workspace (Drive, Docs, Sheets, Gmail, Calendar, Chat, Meet, Admin) via the `gws` CLI. Use this skill when the user wants to read, write, or manage Google Docs, Sheets, Drive files/folders, Gmail messages, Calendar events, or any other Google Workspace resource. Triggers on: Google Docs, Google Sheets, Google Drive, Google Calendar (via gws), Google Chat, Google Meet, spreadsheet operations, document editing, file uploads, sharing permissions, Gmail triage, or any mention of `gws` commands."
---

# Google Workspace CLI (`gws`)

One CLI for all of Google Workspace. Reads Google's Discovery Service at runtime, so new API endpoints are available automatically.

## Prerequisites

- `gws` binary on `$PATH` (install: `pnpm add -g @googleworkspace/cli`)
- Authenticated: `gws auth login` (OAuth via browser)
- Auth status: `gws auth status`

## Reference

All gws skill files are symlinked from the upstream Gemini extension at:
`./gws-skills/`

Key references:
- `./gws-skills/gws-shared/SKILL.md` - Auth, global flags, security rules
- `./gws-skills/gws-drive/SKILL.md` - Drive file/folder operations
- `./gws-skills/gws-docs/SKILL.md` - Google Docs read/write
- `./gws-skills/gws-docs-write/SKILL.md` - Append text to docs
- `./gws-skills/gws-sheets/SKILL.md` - Sheets operations
- `./gws-skills/gws-gmail/SKILL.md` - Gmail operations
- `./gws-skills/gws-calendar/SKILL.md` - Calendar operations
- `./CONTEXT.md` - Core syntax and usage patterns

Read the relevant skill file before executing commands you haven't used before.

## Core Syntax

```bash
gws <service> <resource> [sub-resource] <method> [flags]
```

### Common Flags

| Flag | Description |
|------|-------------|
| `--params '<JSON>'` | URL/query parameters |
| `--json '<JSON>'` | Request body (POST/PUT/PATCH) |
| `--fields '<MASK>'` | Limit response fields (critical for context window) |
| `--page-all` | Auto-paginate (NDJSON output) |
| `--upload <PATH>` | File for multipart uploads |
| `--output <PATH>` | Save binary downloads |
| `--dry-run` | Validate without calling the API |

### Schema Discovery

If you don't know the payload structure, check the schema first:

```bash
gws schema <service>.<resource>.<method>
# Example: gws schema drive.files.list
# Example: gws schema docs.documents.batchUpdate
```

## Common Patterns

### Drive - List/Search Files

```bash
gws drive files list --params '{"q": "name contains \"Report\"", "pageSize": 10}' --fields "files(id,name,mimeType)"
```

### Drive - Create Folder

```bash
gws drive files create --json '{"name": "My Folder", "mimeType": "application/vnd.google-apps.folder"}'
```

### Drive - Move File to Folder

```bash
gws drive files update --params '{"fileId": "FILE_ID", "addParents": "FOLDER_ID"}'
```

### Drive - Export Google Doc as Plain Text

```bash
gws drive files export --params '{"fileId": "DOC_ID", "mimeType": "text/plain"}' --output /tmp/doc.txt
```

### Docs - Read Document

```bash
gws docs documents get --params '{"documentId": "DOC_ID", "fields": "title,body"}'
```

### Docs - Write to Document (batchUpdate)

For inserting/replacing text, build a JSON payload file to avoid shell escaping:

```python
import json
payload = {
    "requests": [
        {"insertText": {"location": {"index": 1}, "text": "Hello world"}}
    ]
}
with open('/tmp/payload.json', 'w') as f:
    json.dump(payload, f)
```

```bash
gws docs documents batchUpdate --params '{"documentId": "DOC_ID"}' --json "$(cat /tmp/payload.json)"
```

### Docs - Append Text (Helper)

```bash
gws docs +write --document DOC_ID --text 'Text to append'
```

### Sheets - Read Cells

```bash
gws sheets spreadsheets values get --params '{"spreadsheetId": "ID", "range": "Sheet1!A1:C10"}'
```

### Gmail - Search Messages

```bash
gws gmail users messages list --params '{"userId": "me", "q": "from:someone@example.com"}'
```

## Agentic Workflow & Vibe Coding

- **Iterative API Execution:** Do not expect complex Workspace API payloads to succeed on the first try. Draft the payload, run it with the `--dry-run` flag, review the expected changes, isolate any schema errors, fix ONE field at a time, and re-test until the payload is valid before executing the actual mutation.
- **Vibe Coding:** Save your complex JSON payloads or script sequences to local files and commit them before running irreversible batch operations across Drive or Docs.

## Rules

- **Context window protection**: ALWAYS use `--fields` on list/get to avoid massive JSON responses
- **Dry-run first**: Use `--dry-run` for destructive operations before executing
- **Confirm writes**: Ask the user before executing write/delete commands
- **Shell escaping**: For Sheets ranges with `!`, use single quotes to prevent bash history expansion
- **Large payloads**: Write JSON to a temp file and use `$(cat /tmp/file.json)` instead of inline
