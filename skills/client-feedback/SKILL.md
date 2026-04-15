---
name: client-feedback
description: >-
  Process client feedback emails into tracked GitHub issues, investigate and fix
  issues in the codebase, and draft response emails. Use this skill whenever the
  user mentions client feedback, stakeholder review, QA feedback, launch feedback,
  or wants to process emails from a client domain into actionable work items.
  Also use when the user says things like "check emails from [domain]",
  "process feedback from [person]", "what did [client] say about the site",
  or "turn that feedback into issues". This skill covers the full loop from
  reading emails through fixing code through drafting responses.
---

# Client Feedback Processor

Transform client feedback emails into tracked, investigated, and resolved GitHub issues with professional response emails.

This workflow handles the full feedback loop: **Intake > Triage > Investigate > Fix > Respond**. Each phase builds on the last. Do not skip phases or batch them out of order.

## Why this workflow matters

Client feedback arrives messy -- forwarded chains, inline screenshots, multiple people's observations in one thread, vague descriptions. Without a systematic process, items get lost, screenshots can't be referenced later, and the client never hears back about what was fixed. This workflow ensures every piece of feedback is captured, investigated against the actual codebase, and responded to with specifics (not vague "we'll look into it" replies).

## Phase 1: Intake

### 1.1 Search and read emails

```
Gmail MCP: gmail_search_messages  q:"from:<client-domain>"
Gmail MCP: gmail_read_message     for each result
```

Read ALL emails from the feedback period. Client feedback often arrives across multiple threads -- a main feedback email, follow-ups with screenshots, forwarded notes from other team members. Read them all before triaging.

### 1.2 Download and view attachments

Email screenshots are critical context. Inline images (CID references) get stripped in plain-text views, so you must download them via the Gmail API.

```bash
# Get message with full payload to find attachment IDs
gws gmail users messages get \
  --params '{"userId": "me", "id": "<MESSAGE_ID>", "format": "full"}' \
  2>/dev/null > /tmp/email.json

# Parse attachment IDs from the nested parts structure
# Parts with body.attachmentId are downloadable attachments

# Download each attachment
gws gmail users messages attachments get \
  --params '{"userId": "me", "messageId": "<MESSAGE_ID>", "id": "<ATTACHMENT_ID>"}' \
  2>/dev/null | python3 -c "
import json, base64, sys
text = sys.stdin.read()
start = text.index('{')
data = json.loads(text[start:])
raw = data.get('data', '').replace('-', '+').replace('_', '/')
with open('/tmp/screenshot.png', 'wb') as f:
    f.write(base64.b64decode(raw + '=='))
"
```

**View every screenshot** with the Read tool before triaging. Screenshots often reveal the real issue is different from what the text describes (e.g., "buttons don't work" might actually be informational badges with hover styles, not broken buttons).

### 1.3 Organize feedback by person and thread

Before creating issues, organize the raw feedback into a structured summary grouped by:
- **Person** who gave the feedback (may be forwarded by someone else)
- **Email thread** (for drafting responses later)
- **Category** (bug, content fix, data correction, question)

Present this summary to the user before proceeding to issue creation.

## Phase 2: Triage -- Create GitHub Issues

### 2.1 Create labels (if they don't exist)

```bash
gh label create feedback     --color 0075ca --description "Client feedback items"
gh label create provider-data --color 7B2D8B --description "Data corrections"
gh label create content      --color 0E8A16 --description "Copy and content fixes"
# bug and question usually exist already
```

### 2.2 Create one issue per feedback item

One issue per item, not one per email. This matters because:
- Individual items can be closed independently with `fixes #N` in commits
- Nothing gets buried in a long checklist
- Items that need client input can be tagged `question` and filtered separately

Each issue body should include:

```markdown
## Source
[Person name] via [forwarding person if applicable] ([date])

## Details
[What was reported -- be specific]

## Action
[What needs to happen, or "Needs answer from [person]" for questions]
```

Apply labels based on category:
| Label | When |
|-------|------|
| `feedback` | All client feedback items |
| `bug` | Broken functionality, errors, 404s |
| `content` | Copy, translation, spelling, wording |
| `provider-data` | Provider locations, photos, credentials |
| `question` | Needs client answer before we can act |

### 2.3 Map issues back to email threads

Keep a mental (or written) map of which issues came from which email thread. You will need this in Phase 5 when drafting responses organized by thread.

## Phase 3: Investigate

For each issue, verify the feedback against the actual codebase before acting. Client descriptions are often imprecise -- "the search is broken" might mean the search works but the results link to 404s.

### Investigation patterns

**Content issues** (spelling, wording, missing info):
```
Grep for the exact text in content/ directory
Read the file to see surrounding context
Check both EN and ES versions
```

**Provider data** (wrong location, missing photo):
```
Find the provider content file in content/providers/
Check the field values (office, headshot_url, etc.)
Verify referenced files exist and aren't placeholders (check file size!)
```

**Broken functionality** (links, maps, video):
```
Trace the route/component chain
Check CSP headers in proxy/middleware
Verify environment variables and API keys
Check if the issue is a missing page route vs broken link
```

**Missing assets** (photos, videos):
```
Check if placeholder files exist (often tiny files, e.g., 9 bytes)
Browse the legacy/old site with Playwright to recover assets
Download at high resolution and replace placeholders
```

### Recovering assets from legacy sites

When provider photos or other assets are missing, check the old site:

```
Playwright: browser_navigate to old site
Playwright: browser_evaluate to find images by provider name
Playwright: browser_take_screenshot to verify visually
curl to download at high resolution (adjust Wix URL params for size)
```

