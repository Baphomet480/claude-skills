#!/usr/bin/env bash
# verify-domain.sh — portable, idempotent passive recon on a single domain.
#
# Uses only standard tools available on most *nix systems:
#   - dig (bind-utils / dnsutils)
#   - curl
#   - jq (optional — output is still readable without it)
#
# No API keys required. All sources are public and passive.
#
# Usage:
#   ./verify-domain.sh <domain>
#   ./verify-domain.sh acme.com
#
# Exit codes:
#   0  success
#   1  missing argument
#   2  required tool not found
#
# Output: structured sections to stdout. Pipe to a file or process further.

set -euo pipefail

DOMAIN="${1:-}"

if [[ -z "$DOMAIN" ]]; then
  echo "Usage: $0 <domain>" >&2
  exit 1
fi

# Strip protocol and path if user pasted a URL
DOMAIN="${DOMAIN#http://}"
DOMAIN="${DOMAIN#https://}"
DOMAIN="${DOMAIN%%/*}"
DOMAIN="${DOMAIN,,}"  # lowercase

# Tool checks
missing=()
for tool in dig curl; do
  if ! command -v "$tool" &>/dev/null; then
    missing+=("$tool")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "Required tool(s) not found: ${missing[*]}" >&2
  echo >&2
  echo "Install hints:" >&2
  echo "  Debian/Ubuntu:   sudo apt-get install -y dnsutils curl" >&2
  echo "  Rocky/RHEL:      sudo dnf install -y bind-utils curl" >&2
  echo "  Arch:            sudo pacman -S bind curl" >&2
  echo "  macOS (brew):    brew install bind curl  # dig usually ships with macOS" >&2
  exit 2
fi

HAS_JQ=0
if command -v jq &>/dev/null; then
  HAS_JQ=1
fi

NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "============================================================"
echo " OSINT verify-domain.sh"
echo " Target:    $DOMAIN"
echo " Generated: $NOW"
echo "============================================================"
echo

# ---------------------------------------------------------------
section() {
  echo
  echo "--- $1 ---"
}

# ---------------------------------------------------------------
section "DNS records"

for rtype in A AAAA MX TXT NS CNAME SOA; do
  result="$(dig +short "$DOMAIN" "$rtype" 2>/dev/null || true)"
  if [[ -n "$result" ]]; then
    echo "[$rtype]"
    echo "$result" | sed 's/^/  /'
  fi
done

# ---------------------------------------------------------------
section "Email auth (SPF / DKIM / DMARC)"

spf="$(dig +short TXT "$DOMAIN" 2>/dev/null | grep -i 'v=spf1' || true)"
dmarc="$(dig +short TXT "_dmarc.$DOMAIN" 2>/dev/null || true)"

echo "SPF:   ${spf:-<none found>}"
echo "DMARC: ${dmarc:-<none found>}"
# DKIM selectors are arbitrary — try common ones
for selector in default google selector1 selector2 k1 mail dkim; do
  result="$(dig +short TXT "${selector}._domainkey.$DOMAIN" 2>/dev/null || true)"
  if [[ -n "$result" ]]; then
    echo "DKIM[$selector]: present"
  fi
done

# ---------------------------------------------------------------
section "HTTP response headers (https)"

# -s silent, -I HEAD, -L follow redirects, -m timeout, --max-redirs cap
if curl -sIL -m 10 --max-redirs 5 "https://$DOMAIN" 2>/dev/null | head -50; then
  :
else
  echo "(https HEAD failed — site may be http-only, blocking, or unreachable)"
fi

# ---------------------------------------------------------------
section "Subdomains via crt.sh (certificate transparency)"

# crt.sh accepts a wildcard query. Some queries time out — be patient.
if [[ $HAS_JQ -eq 1 ]]; then
  curl -s -m 30 "https://crt.sh/?q=%25.${DOMAIN}&output=json" \
    | jq -r '.[].name_value' 2>/dev/null \
    | tr ',' '\n' \
    | grep -v '^*' \
    | sort -u \
    | head -200 || echo "(crt.sh query failed or returned no results)"
else
  echo "(install jq for parsed output. Raw URL:"
  echo "  https://crt.sh/?q=%25.${DOMAIN}&output=json )"
fi

# ---------------------------------------------------------------
section "Hosting hints from A records"

a_records="$(dig +short "$DOMAIN" A 2>/dev/null || true)"
if [[ -n "$a_records" ]]; then
  for ip in $a_records; do
    # Best-effort cloud detection by reverse DNS
    rdns="$(dig +short -x "$ip" 2>/dev/null || true)"
    echo "$ip -> ${rdns:-<no PTR>}"
  done
else
  echo "(no A records)"
fi

# ---------------------------------------------------------------
section "Wayback Machine availability"

# Wayback's "available" endpoint returns JSON with closest snapshot
wayback="$(curl -s -m 10 "https://archive.org/wayback/available?url=${DOMAIN}" 2>/dev/null || true)"
if [[ -n "$wayback" ]]; then
  echo "$wayback"
  echo
  echo "Browse history:"
  echo "  https://web.archive.org/web/*/${DOMAIN}"
fi

# ---------------------------------------------------------------
echo
echo "============================================================"
echo " Done. Review above for tech-stack, hosting, related"
echo " infrastructure, and historical change signals."
echo " Next steps depend on the workflow:"
echo "  - B2B prospecting: combine with stakeholder map"
echo "  - Domain-tech: cross-reference subdomains with services"
echo "  - Threat: compare domain age vs claimed company history"
echo "============================================================"
