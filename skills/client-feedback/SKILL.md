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

This workflow handles the full feedback loop: **Intake > Ack > Triage > Investigate > Fix > Respond**. Each phase builds on the last. Do not skip phases or batch them out of order.

## Why this workflow matters

Client feedback arrives messy: forwarded chains, inline screenshots, multiple people's observations in one thread, vague descriptions, rapid-fire follow-ups during a single review session. Without a systematic process, items get lost, screenshots can't be referenced later, and the client never hears back about what was fixed. This workflow ensures every piece of feedback is captured, investigated against the actual codebase, and responded to with specifics (not vague "we'll look into it" replies).

## Phase 0: Situational awareness (don't skip)

Before doing anything, know what's already been said and done. This prevents duplicate commitments, contradicting yourself, and re-filing already-closed work.

### 0.1 Check sent items
```
Gmail MCP: gmail_search_messages  q:"in:sent to:<client-email> after:<last-cycle-date>"
```
Read your own most recent sends. Did you already promise something on this thread? Is there a thread you haven't replied to yet? This establishes the baseline.

### 0.2 Check existing GitHub issues
```bash
gh issue list --state all --limit 100 --search "created:<date-range>" --json number,title,state,labels
```
Prior sessions (yours or another Claude's) may have filed issues for some of this. Don't create duplicates. When existing issues overlap with the new batch, update the existing one rather than opening a new one.

### 0.3 Check the in-repo tracker
Check `_resources/feedback/*/` for prior-batch `_index.md` files. These are the permanent, commit-tied record. They often show partial work, open questions, and commit SHAs you need to reference.

### 0.4 Check git log for this cycle
```bash
git log --oneline --since="<date>" --author=<your-email-domain-or-coauthor>
```
Recent commits may already resolve items in the new batch. Reference them by SHA in your response.

## Phase 1: Intake

### 1.1 Search and read emails

```
Gmail MCP: gmail_search_messages  q:"from:<client-domain> after:<date>"
Gmail MCP: gmail_read_message     for each result
```

Read ALL emails from the feedback period, not just the newest. Client feedback often arrives across multiple threads during a single review session. Skip Gmail "reacted" messages (they show as UNREAD but are just emoji reactions, not new content — identifiable by the `"Sarah X reacted to your message"` snippet).

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
- **Question vs. statement** — mark each item as either "client asked X" (needs our answer) or "client asserted X" (needs us to verify and act). Rapid scanners often phrase statements rhetorically, so don't mistake a parenthetical fact ("she's at Shea now") for a question.

Present this summary to the user before proceeding to issue creation.

## Phase 2: Ack (when the client is still typing)

If the client is actively sending feedback (multiple emails within a few hours) or the cycle is on a tight deadline (launch week, demo prep), **send a short acknowledgment first** before doing full investigation. This keeps the client feeling heard while you work.

Ack content:
- Confirm receipt of every email you've seen
- Name the 1-3 things already fixed (if anything was resolved in prior sessions or you can spot-fix in under 5 minutes)
- Preview the specific asks you'll need from them (blockers you've identified) so they can gather info in parallel
- Promise a full reply with a timeframe ("later today" or "first thing tomorrow")
- Plain text, no inline images, no branded template

Then do the full loop and send the full response later. This pattern matters when the feedback is too large to triage fast but too important to leave un-acknowledged.

## Phase 3: Triage — GitHub issues are required

GitHub issues and the in-repo tracker are both required. They serve different purposes:
- **GitHub issues**: active work board, assignable, searchable by label, closed by commit, one row per item.
- **In-repo tracker** (`_resources/feedback/<date>/_index.md`): permanent record, tied to commits, survives issue migrations, includes before/after screenshot paths, cross-references GH issue numbers.

Do not substitute one for the other. When the repo has a private/internal tracker, GH issues still get filed; when issues exist, the tracker still gets written.

### 3.1 Create labels (if they don't exist)

```bash
gh label create feedback       --color 0075ca --description "Client feedback items"
gh label create provider-data  --color 7B2D8B --description "Data corrections"
gh label create content        --color 0E8A16 --description "Copy and content fixes"
gh label create design         --color 7B68EE --description "Design and UI improvements"
# bug and question usually exist already
```

### 3.2 Create one issue per feedback item

One issue per item, not one per email. This matters because:
- Individual items can be closed independently with `fixes #N` in commits
- Nothing gets buried in a long checklist
- Items that need client input can be tagged `question` and filtered separately

**Critical `gh` command syntax** (from painful experience):
- `gh issue create` prints the URL on stdout directly — do NOT pass `--json url -q .url`, that flag doesn't exist on this subcommand.
- `gh issue create` must run from inside the repo directory. `cd /tmp` breaks git context; the command fails with `fatal: not a git repository`.
- Use `--body-file <path>` for multi-line bodies to avoid shell escaping hell. Write bodies to `/tmp/feedback-<date>/issues/<code>.md`.

