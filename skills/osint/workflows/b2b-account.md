# Workflow: B2B Account Intelligence

For sales discovery on a target account: what does this company do, who's the right person to talk to, what would they actually buy, what's their current situation, and is there a recent trigger to lead with.

This is the workflow tuned for B2B consulting and SaaS sales. It is **not** a generic company research workflow — it is opinionated about what's worth knowing for a sales conversation.

## Pre-flight

- Confirm the user has stated a hypothesis: *"I think [company] needs/buys [thing] and the right person is [role/name]."* If they don't have one, ask. Cold "tell me about Acme" research without a hypothesis usually wastes effort.
- Run the Four Gates from `SKILL.md`.
- Gate the depth. Quick (5–10 min) for triage; Standard (20–30 min) for an account you're going to actually pursue.

## Phase 1 — Account snapshot (5 min)

The minimum viable picture before any deeper dive:

- **Legal entity + parent.** Are we selling to the operating entity or do procurement decisions live at a holding company / PE owner?
- **What they do** — one sentence in plain language.
- **Size signal** — headcount band (1–10, 11–50, 51–200, 201–1000, 1000+) and rough geographic footprint.
- **Industry** — what NAICS / vertical, and whether it's regulated (healthcare, financial services, government).

## Phase 2 — Buying-center inference

Who actually decides on this kind of purchase at this kind of company?

- For a **company under 50 people**: usually the founder/CEO or a single ops/IT lead. One-stop shop.
- For a **50–200**: VP of [function], with budget approval at C-level. A 1–2 person buying group.
- For a **200–1000**: a director with budget, a VP for sign-off, a CIO/CFO for procurement. 3–5 people.
- For **1000+**: full procurement process, CIO + LOB exec + procurement + security review + legal. 6+ people, longer cycle.

Map the relevant titles for the offering being sold and look up each one on LinkedIn:

```
site:linkedin.com/in "[Company]" "[Title]"
site:linkedin.com/in "[Company]" ("VP" OR "Director") "[function]"
```

For each candidate, capture: name, exact title, tenure, LinkedIn URL. Don't go deep on each — surface them and flag the most likely primary contact.

## Phase 3 — Tech stack inference (the consulting-relevant section)

Especially for infrastructure / IT / SaaS sales, the tech stack tells you whether they're a fit and what trigger language to use.

**Sources, in order of signal-to-noise:**

1. **DNS TXT records** — `dig acme.com TXT +short` reveals SaaS verification tokens (Microsoft, Google Workspace, Atlassian, Docusign, Apple, Adobe, Stripe, etc.). Each token is a customer-of-that-vendor signal.
2. **MX records** — email vendor (`outlook.com` = M365; `googlemail.com` = Workspace; `mailgun`/`sendgrid` = transactional). Email vendor is a strong proxy for general productivity stack.
3. **SPF record** — every authorized sender, including marketing/CRM tools (Marketo, HubSpot, Salesforce Marketing Cloud, Mailchimp, Klaviyo, etc.).
4. **Job postings.** What are they hiring engineers for? "VMware vSphere admin," "Azure cloud engineer," "Veeam backup specialist" — these are direct stack confessions.
5. **GitHub.** If they have a public org, the languages and frameworks tell the story.
6. **BuiltWith / Wappalyzer (free signals).** Surface CMS, CDN, analytics, JS libraries.
7. **LinkedIn employee skills.** Cross-tab the engineering org's listed skills.
8. **Press, case studies, talks.** Vendors love to publish customer wins. Search `"Acme Corp" "case study" site:[vendor].com`.

For an infrastructure-consulting use case, the high-value signals to extract:

- **Hypervisor**: VMware vSphere? Hyper-V? Nutanix? Bare metal?
- **Cloud**: Azure-heavy? AWS-heavy? Multi-cloud? On-prem-only?
- **Backup**: Veeam? Commvault? Rubrik? Native cloud tools?
- **Identity**: AD on-prem? Entra ID? Okta? Ping?
- **Email**: M365 (and which tier)? Workspace?
- **Endpoint**: Defender? CrowdStrike? SentinelOne?
- **Network**: SD-WAN vendor? Firewall vendor (Palo, Fortinet, Cisco)?
- **MSP / consulting partners**: any case-study or press mentions of who they work with.

Grade each finding by source count. A vendor case study + a related job posting + a SPF record naming the vendor's transactional sender = A. A single LinkedIn employee skill = C.

## Phase 4 — Trigger events (the lead-with section)

Recent events worth opening a conversation with. Look in the last 6–12 months:

- **Funding round** → expansion budget likely.
- **Acquisition / merger** → integration work, consolidation, often outsourced.
- **New executive in the buying center** → 90-day window of being open to new vendors. CIO transitions in particular.
- **Layoffs / restructuring** → contractor-friendly, but be tactful.
- **Public incident** (data breach, outage, ransomware) → immediate-need window for security or resilience pitches.
- **Press about a tech initiative** ("Acme migrates to Azure," "Acme adopts zero trust") → direct hook.
- **Office moves / new locations** → infrastructure refresh window.
- **Job postings for senior infra/security roles** → the work they're trying to staff is often work they could outsource.
- **Compliance deadline coverage** (SOC 2 attestation, HIPAA audit, PCI scope change) → consulting hook.

Capture each trigger with date and source. Two well-chosen triggers beat a list of ten.

## Phase 5 — Existing vendor relationships

Are they already buying from someone in your space? If so, identify:

- **Which vendor.** From case studies, press, LinkedIn.
- **How long.** Inferred from contract dates if disclosed.
- **Satisfaction signal.** Recent renewals, expansion press = happy. New job postings to replace the work the vendor does, or competitor evaluations on Reddit/G2 = unhappy.

A current-vendor read prevents the "we already have someone" wall and lets you frame either as a complement or as a replacement candidate.

## Phase 6 — The "why now" synthesis

The dossier is not a report dump. End with a synthesis section answering three questions:

1. **Is this a fit?** Yes / No / Maybe — with the 1–2 reasons.
2. **Who is the right first conversation?** One name (or two), with the reason.
3. **What's the opening?** The single best trigger to lead with. One sentence.

If you can't answer these three, the dossier is incomplete.

## Output

Produce `<target-slug>-dossier.md`. B2B-account dossier sections:

1. Account snapshot — name, parent, what they do, size, vertical
2. Buying center — likely decision-makers, primary contact recommendation
3. Tech stack — what we can infer, with grades
4. Trigger events — last 6–12 months, ranked by relevance
5. Existing vendor relationships
6. Why now — synthesis (fit, contact, opening)
7. Open questions
8. Sources

## Don'ts (B2B-specific)

- Don't research the prospect's personal life. Professional capacity only.
- Don't write a pitch in the dossier. The dossier informs the pitch; it isn't the pitch.
- Don't fabricate trigger events. "They probably need this because…" is not a trigger; a press release is.
- Don't skip the synthesis. A dossier without it is research; with it, it's account intel.
- Don't romanticize the most prominent person. The CEO is rarely the right first conversation.
