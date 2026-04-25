#!/usr/bin/env bash
# domain-footprint.sh
# Passive reconnaissance for a domain. No active scanning, no credentials, no probes.
# Pulls: whois, DNS records, certificate transparency subdomains, wayback history,
#        and a light vendor-stack inference based on DNS TXT/MX/SPF.
#
# Usage:  ./domain-footprint.sh <domain> [output_dir]
#
# Requires: curl, jq, dig, whois (degrades with warnings if any are missing).
# Idempotent: writes timestamped subdir under output_dir; never overwrites prior runs.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <domain> [output_dir]" >&2
  exit 2
fi

domain="$1"
out_root="${2:-./osint-runs}"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
out="$out_root/${domain}-${ts}"
mkdir -p "$out"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
have() { command -v "$1" >/dev/null 2>&1; }

warn_if_missing() {
  for b in "$@"; do
    if ! have "$b"; then
      log "WARN: '$b' not installed — skipping its phase"
    fi
  done
}

warn_if_missing curl jq dig whois

# --- Phase 1: WHOIS --------------------------------------------------------

if have whois; then
  log "WHOIS"
  whois "$domain" > "$out/whois.txt" 2>&1 || log "WARN: whois exit nonzero"
fi

# --- Phase 2: DNS ----------------------------------------------------------

if have dig; then
  log "DNS"
  {
    echo "# DNS records for $domain"
    echo "## Generated $ts"
    for rrtype in A AAAA MX NS TXT SOA CAA; do
      echo
      echo "## $rrtype"
      dig +short "$domain" "$rrtype" 2>/dev/null || true
    done
    echo
    echo "## DMARC (_dmarc.$domain TXT)"
    dig +short "_dmarc.$domain" TXT 2>/dev/null || true
    echo
    echo "## DKIM (default._domainkey.$domain TXT) — common selector only"
    dig +short "default._domainkey.$domain" TXT 2>/dev/null || true
    echo
    echo "## MTA-STS (_mta-sts.$domain TXT)"
    dig +short "_mta-sts.$domain" TXT 2>/dev/null || true
  } > "$out/dns.txt"
fi

# --- Phase 3: Certificate Transparency / subdomains ------------------------

if have curl && have jq; then
  log "Certificate transparency (crt.sh)"
  if curl -fsSL --max-time 30 \
       "https://crt.sh/?q=%25.${domain}&output=json" \
       -o "$out/crtsh-raw.json" 2>/dev/null; then
    jq -r '.[].name_value' "$out/crtsh-raw.json" 2>/dev/null \
      | tr '[:upper:]' '[:lower:]' \
      | tr -d '*' \
      | sed 's/^\.\+//' \
      | grep -E "(^|\.)${domain//./\\.}$" \
      | sort -u \
      > "$out/subdomains.txt" || true
    log "  $(wc -l < "$out/subdomains.txt" 2>/dev/null || echo 0) unique subdomains"
  else
    log "WARN: crt.sh fetch failed"
  fi
fi

# --- Phase 4: Wayback ------------------------------------------------------

if have curl; then
  log "Wayback Machine availability"
  curl -fsSL --max-time 15 \
    "https://archive.org/wayback/available?url=${domain}" \
    -o "$out/wayback-availability.json" 2>/dev/null \
    || log "WARN: wayback availability fetch failed"

  log "Wayback CDX (first 25 captures)"
  curl -fsSL --max-time 30 \
    "https://web.archive.org/cdx/search/cdx?url=${domain}&output=json&limit=25" \
    -o "$out/wayback-cdx.json" 2>/dev/null \
    || log "WARN: wayback CDX fetch failed"
fi

# --- Phase 5: Stack inference (passive) ------------------------------------

log "Stack inference"
{
  echo "# Stack inference for $domain"
  echo "# Read DNS records and infer vendor relationships."
  echo "# Inference is at most B-grade — confirm against primary sources."
  echo

  if [[ -f "$out/dns.txt" ]]; then
    echo "## MX vendors"
    grep -iE 'google|outlook|protection\.outlook|mimecast|proofpoint|barracuda|fastmail|zoho|amazonses' "$out/dns.txt" \
      | sed 's/^/  - /' || echo "  (none recognized)"
    echo
    echo "## SPF includes"
    grep -i 'v=spf' "$out/dns.txt" | tr ' ' '\n' | grep -i 'include:' | sed 's/^/  - /' || echo "  (none)"
    echo
    echo "## TXT verification fingerprints"
    grep -iE 'google-site|atlassian|adobe|stripe|docusign|zoom|webex|salesforce|hubspot|intercom|asana|notion|github|miro|loom|dropbox|monday|asana|cloudflare|facebook-domain' "$out/dns.txt" \
      | sed 's/^/  - /' || echo "  (none recognized)"
    echo
    echo "## DMARC posture"
    grep -i 'p=' "$out/dns.txt" | sed 's/^/  - /' || echo "  (no DMARC found)"
  else
    echo "  (no DNS data — dig was unavailable)"
  fi
} > "$out/stack-inference.md"

# --- Manifest --------------------------------------------------------------

{
  echo "# Run manifest"
  echo "domain: $domain"
  echo "timestamp_utc: $ts"
  echo "output_dir: $out"
  echo "files:"
  for f in "$out"/*; do
    [[ -f "$f" ]] && echo "  - $(basename "$f"): $(wc -c < "$f") bytes"
  done
} > "$out/manifest.txt"

log "Done. Output: $out"