## Phase 4: Fix and Track

### 4.1 Fix what you can

Make fixes directly in the codebase. Common fixes:
- Content: Edit markdown/JSON in `content/` directory
- Spacing/typos: Direct string replacement
- CSP issues: Update security headers
- Provider data: Update provider content files
- Missing assets: Download and replace placeholder files

### 4.2 Update issues with findings

For each investigated issue, add a comment with:
- What you found (file paths, line numbers, current values)
- Root cause analysis (especially for bugs)
- What you fixed, or what still needs to happen

Close issues that are fully resolved. Leave open issues that need client input or further work.

### 4.3 Add screenshots to issues

If screenshots are relevant to open issues, commit them to the repo (e.g., `_resources/feedback/<date>/`) and reference them in issue comments using raw GitHub URLs:

```markdown
![description](https://raw.githubusercontent.com/<owner>/<repo>/main/_resources/feedback/<date>/<file>.png)
```

This provides visual context for anyone working on the issue later.

### 4.4 Commit and push

Group all fixes into a single descriptive commit that references closed issues:

```
fix: address client feedback from <date>

Content fixes:
- [list each fix]

Provider data:
- [list each fix]

Infrastructure:
- [list each fix]

Closes #X, #Y, #Z
```

## Phase 5: Respond

### 5.1 Draft response emails

Create Gmail drafts as **thread replies** (use `threadId`), not new emails. One reply per thread, organized as:

```
FIXED (will be live on next deploy):
- [item]: [what we did]

INVESTIGATED -- NEED YOUR INPUT:
- [item]: [what we found + specific question]
```

The response structure for each item should cover:
1. **What we understood** the feedback to say
2. **What we discovered** investigating it (this is the value-add -- show the client you actually looked into it, didn't just file a ticket)
3. **Action taken** or planned
4. **Outstanding questions** if any (be specific -- not "what do you want?" but "should we list those hospitals for GYN-only, or leave them off since there's no OB?")

### 5.2 Inline proof screenshots in the reply

When a fix has deployed and you want to show the client proof (e.g., "here's the before-and-after"), attach screenshots **inline** so they render in the email body rather than as download links. This is "pretty standard to add proof" per client expectations, and mirrors how the client sent you their screenshots in the first place.

**Do not** base64-inline the image as a `data:` URI in HTML — Gmail's image proxy strips many data URIs, and even when it works, the resulting raw message can exceed shell argv limits when passed to `gws --json`. The MCP `gmail_create_draft` tool has no attachment parameter.

**Do** use `gws`'s native Gmail multipart upload. The flow:

1. Build a `multipart/related` MIME message in Python with the HTML body plus a `MIMEImage` part. Give the image a `Content-ID` header. Reference it from the HTML via `<img src="cid:YOUR-CID">`.
2. Write the raw RFC822 message to a temp file.
3. Call `gws gmail users drafts create` with `--upload PATH --upload-content-type message/rfc822`. This uploads the whole raw message as multipart-upload media, bypassing any argv size limit.

```python
import subprocess, json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

HTML = """<div>
  ...
  <img src="cid:fix-screenshot" alt="..." style="max-width:512px;"/>
  ...
</div>"""

msg = MIMEMultipart("related")
msg["To"] = "client@example.com"
msg["From"] = "you@example.com"
msg["Subject"] = "..."
msg.attach(MIMEText(HTML, "html"))

with open("/path/to/screenshot.png", "rb") as f:
    img = MIMEImage(f.read(), "png")
img.add_header("Content-ID", "<fix-screenshot>")
img.add_header("Content-Disposition", "inline", filename="fix.png")
msg.attach(img)

raw_path = "/tmp/reply-draft.eml"
with open(raw_path, "wb") as f:
    f.write(msg.as_bytes())

subprocess.run([
  "bash", "-lc",
  f"gws gmail users drafts create "
  f"--params '{json.dumps({'userId':'me','uploadType':'multipart'})}' "
  f"--json '{{}}' "
  f"--upload {raw_path} --upload-content-type message/rfc822"
])
```

Alternative for larger or multiple screenshots: upload to Google Drive via `gws drive files create --upload PATH`, set `anyone/reader` permissions via `gws drive permissions create`, then paste the `webViewLink` as a text link in the body. Drive links survive cleanly across clients and let the recipient view full-resolution without bloating the email.

### 5.3 Private repo considerations

If the GitHub repo is private, handle all issue tracking internally and communicate with the client via email only. Don't ask non-technical clients to use GitHub. The email responses ARE the client-facing deliverable.

## Agentic Workflow & Vibe Coding

- **Iterative Resolution:** Do not expect to fix all client feedback perfectly on the first try. Draft a fix for one issue, review the local preview, isolate any specific visual or functional regressions, refine the component or content ONE variable at a time, and verify before moving to the next ticket.
- **Vibe Coding:** Commit your working code fixes locally with `fixes #N` *before* drafting the final response emails, ensuring the codebase accurately reflects the promised resolution.

## Checklist

Before marking the workflow complete, verify:

- [ ] Every feedback item has a GitHub issue
- [ ] Every issue has been investigated (not just created)
- [ ] Fixed issues are closed with comments explaining the fix
- [ ] Open issues have investigation comments and screenshots where applicable
- [ ] All fixes are committed and pushed
- [ ] Draft reply emails cover every item from every email thread
- [ ] Questions for the client are specific and actionable
- [ ] The user has reviewed the draft emails before sending