```bash
cd /path/to/repo    # must be the repo, not /tmp
url=$(gh issue create \
  --title "<category>: <concise title>" \
  --body-file /tmp/feedback-<date>/issues/item.md \
  --label feedback --label content)
echo "filed: $url"
```

### 3.3 Issue body template

```markdown
## Reported by
[Person name] — [date] "[email subject]" (thread [threadId])

## Issue
[Verbatim quote if short, paraphrase if long]

## Source state (verified)
[What you found in code — file paths, line numbers, current values. If not investigated yet, write "Not investigated."]

## Root cause
[If bug or unexpected behavior — what in the codebase causes this]

## Action / Options
[What will fix it, or options needing client input]

## Status
[Open / awaiting client / in progress / blocked by #N]
```

Apply labels based on category:
| Label | When |
|-------|------|
| `feedback` | All client feedback items (always add) |
| `bug` | Broken functionality, errors, 404s |
| `content` | Copy, translation, spelling, wording |
| `design` | Visual / layout / component UI |
| `provider-data` | Provider locations, photos, credentials |
| `question` | Needs client answer before we can act |

### 3.4 Map issues back to email threads

Keep a written map in the in-repo `_index.md` of which issues came from which email thread. You will need this in Phase 6 when drafting responses organized by thread.

## Phase 4: Investigate

For each issue, verify the feedback against the actual codebase before acting. Client descriptions are often imprecise — "the search is broken" might mean the search works but the results link to 404s.

### 4.1 Verify globally, not just at the surface the client saw

This is the most common failure mode. When the client says "remove Victoria Schooler," the instinct is to delete her bio file and call it done. But her name probably appears in roster listings, navigation, search indexes, and schema markup. If you claim "fully removed" after fixing only one surface, the client catches you on the next tour.

Before declaring a fix complete:
```bash
# Grep the ENTIRE codebase for the subject of the claim
grep -rn "<name or text>" content/ src/ public/ docs/
```
Fix every occurrence the client would reasonably encounter. Stale build artifacts (search indexes, generated JSON) that regenerate on build are OK to leave; anything that appears in committed source must be addressed.

### 4.2 Investigation patterns

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
Check if the "location" named is actually a hospital vs. an office — different data models
```

**Broken functionality** (links, maps, video):
```
Trace the route/component chain
Check CSP headers in proxy/middleware
Verify environment variables and API keys
Check if the issue is a missing page route vs broken link
Check redirect routes (permanentRedirect calls can silently filter)
```

**Missing assets** (photos, videos):
```
Check if placeholder files exist (often tiny files, e.g., 9 bytes)
Browse the legacy/old site with Playwright to recover assets
Download at high resolution and replace placeholders
```

### 4.3 Recognize architectural root causes

When the same issue surfaces in multiple forms across a feedback cycle, it's an architectural problem, not a surface bug. Examples:
- "Provider count shows 60+ here, 70+ there, 61+ somewhere else" → symptoms of hardcoded counts. Fix at the root: derive from the collection.
- "Provider X's photo looks off in Y crop" (repeated across multiple providers) → hardcoded crop rule. Fix at the root: add a CMS-editable focal point.
- "Links from brand page go to a filtered directory that excludes this brand's own providers" → architectural routing drift between brand pages and brand-specific directory routes.

Name the pattern explicitly in the relevant issue body and propose the architectural fix as a follow-up. Don't keep playing whack-a-mole.

### 4.4 Recovering assets from legacy sites

When provider photos or other assets are missing, check the old site:

```
Playwright: browser_navigate to old site
Playwright: browser_evaluate to find images by provider name
Playwright: browser_take_screenshot to verify visually
curl to download at high resolution (adjust Wix URL params for size)
```

## Phase 5: Fix and Track

### 5.1 Fix what you can

Make fixes directly in the codebase. Common fixes:
- Content: Edit markdown/JSON in `content/` directory
- Spacing/typos: Direct string replacement
- CSP issues: Update security headers
- Provider data: Update provider content files
- Missing assets: Download and replace placeholder files

### 5.2 Write the in-repo tracker first, then update issues

The tracker is `_resources/feedback/<date>/_index.md`. It lives in the repo, gets committed alongside the fixes, and becomes the canonical record even if GitHub issues later migrate. Structure:

```markdown
# <Client> Feedback — <date range>

Status: X Fixed, Y Open, Z architectural follow-ups.

Source: <list of email threads with IDs>

## Batch 1 — <thread name>
| Code | Item | Status | Commit | After shot |
|---|---|---|---|---|
| A | ... | Done | abc1234 | after/crop-A.png |

## GitHub issue cross-reference
| Code | Issue | State |
|---|---|---|
| A | #128 | Closed |

