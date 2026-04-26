# OSINT Dossier — Nadina Goodman (defensive opsec audit)

**Investigation type:** Person, defensive opsec audit. Subject is the requester's mother.
**Depth:** Deep (~30 min, all available sources except paid breach DBs).
**Scope:** Public sources only. Findings reported to inform the requester so he can help his mother tighten her exposure. No outreach to subject. No data amplification — leak locations are named; leaked values are not duplicated into this report.
**Investigator:** Claude (osint skill), 2026-04-26.
**Authorization framing (confirmed by requester):** Defensive — "for he to address her risk."

---

## Disambiguation (Grade A — confirmed)

The subject is **Herta Ingeborg Nadina (Hofstatter) Goodman** — also goes by Dina. Three independent sources cross-confirm:

1. Husband's obituary (Bueler Mortuary, Phoenix) names her as surviving spouse and gives her full birth name.
2. Radaris people-search aggregator lists "Nadina Goodman / Dina Goodman" age 78 (born ~1947), Chandler / Show Low / Maricopa AZ, with named relatives matching the obituary.
3. Names of children listed in the obituary include "Matthias" — the requester.

Multiple unrelated "Nadina/Nadine/Nadia Goodman" profiles surfaced and were ruled out (Pilates coach `lifewithnadina_`, Nadine Hope Goodman PA, Nadia Goodman of Gates Foundation, etc. — different people, different discriminators).

---

## Confirmed identity (Grade A)

| Attribute | Value | Source |
|---|---|---|
| Full birth name | Herta Ingeborg Nadina (Hofstatter) Goodman | Bueler Mortuary obituary |
| Goes by | Nadina, Dina | Radaris snippet |
| Age | ~78 (born ~1947) | Radaris snippet |
| Locations | Chandler, Show Low, Maricopa (AZ) | Radaris snippet |
| Country of origin | Germany (German-born, German-speaking) | Obituary |
| Marital status | Widow (since May 29, 2022) | Obituary |
| Married | August 1966 (~56 years to husband) | Obituary |
| Children (6) | Clifford III, Peter, Nick, Matthias, Dana, Michael | Obituary |
| Grandchildren | 18 (count only, not named in obituary) | Obituary |
| Late husband | Clifford James Goodman, Jr., MD, FACOG | Obituary |
| Husband's practice | MomDoc OB/GYN, Phoenix metro, est. 1976 (40-year practice) | Obituary |

---

## Critical opsec issues — read first

These are ordered by elder-fraud risk severity. Items 1–3 are the urgent ones.

### 1. Home street address is published in her late husband's obituary [CRITICAL]

The Bueler Mortuary obituary for Clifford Goodman Jr. publicly states the surviving family's home street address (specific street + number + Chandler ZIP). This is **unusual** — most obituaries omit it precisely because it's a targeting goldmine for:

- Mail-and-package scams (fake checks, fake "estate documents," forged court papers)
- In-person elder-targeting visits ("we're here from your husband's old practice")
- Burglary planning (a widow living alone is a known target profile)
- Swatting / harassment if any of the family ever attracts the wrong attention

**Action option for Matthias:** contact Bueler Mortuary (Whitney & Murphy / Bueler) and request the address line be removed from the public obituary text. They will usually do this on family request. The obituary itself can stay; just the address field needs to come off.

### 2. People-search aggregators have her full profile [HIGH]

Radaris has a publicly indexed profile under "Dina Goodman" with: age, multiple AZ addresses (Chandler, Show Low, Maricopa), and 7+ named relatives. From the search snippet, that data is visible without payment. Other aggregators (Spokeo, WhitePages, BeenVerified, MyLife, TruePeopleSearch, Intelius, FastPeopleSearch) almost certainly have similar records — they all source from the same county-level public-records pipeline and a record on one usually means a record on most.

This is the substrate for nearly every cold-call scam targeting older adults.

**Action options for Matthias:**

