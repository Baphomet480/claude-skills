# Search Operators

Operator fluency is the difference between a 5-search investigation and a 50-search one. This file is the cheat sheet.

## Google / general web search

### Core operators

| Operator | Use | Example |
|---|---|---|
| `"exact phrase"` | Force exact match | `"Jason Gurash"` |
| `-term` | Exclude | `"jason smith" -basketball` |
| `OR` (capital) | Either | `acme OR "acme corp"` |
| `site:` | Restrict to a domain | `site:linkedin.com/in "VP Engineering" "Phoenix"` |
| `inurl:` | URL contains | `inurl:contact site:acme.com` |
| `intitle:` | Title contains | `intitle:"about us" site:acme.com` |
| `filetype:` | File extension | `filetype:pdf "annual report" site:acme.com` |
| `before:YYYY-MM-DD` | Older than date | `acme acquisition before:2024-01-01` |
| `after:YYYY-MM-DD` | Newer than date | `acme layoffs after:2025-01-01` |

### Useful patterns

**Find someone's LinkedIn without the LinkedIn search wall:**
```
site:linkedin.com/in "Full Name" "Company"
site:linkedin.com/in "Full Name" "City"
```

**Find a company's leadership team:**
```
site:companydomain.com "leadership" OR "team" OR "about"
site:linkedin.com/in "[Company Name]" "VP" OR "Director" OR "Chief"
```

**Find decision-maker contacts (B2B):**
```
site:linkedin.com/in "Acme" ("IT Director" OR "VP Engineering" OR "CTO")
site:companydomain.com filetype:pdf "org chart" OR "leadership"
```

**Find recent news / triggers:**
```
"Acme Corp" (acquisition OR funding OR layoffs OR "new CEO" OR "data breach") after:2025-01-01
"Acme Corp" "press release" after:2025-06-01
```

**Find slide decks and reports** (often unintentionally indexed):
```
"Acme Corp" filetype:pptx
"Acme Corp" filetype:pdf "internal" OR "confidential"   # caution — read what's actually public
```

**Find email patterns:**
```
"@acme.com" site:linkedin.com
"firstname.lastname@acme.com" OR "f.lastname@acme.com"
intext:"@acme.com" -site:acme.com
```

(Note: respect the ethics file — pattern inference is fine for sales discovery; harvesting at scale isn't.)

## LinkedIn X-ray (via Google)

LinkedIn's own search hides a lot behind authentication. Google indexes profile snippets you can read without logging in.

```
site:linkedin.com/in "[Name]"
site:linkedin.com/in "[Title]" "[Company]"
site:linkedin.com/in "[Skill]" "[City]"
site:linkedin.com/company/ "[Company name variant]"
```

For finding company employees by role:
```
site:linkedin.com/in "Acme Corp" "infrastructure" OR "vmware" OR "azure"
```

## GitHub

For tech stack and engineering footprint:

```
"acme.com" in:file                            # mentions of the company in code
user:acme-corp                                # all repos under an org
user:acme-corp language:terraform             # filter by language
"acme-corp" filename:Dockerfile               # config-file mentions
org:acme-corp pushed:>2025-01-01              # recent activity
```

For finding employees:
```
location:"Phoenix, AZ" language:python        # via the GitHub user search UI
```

GitHub's free API is generous (60 req/hr unauth, 5000 req/hr with a token). Set `GITHUB_TOKEN` if you have one.

## DNS / WHOIS / cert transparency

Passive infrastructure recon — no probing of the target's hosts.

```bash
# DNS
dig acme.com ANY +short
dig acme.com MX +short
dig acme.com TXT +short                    # SPF, DMARC, vendor verification tokens
dig _dmarc.acme.com TXT +short

# WHOIS
whois acme.com                             # registrar, dates, sometimes contact

# Subdomains via certificate transparency (no scanning involved)
curl -s "https://crt.sh/?q=%25.acme.com&output=json" | jq -r '.[].name_value' | sort -u

# Reverse DNS / IP space
dig -x 203.0.113.42 +short
whois 203.0.113.42                          # netblock owner
```

DNS TXT records are gold for tech stack inference: SPF reveals email vendors (Microsoft 365, Google Workspace, Mailgun); verification TXT records reveal SaaS the company uses (`google-site-verification`, `atlassian-domain-verification`, `docusign=...`, `apple-domain-verification=...`, `_globalsign-domain-verification=...`, etc.).

## Wayback Machine

For history and context:

```
https://web.archive.org/web/*/acme.com                          # all snapshots
https://web.archive.org/web/2020*/acme.com/about                # specific year
```

API form (machine-readable):
```
https://web.archive.org/cdx/search/cdx?url=acme.com&output=json&limit=20&from=20200101
```

Use cases: see what the company looked like before a rebrand, recover a deleted leadership page, find old job postings that reveal stack history.

## Search engine fan-out

Don't rely on Google alone. The same query in different engines surfaces different results:

- Google — primary. Best for general web.
- Bing — sometimes better for LinkedIn snippets, sometimes surfaces sites Google doesn't.
- DuckDuckGo — privacy-respecting but limited corpus.
- Brave Search — independent index, often surfaces non-mainstream results.
- Marginalia / Kagi — niche; useful for long-tail.

If `BRAVE_API_KEY` is set, prefer it for programmatic searches.

## Specialty engines

- **`crt.sh`** — certificate transparency, finds subdomains and historical certs.
- **`shodan.io`** — internet-exposed services. **Read-only public results are fine; do not run active scans against the target.**
- **`viewdns.info`** — DNS history, reverse IP lookup.
- **`builtwith.com`** / **`wappalyzer.com`** — tech stack inference (often paywalled deeper data; the free signal is usable).
- **`hunter.io`** — email patterns (free tier; rate-limited).
- **`opencorporates.com`** — global corporate registries.
- **`SEC EDGAR`** — US public company filings.
- **`Companies House`** (UK), **state Secretary-of-State sites** (US), **CNMV** (Spain), etc. for company filings.

## Anti-patterns

- **Single-engine over-reliance.** If you didn't find it in Google, don't conclude it doesn't exist.
- **Boolean stew.** `(("Acme" OR "Acme Corp") AND ("CTO" OR "CIO") AND -"resigned")` rarely outperforms two simpler queries.
- **Overuse of quotes.** Quotes prevent fuzzy matching that often surfaces the right result with a typo.
- **Forgetting to time-bound.** A 2018 article ranking #1 for a 2026 question is a constant trap.
