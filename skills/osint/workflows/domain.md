# Workflow: Domain / IP

For investigating a domain, IP, or netblock — passively. This is reconnaissance, not active scanning. We read what's already public; we do not probe.

**Hard rule:** No active scanning, port scanning, vulnerability scanning, fuzzing, or anything that touches the target's infrastructure beyond a normal browser request. Even when "they won't notice."

## Pre-flight

- Confirm the user has a lawful purpose: their own domain, an authorized engagement, journalism, threat-intel, or general due diligence. If the request is "scan this competitor for vulnerabilities," decline.
- Confirm scope. A single domain? A whole org's footprint? A specific subdomain?

## Phase 1 — Ownership and registration

```bash
whois acme.com
```

Capture: registrar, creation date, last update, expiration, registrant (often privacy-protected; that's a finding, not a failure), name servers.

For TLDs that strip detail (most do post-GDPR), pull what you can and note the privacy redaction.

If the registrant is named, check whether the same name owns other domains (`viewdns.info` reverse-WHOIS, or domain-broker tools). This is how you find the same operator behind multiple properties.

## Phase 2 — DNS landscape

```bash
dig acme.com ANY +short          # try first, often filtered
dig acme.com A +short
dig acme.com AAAA +short
dig acme.com MX +short
dig acme.com TXT +short
dig acme.com NS +short
dig acme.com CNAME +short

dig _dmarc.acme.com TXT +short
dig _domainkey.acme.com TXT +short
dig default._domainkey.acme.com TXT +short
```

Read the records like a stack confession:

- **MX** → email vendor.
- **SPF** (in TXT) → every authorized sender. Each `include:` is a vendor relationship.
- **DMARC** → policy maturity (`p=none` is widespread but a sign of incomplete deployment; `p=quarantine`/`p=reject` indicates serious posture).
- **Verification TXT records** → SaaS the org uses (`google-site-verification`, `MS=`, `atlassian-domain-verification`, `docusign=`, `apple-domain-verification`, `_globalsign-domain-verification`, etc.).
- **NS** → DNS hosting vendor (Cloudflare, Route53, Azure DNS, GoDaddy, on-prem BIND).

## Phase 3 — Subdomain enumeration (passive)

Use certificate transparency, not active brute-forcing.

```bash
curl -s "https://crt.sh/?q=%25.acme.com&output=json" | jq -r '.[].name_value' | sort -u
```

Or via the web at `crt.sh/?q=%25.acme.com`.

Other passive sources:

- `dnsdumpster.com` (free, web)
- Google: `site:acme.com -www`
- Wayback CDX: `https://web.archive.org/cdx/search/cdx?url=*.acme.com&output=json&fl=original&collapse=urlkey`

What to capture:

- Production subdomains (often `app.`, `api.`, `auth.`, `mail.`)
- Vendor-hosted properties (`acme.atlassian.net`, `acme.zendesk.com`, `acme.salesforce.com`, etc.) — these are tech-stack confessions.
- Staging / dev (`stage.`, `dev.`, `qa.`) — useful as observations; do not probe them.
- VPN / remote access (`vpn.`, `remote.`, `connect.`) — note presence; do not interact.
- Acquired-company subdomains under the parent — historical data and integration progress signals.

## Phase 4 — Hosting and CDN

From the apex and main subdomains:

- **A / AAAA** → IP. Reverse to the netblock owner via WHOIS on the IP. Distinguishes self-hosted from cloud-hosted from CDN-fronted.
- **CDN signals** — Cloudflare, Akamai, Fastly, CloudFront present in CNAMEs or IP ranges.
- **Cloud signals** — Azure (`azurewebsites.net`, `azure.com` ranges), AWS (`amazonaws.com`, `cloudfront.net`), GCP, Vercel, Netlify, Heroku.

Geolocation of the IP is a weak signal — the company isn't necessarily where the IP is. Note jurisdiction implications for regulated industries.

## Phase 5 — Web fingerprint (passive)

A normal browser fetch reveals plenty without probing:

- HTTP response headers: `Server`, `X-Powered-By`, `Set-Cookie` patterns, security headers.
- Source HTML: framework (`__NEXT_DATA__`, `data-react`, Vue, Angular signals), CMS (WordPress's `wp-content`, Drupal's signatures), analytics (GA4, Plausible, Mixpanel), tag manager, marketing pixels.
- `robots.txt` and `sitemap.xml` — what they're publishing.
- `/.well-known/security.txt` if it exists.

`builtwith.com` and `wappalyzer.com` summarize this; their free output is usable.

## Phase 6 — Historical view

Use the Wayback Machine:

- First snapshot (when did this domain start being used?)
- Major redesigns / rebrands (note dates)
- Old leadership pages, old job postings — often revealing
- Old DNS records via `viewdns.info` or `securitytrails` (free tier).

Historical data answers questions like: "When did they switch from on-prem to cloud?" "When did the previous CTO leave?" "Did they used to operate under a different name?"

## Phase 7 — Threat / abuse posture (selective)

Only when relevant:

- **Shodan public results** — `shodan.io` web search shows what services are publicly exposed on the netblock. **Do not run shodan API scans against the target.** Read what's already indexed.
- **Censys public results** — same caveat.
- **VirusTotal** — has the domain been flagged for malware/phishing in the past? Read-only.
- **URLScan.io** — historical scans others have run.
- **HaveIBeenPwned domain breach summary** — if the user owns the domain or has authorization. Do not enrich third-party domains for stalking/harassment purposes.

## Output

Produce `<domain>-dossier.md`. Sections:

1. Registration card — registrar, dates, registrant (or redaction note)
2. DNS profile — A/MX/TXT/NS, with stack inferences
3. Subdomains — the full list, categorized
4. Hosting / CDN / cloud
5. Web fingerprint — frameworks, CMS, analytics, marketing stack
6. Historical context — first appearance, major changes
7. Threat posture (if examined) — public flagging, exposed services per public scanners
8. Inferences and confidence — what we believe about the org from this footprint
9. Open questions
10. Sources

## Don'ts (domain-specific)

- **No active scanning.** Repeat. No nmap, masscan, ZMap, dirb, gobuster, nikto, or anything that probes the host.
- Don't crawl past `robots.txt` exclusions even if you can.
- Don't include passwords, API keys, or secrets discovered via Wayback or other public sources without the user's explicit instruction. The right move is usually to disclose to the affected entity.
- Don't infer ownership of a property from a single shared third-party service (CDN, registrar) — too many domains share Cloudflare for that to be diagnostic.