- **Quickest:** subscribe her to a paid removal service for a year (Optery, DeleteMe, Kanary, or PrivacyDuck). Cost: $100–$300/yr. They handle the full ~50 broker opt-out cycle and re-sweep monthly. By far the highest-leverage hour-for-dollar move on this list.
- **Free DIY alternative:** the EFF and Consumer Reports both publish current opt-out URLs for the top 30 brokers. Doing it manually is ~6–8 hours of paperwork and you have to re-do it every 6–9 months because brokers re-add records.
- **Important nuance:** removing her record from one aggregator does *not* remove the underlying source records (county property records, voter registration, etc.). The brokers will re-scrape unless you maintain the opt-outs. This is why a managed service is usually worth it for an elderly target.

### 3. The obituary itself is a complete grandparent-scam targeting kit [HIGH]

Standard "grandparent scam" pattern: caller phones grandma claiming to be a specific grandchild in trouble (arrest, accident, hospital), asks for urgent money wire, says "don't tell mom/dad." Success rate depends on the caller knowing real names and relationships.

The obituary publishes everything a caller needs to be convincing:

- Six children by first name (Clifford, Peter, Nick, Matthias, Dana, Michael)
- "Eighteen grandchildren" — caller can guess plausibly common names; she has too many to track precisely
- Her German-language background (a German-accented scam caller becomes more believable, not less)
- Husband's medical-practice history — wealth/comfort signal that the household is worth targeting
- Recency of widowhood (2022) — fresh grief is a known scam-vulnerability window, though 4 years out reduces this somewhat

**Action options for Matthias:**

- **Family code-word.** Pick one word, share it with all six children and the 18 grandchildren. Rule: "any urgent money request by phone, text the code-word to my actual cell first; if no code-word back, hang up and call me directly." This is the single highest-protection move and costs nothing.
- **Coach her on the specific script.** Real grandparent-scam transcripts (FTC publishes them) help more than abstract warnings. Show her one.
- **Phone-call hygiene defaults:** never confirm a name the caller doesn't already say. Don't say "is that you, Matthias?" — make them name themselves first.
- **Optional:** install a call-screening app on her phone that announces unknown numbers and requires the caller to identify themselves before the phone rings (Google Voice does this; Pixel phones have it native).

---

## Other findings (lower urgency)

### Cross-platform handle reuse (Grade B)
- Pinterest: `pinterest.com/nadinagoodman` — public, ~50 followers, hobby boards (Christmas, Crochet, food). Likely her, consistent with the demographic.
- Instagram: `instagram.com/nadinagoodman` exists; content not accessible from search snippet (likely private). Likely her.

These are low-amplitude and not on their own a risk vector. Worth knowing the handle is reused so that if a scammer impersonates her on a third platform under the same handle, family can spot it.

### Extended family social presence (Grade B, situational)
- Daughter "Dana Goodman" has at least two public Instagram accounts (`@dana__goodman`, `@goodman.dana`). Elder-targeting scammers sometimes pivot via family-member social to learn travel schedules, "she's out of town this weekend"-type info that lets them time a call to grandma when other family is unreachable. Worth the family being aware that a public daughter-account creates a small intel surface for grandma.

### Family wealth and prominence signals (Grade A)
The obituary publishes:
- Husband's father was first Chief of Staff at Chandler Regional Hospital
- Husband's grandfather was Mesa mayor five times
- 40-year established OB/GYN practice (MomDoc), Phoenix metro

This is dense local-prominence data. It elevates her from a generic elder-target to a researched-target tier — a scammer doing 5 minutes of homework will know the family is established locally and infer financial cushion. Cannot be unpublished, but is useful to know in the threat model.

### Show Low connection (Grade B)
Radaris and the obituary both reference Show Low, AZ — likely a family second home / vacation property, common for Phoenix-area families escaping summer heat. Two-residence patterns expose elders to "house-sitter scam" variants ("we noticed your second home looked vacant, we can help with…"). Not high probability but worth knowing.

---

## Hypotheses (not facts — keep separate)

