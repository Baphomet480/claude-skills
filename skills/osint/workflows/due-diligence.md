# Workflow: Due Diligence

For investment-grade or partnership-grade research on a company. Heavier than `company.md`. Slower. More skeptical. The deliverable is a defensible risk picture, not a marketing summary.

This workflow is **not a substitute** for legal due diligence, financial audit, or a regulated background check. It's the open-source layer that informs and stress-tests those processes.

## Pre-flight

Run the Four Gates with extra weight on Gate 1:

- **Authorized?** Diligence on a company you're investing in, partnering with, acquiring, or vetting as a vendor is normal. Diligence as a competitor pretext or a personal vendetta is not.
- **Scope statement.** Write the purpose explicitly: investment, M&A, vendor onboarding, partnership, lending. The scope shapes what risks matter.
- **Adverse-media legal posture.** In some jurisdictions (notably under FCRA in the US) certain employment/credit decisions require regulated background checks, not OSINT. Don't let an OSINT report be repurposed as one — say so in the deliverable.

## Phase 1 — Entity and structure

Start from `company.md` Phase 1, then go deeper:

- **Full corporate genealogy.** Parent → target → subsidiaries → JVs. Map it.
- **Jurisdictions of incorporation** for each entity. Note any tax-haven structuring (Cayman, BVI, Delaware-only with no operations there) without editorializing — flag, don't conclude.
- **Beneficial ownership** to the extent disclosed. UBO registries vary: UK PSC register is public, US Corporate Transparency Act filings are not, opencorporates aggregates what's available.
- **Recent structural changes** — formations, dissolutions, mergers, name changes, jurisdiction shifts in the last 5 years.

## Phase 2 — Financial picture

- **If public:** SEC filings (10-K, 10-Q, 8-K, proxy), earnings calls, investor presentations. Read the *Risk Factors* and *Legal Proceedings* sections, not just the press release.
- **If private:** what's been disclosed publicly — funding rounds (Crunchbase, PitchBook snippets, press releases), reported revenue ranges in news coverage, customer counts in marketing material.
- **Auditor.** If named, note who. Big Four vs. regional vs. unnamed has signal.
- **Material litigation involving money.** Court records (PACER for US federal, state court systems vary).
- **Bankruptcy / insolvency history** of the entity and its principals.

Don't fabricate financials. If revenue isn't disclosed, write "not publicly disclosed" — don't infer from headcount.

## Phase 3 — Leadership and governance

For each named C-level and board member:

- Tenure here.
- Prior roles — stable career or pattern of short stints?
- Board overlaps — do they sit on the boards of competitors, customers, or related entities?
- Any disqualifications, regulatory bars, or sanctions against the individual.
- Any prior bankruptcies, fraud findings, or SEC actions naming them personally.

This is `person.md`-style work narrowed to governance-relevant signals. It's not a personal-life dossier.

## Phase 4 — Litigation and regulatory

- **Civil litigation.** Plaintiff/defendant patterns. A company that is routinely sued by employees vs. one routinely suing customers tells different stories.
- **Regulatory actions.** SEC, FTC, FDA, EPA, state AGs, OSHA, foreign equivalents — whatever applies to the industry.
- **Consent decrees, settlements, fines.**
- **Whistleblower complaints** that became public.
- **Industry-specific:** for healthcare — HHS OIG exclusions, CMS sanctions; for finance — FINRA actions, OCC enforcement; for federal contractors — SAM.gov debarment, GAO bid protests.

## Phase 5 — Sanctions and adverse media

Run the entity and key principals against:

- **OFAC SDN list** (US Treasury).
- **UN Security Council Consolidated List.**
- **EU consolidated financial sanctions list.**
- **UK OFSI sanctions list.**
- Country-of-operation watchlists where relevant.

Then adverse-media sweep: bribery, fraud, money laundering, sanctions evasion, environmental, labor, human-rights. Use multiple search engines — one engine's blind spot is another's headline.

A clean sanctions check is itself a finding. Record it.

## Phase 6 — Operations and footprint

- **Physical footprint.** Real estate, manufacturing sites, data centers, retail.
- **Headcount and locations** with reasonable confidence.
- **Customer concentration** if disclosed.
- **Supplier and vendor exposure** — single-source dependencies that surface in 10-Ks or press.
- **Geographic risk** — operations in sanctioned countries, conflict zones, or high-corruption jurisdictions.

## Phase 7 — Reputational and market

- **Customer sentiment** — Trustpilot, BBB, G2, industry forums. Patterns matter more than individual reviews.
- **Employee sentiment** — Glassdoor, Indeed, Blind. Look for *patterns* (mass-firing language, ethics complaints), not individual gripes.
- **Press coverage** — last 24 months. Tone trajectory: improving, deteriorating, controversy-cluster.
- **Social-media reputation** of the brand — boycott campaigns, viral incidents.

## Phase 8 — Risk-area-specific deep dives

Pick the ones that match the use case:

- **Cybersecurity.** Public breaches (HIBP, public disclosure databases, news), exposed assets (Shodan/Censys read-only), DMARC/SPF posture, public vuln-disclosure history.
- **Privacy.** GDPR enforcement actions, state-AG privacy actions, public DPIA mentions.
- **ESG.** Sustainability reports, third-party ESG ratings, environmental violations (EPA ECHO).
- **Supply chain.** Forced-labor disclosures (UFLPA, EU CSDDD), customs records (when public), anti-trafficking statements.
- **Tax.** Public tax-controversy filings, transfer-pricing disputes if disclosed.
- **IP.** Patent portfolio, trademark disputes, recent litigation on IP.

## Phase 9 — Synthesis: rated risk register

The output is not a list of facts. It's a **rated register** — risks ordered by severity, each with:

- **Risk description** in one sentence.
- **Severity** (low / medium / high / critical) with the reasoning.
- **Likelihood** (or *materialized* if it already happened).
- **Evidence** — pointers to findings with confidence grades.
- **Open questions** that would change the rating.

Then a one-paragraph executive summary that is genuinely *executive* — what would you tell the decision-maker in 30 seconds.

## Output

For Deep diligence, produce three files:

1. `<target-slug>-executive-summary.md` — one page, the 30-second briefing.
2. `<target-slug>-dossier.md` — full report.
3. `<target-slug>-findings.json` — structured findings against the schema.

The dossier sections (in order):

1. Executive summary
2. Entity and structure
3. Financial picture
4. Leadership and governance
5. Litigation and regulatory
6. Sanctions and adverse media
7. Operations and footprint
8. Reputational and market
9. Risk-area deep dives (only the ones that matter)
10. Risk register (rated)
11. What we couldn't confirm — open questions
12. Method notes — sources used, scope of public-records access, jurisdictions touched
13. Sources (numbered, grouped)
14. Disclaimer

## Don'ts (diligence-specific)

- **Don't render legal conclusions.** "X is liable for Y" — never. "X has been sued by Y for Z; the case is at [stage]; outcome [if known]" — yes.
- **Don't substitute for FCRA-regulated background checks.** If the use case is hiring or credit, say so explicitly in the disclaimer.
- **Don't invent financials.** Headcount × industry-average revenue per employee is a guess, not a finding.
- **Don't speculate about beneficial ownership** beyond what's in registries. "Person X is the real owner" without a registry filing is a C-grade *claim*, not a fact.
- **Don't editorialize on tax structuring.** Note it. Let the reader and their counsel decide.
- **Don't bury negative findings.** If the diligence picture is mixed, the executive summary says so.
