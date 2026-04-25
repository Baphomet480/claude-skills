# Workflow: Company

For general company research — what does this company do, are they real, who runs them, what's their situation. For B2B-prospect-specific work, see `b2b-account.md`. For investment-grade work, see `due-diligence.md`.

## Pre-flight

Run the Four Gates. The disambiguation step matters even for companies:

- "Acme Corp" might be three different entities (US Delaware Inc., UK Ltd., a defunct shell, a trade name belonging to a holding company).
- Confirm the registry record before reporting on the entity.

## Phase 1 — Entity identification

1. **Find the canonical website.** A search for the company name should land on the company's own site. If it doesn't, you may have the wrong target.
2. **Find the registry record.** US: Secretary of State of the state of incorporation; SEC EDGAR if public. UK: Companies House. Look up: legal entity name, formation date, status (active/dissolved), registered agent, registered address. Mexico: Registro Público de Comercio. Spain: Registro Mercantil.
3. **Identify any DBAs and brand names.** Many companies operate under multiple trade names.
4. **Confirm match.** The website's footer/legal page usually states the legal entity name and jurisdiction. That should match the registry. If it doesn't, write down the discrepancy.

## Phase 2 — What they do

- **Product / service summary.** Read the homepage and one or two product pages. Write 2–3 sentences in plain language. If you can't, the company's positioning is probably bad — note that and infer from clearer downstream signals.
- **Customers.** Look for case studies, customer logos, testimonials. These are often selectively chosen — useful as floor evidence, not as a representative sample.
- **Industry / vertical.** Self-described and externally classified (NAICS code if relevant).
- **Pricing model** (if public). SaaS subscription, project-based, enterprise license, etc.

## Phase 3 — Size, scale, posture

- **Headcount.** LinkedIn company page is the easiest read but gives a rough number; cross-check with a recent press mention.
- **Locations.** HQ + offices. Often on the contact page or footer.
- **Funding / financials** (if available). Crunchbase, press releases, regulatory filings.
- **Revenue indicators** (if publicly disclosed). Most private companies don't disclose; don't make this up.

## Phase 4 — Leadership

- C-level: CEO, CFO, CTO, COO, etc. — name and tenure.
- Board (if disclosed).
- Founders (especially if still active).

For each, capture: name, role, LinkedIn URL, and how long in the role. Don't deep-dive each one in this workflow — that's `person.md` territory.

## Phase 5 — Recent signals

The last 12 months of:

- Press releases on their own site.
- Third-party news coverage.
- Job postings (a goldmine for direction — what are they hiring? what tech stack? what pain points are they trying to solve?).
- Funding events, acquisitions, divestitures.
- Personnel changes — new executives, departures, layoffs.

## Phase 6 — Reputation and risk

Selective — depth depends on the use case:

- News searches with "lawsuit," "data breach," "controversy," "layoffs," "fraud" (each separately).
- BBB / Trustpilot / G2 / industry-specific review sites for service companies.
- Public regulatory action (FTC, SEC, state AGs).
- Glassdoor / Indeed for employee sentiment if it bears on the use case.

If the use case is investment or partnership, this section becomes much heavier — escalate to `due-diligence.md`.

## Phase 7 — Web / tech footprint (light pass)

For a fuller pass, see `domain.md`. The light version:

- Primary domain + obvious aliases.
- Email vendor (from MX or SPF).
- CMS / hosting (from public headers if visible without probing).
- Major SaaS the company runs (from DNS verification TXT records).

## Output

Produce `<target-slug>-dossier.md`. Standard company sections:

1. Entity card — legal name, jurisdiction, formation date, status, address
2. What they do — 2–3 sentences
3. Size and scale — headcount, locations, funding posture
4. Leadership
5. Customers / market position (with caveats about selection bias)
6. Recent signals — last 12 months
7. Reputation and risk — what surfaced and what didn't
8. Light tech footprint
9. Open questions
10. Sources

## Don'ts (company-specific)

- Don't conflate the parent and a subsidiary. Note the relationship explicitly.
- Don't mistake a DBA for a separate company.
- Don't take Crunchbase as gospel — it's frequently outdated, especially on private-company headcount and funding.
- Don't infer "they must use X" from a single weak signal. Tech-stack inference belongs in `domain.md` with appropriate confidence grades.