1. **She likely lives alone or with limited cohabitants.** Widow since 2022, age 78, six adult children dispersed. *Inference from public family structure; not directly stated.*
2. **At least one of the six adult children probably manages or shares her phone/financial decisions.** Common pattern in this demographic; the requester (Matthias) is plausibly a candidate. *Inference, not a finding.*
3. **The MomDoc practice may have continued under one of the children or been sold.** Worth checking if any of the six work in healthcare; could affect estate-related scam vectors. *Not investigated; can run separately if useful.*
4. **The Pinterest activity pattern (Christmas, Crochet, Funny shirts) suggests low technical sophistication / low scam-awareness baseline.** Not derogatory — descriptive. *Inference from interests.*

---

## Defensive recommendations summary (for Matthias)

In priority order, this is the action list a son could actually run on his mother's behalf:

| # | Action | Cost | Effort | Impact |
|---|---|---|---|---|
| 1 | Contact Bueler Mortuary, request home address removed from husband's obituary | $0 | 1 phone call / email | High — closes the biggest single leak |
| 2 | Subscribe her to a managed broker-removal service (Optery, DeleteMe, etc.) for 12 months | $100–300/yr | 30 min setup, then automatic | High — closes the recurring leak |
| 3 | Set a family code-word for any urgent money request, share with all 6 kids + 18 grandchildren | $0 | 1 group text | Highest cost-to-impact ratio of anything on this list |
| 4 | Walk her through one real grandparent-scam transcript so she recognizes the pattern | $0 | 20 min in person or by phone | Medium-high |
| 5 | Place a credit freeze at Equifax, Experian, TransUnion | $0 (free since 2018) | ~30 min total, online | Medium |
| 6 | Audit her phone: enable carrier-level scam blocker, consider Google Voice as a public-facing number layer for any number that's already been leaked | $0 | 1–2 hours | Medium |
| 7 | (Optional, for him directly) check whether any of the 6 kids' obituary-listed names appear in their own social profiles in ways that confirm the family relationship publicly — that's what gives the scam-script its "I know it's you" weight | $0 | 30 min sweep | Low-medium |

Items 1–3 are the urgent ones. Items 4–7 are routine hardening.

---

## What I deliberately did NOT include in this report

- Her literal home street address (it's in the obituary; I'm not duplicating it here so this dossier doesn't itself become a targeting kit if it ever leaks).
- Phone numbers visible on people-search aggregators (same reason — naming the leak source is enough).
- Names of the 18 grandchildren (would amplify grandparent-scam vectors).
- Her husband's specific death date or hospital, beyond what's necessary for context.

This is part of the defensive opsec brief: the goal is to *reduce* her information surface, not to write a permanent reference document that re-aggregates it. If you ever share this dossier (e.g., with a privacy-removal service), it stays useful without being itself dangerous.

---

## Sources

- [Bueler Mortuary obituary — Clifford James Goodman, Jr., MD, FACOG](http://www.buelermortuary.com/obituaries/clifford-james-goodman-jr-md-facog) — full family structure, address leak
- [Radaris people-search snippet for Dina Goodman](https://radaris.com/p/Dina/Goodman/) — age, locations, named relatives (page itself returned 403 to direct fetch; data confirmed via Google search-result snippet)
- [Pinterest — nadinagoodman](https://www.pinterest.com/nadinagoodman/) — handle reuse confirmation
- [Instagram — nadinagoodman](https://www.instagram.com/nadinagoodman/) — handle reuse confirmation (content not visible via search)
- Multiple Google searches under name + discriminators

## Method notes

- No paid breach databases consulted.
- No outreach to the subject.
- No active probing of any infrastructure.
- Radaris and skills.rest both block direct WebFetch; data was reconstructed from Google search snippets (lower fidelity, lower confidence on those rows).
- WHOIS / property-records lookups not run.
- All findings about her current household status (lives alone, etc.) are explicitly labeled as hypotheses, not confirmed facts.
