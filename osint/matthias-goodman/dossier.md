# OSINT Dossier — Matthias Goodman (self-audit)

**Investigation type:** Self-OSINT. Subject = requester.
**Depth:** Standard
**Scope:** Public sources only. Defensive opsec lens — what is publicly findable, what could be tightened.
**Investigator:** Claude (osint skill v1.x), 2026-04-25.
**Disambiguation result:** Confirmed. The subject is Matthias Goodman, founder/principal of Generic Service (Phoenix, AZ); GitHub `Baphomet480`; LinkedIn `matthias-goodman-3a36961a0`. Explicitly *not* the Matthias Goodman at `linkedin.com/in/matthias-goodman-aa2b30153` (different person, ruled out — no shared discriminators). Multiple "Matthew Goodman" profiles also surfaced and were ruled out by spelling.

---

## Confirmed identity (Grade A)

| Attribute | Value | Anchor source |
|---|---|---|
| Real name | Matthias Goodman | Self-declared on GitHub profile `Baphomet480`, commit author on this repo |
| Primary brand | Generic Service ("Infrastructure that behaves") | `genericservice.app` (live site) |
| Location | Phoenix, AZ | `genericservice.app` content |
| GitHub handle | `Baphomet480` | `github.com/Baphomet480` (real name attached) |
| LinkedIn (canonical) | `linkedin.com/in/matthias-goodman-3a36961a0` | Direct outbound link from `genericservice.app` "Founder/Principal" reference |
| Account email | `matthiasgoodman@icloud.com` | Local CLAUDE.md memory file |
| Git commit identity | Matthias Goodman `<matthiasgoodman@gmail.com>` | `git config` + recent commits in `Baphomet480/claude-skills` |

The two-source rule is satisfied for every row: `genericservice.app` ↔ LinkedIn ↔ GitHub real-name field cross-confirm the identity, and the local repo's git config matches.

---

## Public business surface (Grade A)

**Generic Service** (`genericservice.app`) — stability-focused infrastructure consulting firm.

- **Tagline:** "Infrastructure that behaves." / "Stable, documented, and recoverable. The way it should have been built the first time."
- **Productized services with public pricing:**
  - vSphere Stabilization & Drift Control — $2,500
  - Reversible Migration Engineering — $2,500
  - Proof of Recovery Architecture — $2,000
  - Azure Guardrails & Governance — $2,500
  - Plus fractional architecture and IT assessments
- **Target market:** hybrid vSphere + Azure, healthcare (HIPAA), manufacturing, professional services
- **Engagement model:** "90% of our engagements involve an existing IT provider" — collaborative-with-MSP positioning, not displacement
- **Contact surface:** form-only ("You know if you need this"), no exposed phone or direct email
- **Domain WHOIS:** privacy-protected (default for `.app` TLD via Google). Good opsec.

---

## GitHub footprint (Grade A)

`github.com/Baphomet480` — Pro account, 7 public repos, 1 follower / 1 following, "Public Sponsor" badge.

| Repo | Lang | What it tells a researcher |
|---|---|---|
| `claude-skills` | Mixed (this repo) | Active in agentic-AI tooling; framework-agnostic Claude/Gemini skill distribution |
| `ninjaone-universal-installer` | PowerShell | Builds for NinjaOne RMM ecosystem — strong MSP signal |
| `autotask-mcp` | TypeScript | MCP server for Kaseya Autotask — strong MSP/PSA signal |
| `messages-app-mcp` | JavaScript | Personal automation — Apple Messages MCP |
| `signal-mcp-server` | Makefile | Personal automation — Signal MCP |
| `deploy-codex-crossplatform` | PowerShell | Cross-platform devops scripts |
| `tmate` (fork) | C | Terminal-sharing fork |

**Pattern read:** the public repo set tells a coherent story — MSP/RMM tooling (NinjaOne, Autotask) plus AI-agent infrastructure (claude-skills, multiple MCP servers). Consistent with the Generic Service consulting brand.

---

## Public skill distribution — drift signal (Grade B)

This repo's skills are indexed on `skills.rest` (third-party Claude skills directory). At least one skill — **`hugo-sveltia-cms`** — is currently published there, but it's **no longer present** in `skills/` of the local repo.

- Public URL: `skills.rest/skill/hugo-sveltia-cms` (still live as of 2026-04-25)
- Local presence: not in `ls skills/`
- Implication: deleted/renamed skills can persist in third-party caches indefinitely.