## Reply drafts / sent
| Thread | Subject | Draft / sent ID |
```

### 5.3 Update issues with findings

For each investigated issue, add a comment with:
- What you found (file paths, line numbers, current values)
- Root cause analysis (especially for bugs)
- What you fixed, or what still needs to happen
- Link to relevant commit: `[abc1234](https://github.com/<owner>/<repo>/commit/abc1234)`

Close issues that are fully resolved. Leave open issues that need client input or further work.

### 5.4 Add screenshots to issues

Commit before/after screenshots to `_resources/feedback/<date>/` and reference them in issue comments using raw GitHub URLs:

```markdown
![description](https://raw.githubusercontent.com/<owner>/<repo>/main/_resources/feedback/<date>/after/<file>.png)
```

These render inline in GitHub issue comments (no separate click-through to Drive). For before/after pairs, use two images stacked with labels.

### 5.5 Commit and push

Commit incrementally as logical chunks complete — NOT in one big batch at the end. Reference closed issues in commit messages:

```
fix(<area>): <concise title>

<paragraph explaining what and why>

Closes #X, #Y, #Z

Co-Authored-By: <your coauthor line>
```

Push when the user asks or clearly implies it (e.g., wants to reply to client and staging needs to match the email's claims).

## Phase 6: Respond

### 6.1 Check for new emails before drafting

Before you start writing the response, re-check Gmail. Clients sending rapid-fire feedback often send a second or third email during the hour you were investigating. Drafting a response based on only the first email means the client's follow-ups look un-acknowledged when they open it.

### 6.2 Pick the reply shape

- **One reply per thread** is the default (use `threadId` to thread correctly).
- **Consolidated reply + acks** when the client sent multiple threads during one review session on the same broad topic: send the full response on the newest thread, then 2-line "covered in the consolidated reply" acks on the earlier threads. Confirm shape with user before writing.

### 6.3 Response structure

```
FIXED (will be live on next deploy):
- [item]: [what we did]

ALSO CHANGED (not flagged but relevant):
- [proactive fix]: [reason]

COMING NEXT:
- [architectural follow-up]: [why it closes a whole class of drift]

NEED YOUR INPUT:
- [question]: [specific options with tradeoffs]
```

Per-item content should cover:
1. **What we understood** the feedback to say (briefly, letter-code preferred)
2. **What we did** (specific — file path, commit SHA if meaningful to client)
3. **Outstanding questions** if any (specific — not "what do you want?" but "should we list those hospitals for GYN-only, or leave them off since there's no OB?")

**Anti-tell discipline**: strip meta-framing ("catching up on," "while in there," "we think"), em dashes, "just / simply / actually / pretty / really," and apologetic openers ("sorry for the delay"). Write cold — the client reads the email cold.

### 6.4 Inline before/after proof

Inline before/after image pairs in the email body. The client sent you their screenshots; reply in kind.

**Do not** base64-inline the image as a `data:` URI in HTML — Gmail's image proxy strips many data URIs, and even when it works, the resulting raw message can exceed shell argv limits when passed to `gws --json`. The MCP `gmail_create_draft` tool has no attachment parameter.

**Do** use `gws`'s native Gmail multipart upload. The flow:

1. Build a `multipart/related` MIME message in Python with the HTML body plus `MIMEImage` parts. Give each image a `Content-ID` header. Reference them from the HTML via `<img src="cid:YOUR-CID">`.
2. Set `In-Reply-To` and `References` headers to the original message ID for proper threading.
3. Write the raw RFC822 message to a temp file.
4. Call `gws gmail users drafts create` with `--upload PATH --upload-content-type message/rfc822` and `--json '{"message":{"threadId":"<threadId>"}}'`. The threadId in the JSON body is belt-and-suspenders alongside the Message-ID headers.

```python
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

ORIG_MSG_ID = "<the Message-ID header from the email you're replying to>"
ORIG_REFS = "<the References header from that email>"

msg = MIMEMultipart("related")
msg["To"] = "Client <client@example.com>"
msg["From"] = "You <you@example.com>"
msg["Subject"] = "Re: Original subject"
msg["In-Reply-To"] = ORIG_MSG_ID
msg["References"] = f"{ORIG_REFS} {ORIG_MSG_ID}"
msg.attach(MIMEText(HTML, "html"))

for cid, path in [("before-A", "before.jpg"), ("after-A", "after.png")]:
    with open(path, "rb") as f:
        img = MIMEImage(f.read(), "jpeg" if path.endswith(".jpg") else "png")
    img.add_header("Content-ID", f"<{cid}>")
    img.add_header("Content-Disposition", "inline", filename=os.path.basename(path))
    msg.attach(img)

with open("/tmp/reply.eml", "wb") as f:
    f.write(msg.as_bytes())
```

Upload as a draft:
```bash
gws gmail users drafts create \
  --params '{"userId":"me","uploadType":"multipart"}' \
  --json '{"message":{"threadId":"<THREAD_ID>"}}' \
  --upload /tmp/reply.eml \
  --upload-content-type message/rfc822
```

### 6.5 Revise drafts atomically — delete the superseded one

When iterating a draft (v2 → v3 → v4), always **delete the old draft** before uploading the new one. Multiple drafts on the same thread get confusing and the sender can accidentally send the wrong version.

```bash
gws gmail users drafts delete --params '{"userId":"me","id":"<OLD_DRAFT_ID>"}'
# then upload the new one
```

### 6.6 ALWAYS show the draft before sending

This is non-negotiable. Even if the user has just said "send" — **paste the draft body text back into the chat before actually sending**. The user should see the final wording, letter codes, inline image references, and sign-off before the message goes out.

Reason: drafts evolve during revision. The text the user approved five turns ago is not the text currently in the draft. A spot-check before send costs ten seconds and prevents sending a version with a wrong commit reference, a leftover placeholder, or a tone shift from voice-review.

**Rule**: "send" means "show me what will be sent, then send when I confirm" — not "send immediately."

### 6.7 Send

```bash
gws gmail users drafts send --params '{"userId":"me"}' --json '{"id":"<DRAFT_ID>"}'
```

Records the sent `messageId` immediately into the in-repo `_index.md` for traceability.

### 6.8 Signature policy

Keep the signature simple — typically just your first name or short professional sig. Avoid signing as "You (and Claude)" or similar unless the client relationship explicitly welcomes AI co-authorship. If you want to disclose AI pair-programming to the client, do it once in a dedicated conversation (Slack, call), not baked into every email signature.

### 6.9 Private repo considerations

If the GitHub repo is private, handle all issue tracking internally and communicate with the client via email only. Don't ask non-technical clients to use GitHub. The email responses ARE the client-facing deliverable; the in-repo tracker is Matthias/team-facing.

## Phase 7: Deploy discipline

The email you just sent claims things are fixed. The client will verify on staging. **Before sending, confirm**:
1. All fixes are committed
2. Commits are pushed to `origin/main` (or whatever branch deploys to the staging URL the client uses)
3. The deploy is triggered or live

If there's deploy lag (CI takes a few minutes), say so explicitly in the email: "deploy is building now, staging should match by the time you open this." Don't hope the client opens the email slowly enough for the deploy to finish.

## Patterns to watch for

### Verification theatre

Claiming "Done" at one surface doesn't mean the change is actually deployed. Grep globally before making claims. Every "Fixed" bullet in a client reply should be something you can point to in committed source on the deployed branch.

### Count drift (canonical example)

"Provider count shows 60+ here, 70+ there, 61+ somewhere else" = hardcoded counts spread across files. The architectural fix is to compute the count from the collection at build time. Don't keep updating individual strings on every cycle — they'll drift again next month.

### Routing drift between brand landing and brand-specific directory

If the codebase has both a brand landing page AND a brand-specific directory route (e.g., `/women-for-women` and `/women-for-women/providers`), check that they agree on filter behavior and CTAs. Common failure: landing page uses one View-All link, directory route hardcodes a different filter, client sees inconsistent provider counts on what looks like the same page.

### "Location" vs "hospital"

Clients conflate office (where they see the provider) with hospital (where the provider delivers). "Dr. X is at Shea now" might mean her office is Shea OR she delivers at Shea. Check both data models before acting.

## Checklist

Before marking the workflow complete, verify:

- [ ] Prior sent items and existing issues reviewed (Phase 0)
- [ ] Every feedback item has a GitHub issue (Phase 3)
- [ ] In-repo `_resources/feedback/<date>/_index.md` written and committed (Phase 5.2)
- [ ] Every issue has been investigated, not just filed
- [ ] "Fixed" claims grep-verified globally before being claimed (Phase 4.1)
- [ ] Architectural root causes named as such, not whack-a-moled (Phase 4.3)
- [ ] Closed issues have commit + after-shot evidence URL (Phase 5.3 / 5.4)
- [ ] Open issues have "awaiting X" comment linking to the sent client email
- [ ] All fixes committed AND pushed — deploy confirmed live or stated as in-flight in the reply
- [ ] Draft reply covers every item from every email thread, including any rapid-fire follow-ups (Phase 6.1)
- [ ] Questions for the client are specific and actionable, with options when tradeoffs exist
- [ ] Anti-tell and voice discipline applied (Phase 6.3)
- [ ] Draft content shown to user before sending, even when user said "send" (Phase 6.6)
- [ ] Superseded drafts deleted before uploading revisions (Phase 6.5)
- [ ] Sent message IDs recorded in `_index.md` (Phase 6.7)
