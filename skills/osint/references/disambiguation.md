# Disambiguation Protocol

The single most common OSINT error is reporting on the wrong person or wrong company. This protocol exists to make that error rare.

## The principle

Names are not identifiers. "John Smith" is not a target. "John Smith, VP Engineering at Acme Corp, based in Austin TX, LinkedIn URL `linkedin.com/in/johnsmithatx`" is a target. Until you have a discriminator that uniquely picks out the right entity, you do not have a target — you have a name.

## The protocol

### Step 1 — Enumerate candidates

For the given name/handle, list every plausible candidate you find in the first 2–3 searches. **Do not pick the first match.**

For people, common signals that produce candidates:
- Common name + common employer (e.g., "John Smith Acme")
- Common name + common location
- Username appearing on multiple unrelated platforms

For companies:
- Same/similar trade name in different jurisdictions
- Subsidiary vs. parent vs. doing-business-as
- Defunct entity vs. current operating company

### Step 2 — Pick a discriminator

A discriminator is one fact that uniquely picks out the right candidate from all the others. It should be:

- **Specific** — narrow enough to exclude the others
- **Verifiable** — confirmable from a primary source
- **Stable** — not a fact that changes weekly

Strong discriminators (in roughly this order):
1. Exact LinkedIn URL or company website employee page
2. Email domain or work email pattern
3. Employer + role + city
4. Domain ownership / WHOIS contact
5. Author byline on a specific publication
6. Photo cross-confirmed across two profiles

Weak / unsafe discriminators:
- Same name + same general industry (too broad)
- Same name + same city (especially in large cities)
- Self-reported social media posts alone
- Auto-generated "people you may know" / "people search" aggregator pages — these are notoriously wrong

### Step 3 — Confirm from a primary source

A primary source is one controlled by the entity itself or by an authoritative registry:

- The target's LinkedIn profile, company bio, About page
- A press release on the company's own domain
- Government registries (Secretary of State, SEC EDGAR, Companies House, etc.)
- Domain WHOIS / cert transparency
- Conference speaker pages, peer-reviewed publications

People-finder sites (Spokeo, BeenVerified, ZoomInfo aggregator pages, RocketReach, etc.) are **not** primary sources. They are downstream and often wrong. Use them as leads to investigate, never as confirmation.

### Step 4 — Declare the match

In the dossier, before any findings, state:

> **Target match:** [name], [discriminator]. Confirmed via [primary source URL]. Distinct from at least [N] other [name]s found in search (e.g., a hardware engineer at IBM in Boston, an attorney in Phoenix).

This sentence is the disambiguation receipt. It tells the reader you did the work and lets them spot-check.

## When you can't disambiguate

If the discriminator cannot be confirmed:

- For a person: report only what is true of *the name as searched* and explicitly note that the identity is not confirmed.
- For a company: same — note ambiguity, do not pick a winner.
- Do not proceed to a deep investigation on a wrong target. Ask the user for additional context (a city, an employer, a domain, a LinkedIn URL).

A failed disambiguation is not a failed investigation. It is a correctly-handled investigation that surfaced an answerable question.

## Common traps

- **The famous-namesake trap.** A search for "Sarah Chen marketing" will surface the most prominent Sarah Chen even if your target is a regional marketing manager. Add narrowing constraints early.
- **The merged-profile trap.** People-search aggregators routinely merge two people with the same name into one profile. If the page shows wildly inconsistent ages, employers, or locations, the merge is bad.
- **The handle-collision trap.** Usernames are reused. `@msmith` on Twitter is not necessarily `msmith` on GitHub. Confirm cross-platform identity from the user's own linking (their own bio links one to the other), not from third-party "username search" tools.
- **The dead-relative trap.** Obituaries and old genealogy records often surface a long-dead person with the same name. Watch the dates.
- **The shell-company trap.** Two companies with the same trade name can be unrelated, or one can be a defunct shell. Always check the registry record (Secretary of State / Companies House) for status, formation date, and registered agent.
