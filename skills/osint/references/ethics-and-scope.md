# Ethics & Scope

This skill exists to do legitimate, public-source intelligence work. The rules here are not lawyerly throat-clearing — they're operational. Following them keeps the user, the target, and you out of trouble.

## Always allowed

- Researching public-facing professionals (executives, public-facing employees) in their professional capacity
- Researching companies, including private companies, from public records and public sources
- Researching public domains, public IPs, and public infrastructure (passively — DNS, WHOIS, cert transparency)
- Reading what the target has chosen to publish (their website, their public social media, their press releases, their conference talks, their open-source contributions)
- Cross-referencing public records (court filings in jurisdictions where they are public, government registries, regulatory filings)
- Using the Wayback Machine and other public archives
- Reading public news coverage

## Allowed with care

- **Researching private individuals** is allowed only when there's a clear lawful basis — they're a public figure, a fraud suspect named publicly, a journalist's named source, a person who has consented, or a B2B counterparty in their professional capacity. Otherwise, don't.
- **Photo / image searches** — fine for confirming a public-facing professional's identity. Not fine for assembling a stalking aid.
- **Family / relationship mentions** — only when materially relevant to the investigation (e.g., a publicly disclosed business co-founder who is a spouse). Never as background color.
- **Home addresses** — basically never. If a target's home address is needed (e.g., for a legitimate process server), that's a job for a licensed PI, not this skill.
- **Phone numbers** — work numbers, fine. Personal mobile numbers, no.

## Never allowed

- **Paid breach databases** (Have I Been Pwned single-domain checks for legitimate security work are different from buying breach dumps to enrich a profile). No combolists. No "people lookup" services that traffic in scraped data of dubious provenance.
- **Accessing accounts you don't own.** Even with a leaked password.
- **Social engineering.** No pretexting, no fake personas to extract information, no asking the target's coworkers to confirm details under false pretenses.
- **Active scanning of infrastructure you don't own.** No port scans, no vuln scans, no fuzzing — even if "no one will notice." Passive recon (DNS, cert transparency, public Shodan results) is fine.
- **Bypassing platform ToS.** No scraping LinkedIn at scale in ways that violate their terms; no using credential-stuffing tools; no auth bypass.
- **Bypassing paywalls** for paid content the user doesn't have a license to.
- **Doxing.** Compiling a target's personal contact info for the purpose of harassment, regardless of whether the individual data points are technically public.
- **Stalkerware tactics.** Tracking someone's real-time location, monitoring private accounts, recording private communications.

## Use-case smell tests

Decline the request if any of these are true:

- The target is described in terms suggesting personal grievance ("my ex," "this woman who…", "the guy who screwed me on…") and the requested output is contact info or location.
- The user wants to "find" someone who is implied to be hiding (estranged, in witness protection, evading service).
- The user wants the target's home address, daily schedule, or movements.
- The investigation is into a minor.
- The user explicitly asks you to bypass a ToS, a paywall, or a privacy setting.
- The user asks for "everything you can find" with no stated purpose. Always ask for the purpose first — not to interrogate, but to scope correctly.

When you decline, be brief and clear about which line was crossed. Don't lecture. Offer the legitimate version if there is one — e.g., "I can't help locate a private individual, but if this is about a B2B counterparty, I can do a professional-capacity workup of their company."

## Jurisdictional notes (briefly)

You are not a lawyer. The user's jurisdiction matters. Some defaults that are roughly safe across major Western jurisdictions:

- **GDPR-ish jurisdictions (EU, UK):** Personal data of identifiable individuals deserves more care. Lawful basis matters even for public data.
- **US:** State laws vary on things like Fair Credit Reporting Act applicability if the output is used for employment, credit, or tenant decisions. If the user signals that's the use case, point them to a licensed CRA — this skill is not one.
- **Anywhere:** Anti-stalking and anti-harassment laws exist. Defamation laws exist. Don't assemble material that obviously feeds either.

If a user's request hinges on a jurisdiction-specific question, name the question rather than guessing.

## What to write when scope is unclear

A short pre-investigation note in the dossier:

> **Scope:** Public sources only. Researching [target] in professional capacity for [purpose]. Personal-life material out of scope unless directly relevant to the stated purpose. No active scanning, no breach data, no private records.

That sentence anchors the investigation and gives the user a clean handle to adjust if needed.
