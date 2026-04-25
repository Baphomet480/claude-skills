# Workflow: Person

For investigating a named individual — typically a professional, executive, public-facing employee, or B2B counterparty. Personal-life material is out of scope unless explicitly relevant.

## Pre-flight

Run the Four Gates from `SKILL.md` first. In particular:

- **Scope it.** Is this a professional workup or something else? If something else, see `references/ethics-and-scope.md` and decline if appropriate.
- **Disambiguate.** This is the most important step in a person investigation. See `references/disambiguation.md`.

## Phase 1 — Identity confirmation

Goal: confirm exactly which person you're researching.

1. **Initial broad pass.** One web search for the full name. Look at the top 10 results. Note candidates.
2. **Narrowing pass.** Add the discriminator the user gave you (employer, location, domain, LinkedIn URL).
3. **Primary source confirmation.** Land on the LinkedIn profile or company bio that proves the match. Save the URL.
4. **Stop and check.** If you have not unambiguously identified the right person, ask the user for a discriminator. Do not continue.

Output of Phase 1: a single sentence — *"Target: [name], [role] at [company], [city]. LinkedIn: [URL]. Distinct from: [N other matches you saw]."*

## Phase 2 — Professional footprint

For the confirmed target, build out the professional picture:

- **Current role.** Title, employer, tenure, location. Source: LinkedIn or corporate bio.
- **Career arc.** Previous 2–3 roles. Source: LinkedIn or bios on previous employers' sites (Wayback if needed).
- **Education.** Where stated publicly. Skip if not material.
- **Certifications / public credentials.** Where they affect the use case (e.g., a security cert for a security target).
- **Public writing / talks.** Conference talks, podcast appearances, articles, GitHub. Strong signal of expertise areas.
- **Industry recognition.** Awards, board seats, publications.

## Phase 3 — Network and adjacency (if relevant)

Only if the use case requires it (B2B selling, investment due diligence, journalism):

- **Co-founders / co-authors / co-presenters** — people consistently appearing alongside the target.
- **Boards / advisor roles** — public registry filings, company About pages.
- **Notable past colleagues** — the "team that built X together" pattern.

Skip this phase for simple "who is this person" lookups.

## Phase 4 — Recent activity

What is the target doing or saying *now*?

- LinkedIn posts in the last 90 days.
- Recent talks, podcast appearances, articles.
- Recent press mentions in the company's industry.
- Public X/Twitter activity if professionally relevant.

This is often the most useful section for B2B work — it reveals priorities, recent moves, and conversational hooks.

## Phase 5 — Cross-platform identity (selective)

If the use case requires it: confirm the target's public handles on other platforms.

- GitHub, if technical.
- X/Twitter, if professionally active.
- Personal blog or Substack, if writing.

Confirm via cross-linking from the target's own bio. Don't rely on third-party "username search" services — they collide.

## Phase 6 — Negative checks

Before closing, look for:

- **Recent press scandals or controversies.** Search the name with "lawsuit," "fired," "resigned," "fraud," "controversy" — separately, not stacked.
- **Sanctions / public registries** (only if the use case warrants — investment DD, regulatory work). OFAC, World-Check (if available), etc.
- **Bankruptcy / litigation** (only if material; jurisdictional rules apply).

These should be present-or-absent findings, not fishing expeditions. If nothing comes up, that's a finding — write it down with appropriate confidence.

## Output

Produce `<target-slug>-dossier.md` per `templates/dossier.md`, plus `<target-slug>-findings.json` per `templates/findings.schema.json`.

Standard person dossier sections:
1. Target match (Phase 1 output)
2. Professional summary — 2–3 sentences
3. Current role and tenure
4. Career arc
5. Public expertise / writing / talks
6. Recent activity (last 90 days)
7. Notable network connections (if relevant)
8. Negative checks
9. Open questions / what we couldn't confirm
10. Sources

## Don'ts (person-specific)

- Don't speculate on personal life (relationships, family, health) unless explicitly in scope.
- Don't combine separate people's data into one profile, even when "very likely the same person."
- Don't rely on people-finder aggregators as primary sources.
- Don't include the target's home address or personal phone, ever, in any workup.
- Don't rank or rate the person unless the user asks for that and it's appropriate.
