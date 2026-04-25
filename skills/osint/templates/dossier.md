# {{TARGET_DISPLAY_NAME}} — OSINT Dossier

| Field | Value |
|---|---|
| Target slug | `{{TARGET_SLUG}}` |
| Target type | {{TYPE}} <!-- person / company / b2b-account / domain / dd-subject --> |
| Depth | {{DEPTH}} <!-- Quick / Standard / Deep --> |
| Investigator | {{INVESTIGATOR}} |
| Started | {{STARTED_AT}} |
| Completed | {{COMPLETED_AT}} |
| Scope statement | {{SCOPE_STATEMENT}} |

---

## Target match (disambiguation)

**Tracking:** {{CANONICAL_IDENTIFIER}} — {{PRIMARY_URL}}

**Discriminator(s) used:** {{DISCRIMINATOR_LIST}}

**Explicitly NOT tracking:**
- {{NAMESAKE_1}} — {{WHY_NOT}}
- {{NAMESAKE_2}} — {{WHY_NOT}}

If the user requested a different person/entity than the one we tracked, stop here and re-scope.

---

## Executive summary

{{2–4 sentences. Plain language. The 30-second answer to "what did you find?"}}

---

## Findings

Group by topic. Every claim ends with a confidence grade in brackets: **[A]**, **[B]**, **[C]**, **[D]**. See `references/confidence-grading.md`.

### {{TOPIC_1}}

- {{Claim}} **[A]** ([1], [2], [3])
- {{Claim}} **[B]** ([4], [5])
- {{Claim with caveat}} **[C]** ([6]) — single source; would upgrade if confirmed by {{what would resolve it}}.

### {{TOPIC_2}}

- {{Claim}} **[A]** ([7], [8], [9])
- {{Claim}} **[D]** — inferred from {{signal}}, not directly confirmed.

<!-- Add as many topic blocks as the workflow requires. Person, company, b2b-account, domain, due-diligence each have their own Output sections — follow them. -->

---

## What we couldn't confirm

Things we looked for and didn't find, or found ambiguously. Negative findings are findings.

- **{{Open question}}** — searched {{where}}; no result. Could be resolved by {{primary source if accessible}}.
- **{{Open question}}** — conflicting signals: {{source A says X, source B says Y}}.

---

## Synthesis

{{1–3 paragraphs. What does this picture mean for the user's stated purpose? Connect findings to the scope statement. This is the only section where you reason out loud — keep it tied to the evidence.}}

---

## Method notes

- **Tools used:** {{web_search, web_fetch, dig, whois, crt.sh, …}}
- **Searches run:** {{count, or list distinctive ones}}
- **Sources reviewed but not cited:** {{count}} — discarded for {{reason: low quality, duplicate, wrong target, paywalled, etc.}}
- **Time budget:** {{actual elapsed}} vs. {{Quick / Standard / Deep budget}}
- **Notable gaps in tooling:** {{e.g., "no Hunter API key — email patterns inferred from MX only"}}

---

## Sources

Numbered. Each citation in the findings section refers to one of these.

### Primary (target's own properties, registries, filings)

1. {{URL}} — {{publisher / type}} — accessed {{date}}
2. {{URL}} — {{publisher / type}} — accessed {{date}}

### Press and third-party reporting

3. {{URL}} — {{publisher}} — {{published}} — accessed {{date}}
4. {{URL}} — {{publisher}} — {{published}} — accessed {{date}}

### Registry / regulatory

5. {{URL}} — {{registry name}} — accessed {{date}}

### Other

6. {{URL}} — {{publisher / type}} — accessed {{date}}

---

## Disclaimer

This report is an open-source intelligence summary based on public information available at the time of writing. It is not a regulated background check (FCRA), legal opinion, financial audit, or credit assessment. Public information can be incomplete, outdated, or wrong; named individuals may share names with others; corporate records vary in quality across jurisdictions. Decisions with legal or financial consequences should be made with appropriate professional counsel and, where required, regulated investigative services.