Two sources: skills.rest search-result snippet + local `ls skills/` confirms absence. Confidence B (only one external indexer confirmed; haven't checked `awesome-agent-skills` lists).

---

## Day-job signal — needs reconciliation (Grade C)

Google search snippet for `linkedin.com/in/matthias-goodman-3a36961a0/` shows the page title as **"Matthias Goodman — Senior Cloud Engineer — Candor"** (with a separate snippet labeling the same profile "Senior Project Engineer at Candor, Chandler, 78 connections").

Single self-published source (LinkedIn, not directly fetchable due to LinkedIn's anti-bot 999 response) + indirect confirmation through Google's title cache. **Cannot independently verify** whether this is current employment, prior employment with stale headline, or a moonlighting arrangement alongside Generic Service.

**This is the most reconcilable inconsistency in the public footprint** — a prospect doing diligence on Generic Service who clicks the LinkedIn link will see "Senior Cloud Engineer at Candor" and may form a confused picture of whether they're hiring a full-time founder or a side-gig consultant.

---

## Negative findings (Grade A)

These are things *not* found that would normally surface for a person with this footprint:

- **No public Twitter/X, Mastodon, or personal blog** indexed under "Matthias Goodman" + plausible discriminators.
- **Neither email** (`matthiasgoodman@icloud.com`, `matthiasgoodman@gmail.com`) appears in any indexed web content. Not checked against breach databases (out of scope; the user can self-check at HaveIBeenPwned).
- **No phone number, address, or family-member info** publicly tied to this identity through standard people-search dorks.
- **No appearances on standard MSP/IT-consulting podcasts, conference talks, or trade press** under either the personal name or the Generic Service brand.

This is a *quiet* footprint — intentional or not, it gives a researcher very little personal-life surface to mine.

---

## Hypotheses (not confirmed — keep separate from facts)

These are inferences I formed from the data but cannot directly cite to a source:

1. The `Baphomet480` handle was likely chosen for a non-professional context (gaming/forum era?) and reused for technical accounts. The numeric suffix and tone are inconsistent with the "Generic Service" brand voice. *Inference from naming style only — no source.*
2. Generic Service appears to be a **solo or near-solo practice** — the website lists no other named principals, the GitHub footprint is one person, and the LinkedIn profile shows 78 connections (low for an established multi-person firm). *Inference from absence of other named staff.*
3. The MSP-tooling repos (`ninjaone`, `autotask`) suggest the user has working relationships with at least one MSP that uses those platforms — possibly Candor, possibly the "existing IT provider" mentioned in 90% of GS engagements. *Inference from tool selection.*

---

## Defensive opsec — what could be tightened

Ordered by leverage, highest first:

### 1. The pseudonym is nominal — decide whether you want it real
GitHub handle `Baphomet480` looks pseudonymous, but:
- Profile "Name" field publicly displays "Matthias Goodman"
- Commit author is `Matthias Goodman <matthiasgoodman@gmail.com>` on every commit
- A casual searcher links handle ↔ real name in one click

**Action options:**
- **If pseudonym intentional:** create a separate git identity for that persona (`git config --local user.name "Baphomet"`, fresh email), and remove "Matthias Goodman" from the GitHub profile name field.
- **If pseudonym is just a vestigial handle:** rename the GitHub account to `MatthiasGoodman` (or `genericservice`) for brand coherence. The `Baphomet480` ↔ Generic Service link confuses prospects doing diligence.

### 2. LinkedIn headline reconciliation
If `Senior Cloud Engineer at Candor` is **current**, the genericservice.app link to that LinkedIn confuses the buyer. Either:
- Update the LinkedIn headline to "Founder, Generic Service" (or stack: "Senior Cloud Engineer at Candor • Founder, Generic Service")
- Or, if Candor is past, update the LinkedIn current-position section to reflect Generic Service.

### 3. Stale public skill cache
`skills.rest/skill/hugo-sveltia-cms` is still indexed though removed from the local repo. Periodic sweep:
```bash
# rough idea — adapt to your dist set
for skill in $(ls dist/ | sed 's/\.skill$//'); do echo "$skill"; done > .local-skills.txt
# manually compare against skills.rest, awesome-agent-skills, anthropic skills marketplace
```
A proper fix is to ask `skills.rest` to remove/refresh the entry, or add a `deprecated: true` flag in any future skill manifests so indexers know.

### 4. Email pattern
`matthiasgoodman@{icloud,gmail}.com` shares the same local-part across providers. If either appears in a future breach corpus, a determined searcher gets the other for free. Mitigation:
- Use plus-addressing for high-risk signups (`matthiasgoodman+vendorname@gmail.com`)
- Or stand up a catch-all forwarder on a personal domain (`me@goodman.example`) and pivot signups onto that.
This is a low-urgency hardening, not a current breach.

### 5. Repo discoverability vs. privacy is unclear
`Baphomet480/claude-skills` is **public, 0 stars, 0 forks**. If the goal is to be discovered (Generic Service marketing surface), add a README, topic tags (`claude-code`, `agent-skills`), and a license file. If the goal is to be a private working tree that happens to be public, consider making it private and using `dist/` as the only public artifact.

---

## Sources

- [github.com/Baphomet480](https://github.com/Baphomet480) — profile, real name attached
- [github.com/Baphomet480/claude-skills](https://github.com/Baphomet480/claude-skills) — repo metadata
- [genericservice.app](https://genericservice.app) — business identity, services, location, LinkedIn link-out
- LinkedIn profile `matthias-goodman-3a36961a0` (only via Google snippet — direct fetch blocked by LinkedIn anti-bot)
- [skills.rest/skill/hugo-sveltia-cms](https://skills.rest/skill/hugo-sveltia-cms) — third-party skill cache
- Local `git config` and `git log` in `~/github/claude-skills`
- Local `~/.claude/CLAUDE.md` memory (account email)

## Method notes

- LinkedIn returned HTTP 999 (anti-bot) on direct fetch; profile content is from Google's cached snippet.
- skills.rest returned HTTP 403 on direct fetch; presence confirmed from search snippet only.
- WHOIS on `genericservice.app` is privacy-protected at registrar (Google).
- No paid breach databases consulted. No HaveIBeenPwned check performed (recommend the user run their own).
- No active probing of GS infrastructure (DNS, ports, certs) performed beyond what is in the rendered website. Defensive scope.
