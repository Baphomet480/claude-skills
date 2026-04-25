# Confidence Grading

Every finding in a dossier carries a letter grade. Grading is not optional and not cosmetic — a downstream reader's trust in the whole dossier comes from grading discipline.

## The grades

### A — Three or more independent sources, including at least one primary or authoritative

- The fact is on the target's own website **and** in a third-party news article from a reputable outlet **and** in a public registry (or equivalent).
- Or: published in two independent reputable outlets plus a primary source.
- Use sparingly. Most "facts" don't actually clear this bar.

### B — Two independent sources

- Often the realistic best you can get for B2B/account work.
- Two reputable third-party sources, or one primary plus one third-party.
- Acceptable for most actionable findings.

### C — One source, or multiple non-independent sources

- A single LinkedIn bio. A single press release. Three news sites all citing the same press release.
- Useful, but mark it as such. The reader should know they're standing on one leg.

### D — Inferred, likely-but-unconfirmed, or single self-published source

- "They probably use [tool] because [reasoning]."
- A self-reported claim that can't be cross-checked.
- An aggregator-only finding with no upstream primary source.
- Either drop it or label it explicitly: *"Inference (D): ..."*. Never present as fact.

## What counts as a primary source

| Type | Examples | Authority |
|---|---|---|
| Entity-owned | Company website, About page, official LinkedIn page, official press releases | Authoritative for *what they claim*, not for the underlying fact |
| Government / regulatory | SEC EDGAR, Secretary of State filings, Companies House, USPTO, FCC, court records | Authoritative |
| Standards / registry | DNS records, WHOIS (with caveats), certificate transparency logs, IANA, ARIN | Authoritative for technical facts |
| First-hand journalism | Investigative reporting from a recognized outlet, with named author | Strong |
| Peer-reviewed / scholarly | Academic papers, conference proceedings | Strong for the claim made |

## What does NOT count as independent confirmation

- Two articles on the same parent's outlets (e.g., two Hearst properties).
- Two articles published within an hour of a press release that quote the press release.
- A LinkedIn post + a Twitter post by the same person.
- Two people-finder aggregator pages — they all pull from the same underlying brokers.
- An AI-generated summary that cites a source you haven't read.

## Edge cases

### Self-published claims

A target's LinkedIn bio claiming "led $50M Series B" is **C-grade** for the underlying fact (we have only their word), but **A-grade** for "this person publicly claims to have led the Series B." If the user cares about the difference, write both.

### Negative findings

"No evidence of X" is itself a finding and gets a grade based on how thoroughly you looked:
- **B** — searched all reasonable sources and found nothing.
- **C** — did a quick check, didn't find it, didn't exhaust the obvious places.
- Don't grade a negative **A** — absence of evidence is hard to prove definitively.

### Old facts

A 2018 article confirming a 2018 fact is fine. A 2018 article being used to confirm someone's *current* employer is C-grade at best. Time-stamp every claim where currency matters.

### Translated / non-English sources

Don't downgrade automatically — a primary source in Spanish is still a primary source. But if you can't read it confidently, say so and prefer the translation as a lead, not a confirmation.

## Mechanics in the dossier

In prose:

> Founded in 2007 by Jane Doe and John Smith **(A)** in Phoenix, AZ.

In a finding list:

```
- Founded 2007 by Doe & Smith in Phoenix
  Confidence: A
  Sources: [1] AZ Corp Commission filing | [2] 2008 Phoenix Business Journal | [3] company About page
```

In `findings.json`:

```json
{
  "claim": "Founded in 2007 by Jane Doe and John Smith in Phoenix, AZ",
  "confidence": "A",
  "category": "company.history",
  "sources": [
    {"url": "https://...", "type": "registry"},
    {"url": "https://...", "type": "press"},
    {"url": "https://...", "type": "primary"}
  ],
  "extracted_at": "2026-04-25T18:30:00Z"
}
```

## Sanity check before publishing

Before handing the dossier over, scan the grades:

- If the dossier is mostly A's, you're probably overgrading. Most B2B account work yields a mix of B and C.
- If the dossier is mostly D's, the investigation isn't done — go back or scope down.
- If the most important finding is a D, surface that to the user as a question, not an answer.
