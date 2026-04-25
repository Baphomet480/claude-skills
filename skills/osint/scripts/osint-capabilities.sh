#!/usr/bin/env bash
# osint-capabilities.sh
# Probe the local environment for OSINT-relevant tools and credentials.
# Prints a YAML report. Never prints secret values — only presence flags.
#
# Idempotent. Safe to run on any host.
#
# Usage:  ./osint-capabilities.sh [--json]

set -euo pipefail

want_json=false
[[ "${1:-}" == "--json" ]] && want_json=true

bin_present() { command -v "$1" >/dev/null 2>&1 && echo "true" || echo "false"; }
env_present() { [[ -n "${!1:-}" ]] && echo "true" || echo "false"; }
path_present(){ [[ -e "$1" ]] && echo "true" || echo "false"; }

# Network reachability check — short timeout, follow redirects, no body.
reach() {
  if command -v curl >/dev/null 2>&1; then
    curl -sS -o /dev/null -L --max-time 5 -w '%{http_code}' "$1" 2>/dev/null || echo "000"
  else
    echo "no-curl"
  fi
}

# --- gather ----------------------------------------------------------------

bins=(curl jq dig whois git python3 node go awk sed grep openssl tar gzip)
declare -A bin_status
for b in "${bins[@]}"; do bin_status[$b]=$(bin_present "$b"); done

env_keys=(
  GITHUB_TOKEN
  BRAVE_API_KEY
  APIFY_TOKEN
  SHODAN_API_KEY
  HUNTER_API_KEY
  SECURITYTRAILS_API_KEY
  CENSYS_API_ID
  CENSYS_API_SECRET
  VIRUSTOTAL_API_KEY
  URLSCAN_API_KEY
)
declare -A env_status
for k in "${env_keys[@]}"; do env_status[$k]=$(env_present "$k"); done

# Optional PAI / OpenCode integration paths
pai_paths=(
  "$HOME/.opencode/skills/PAI/SKILL.md"
  "$HOME/.opencode/skills/OSINT"
  "$HOME/.opencode/skills/Apify"
  "$HOME/.claude/skills/osint"
  "$HOME/.config/opencode/skills/osint"
)
declare -A pai_status
for p in "${pai_paths[@]}"; do pai_status[$p]=$(path_present "$p"); done

crtsh=$(reach "https://crt.sh/")
wayback=$(reach "https://archive.org/wayback/available?url=example.com")

# --- emit ------------------------------------------------------------------

emit_yaml() {
  echo "osint_capabilities:"
  echo "  generated_at: \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
  echo "  host: \"$(uname -srm)\""
  echo "  binaries:"
  for b in "${bins[@]}"; do echo "    $b: ${bin_status[$b]}"; done
  echo "  env_keys_present:"
  for k in "${env_keys[@]}"; do echo "    $k: ${env_status[$k]}"; done
  echo "  pai_integration_paths:"
  for p in "${pai_paths[@]}"; do echo "    \"$p\": ${pai_status[$p]}"; done
  echo "  network:"
  echo "    crt_sh_http_status: \"$crtsh\""
  echo "    wayback_http_status: \"$wayback\""
  echo "  notes:"
  echo "    - Presence flags only. No secret values are printed."
  echo "    - Missing binaries degrade gracefully — see SKILL.md tool-usage notes."
  echo "    - Network status 200/3xx = reachable; 000 = blocked or no curl."
}

emit_json() {
  # Build JSON without jq dependency.
  printf '{\n'
  printf '  "generated_at": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "host": "%s",\n' "$(uname -srm)"
  printf '  "binaries": {'
  first=true
  for b in "${bins[@]}"; do
    $first || printf ','; first=false
    printf '\n    "%s": %s' "$b" "${bin_status[$b]}"
  done
  printf '\n  },\n'
  printf '  "env_keys_present": {'
  first=true
  for k in "${env_keys[@]}"; do
    $first || printf ','; first=false
    printf '\n    "%s": %s' "$k" "${env_status[$k]}"
  done
  printf '\n  },\n'
  printf '  "pai_integration_paths": {'
  first=true
  for p in "${pai_paths[@]}"; do
    $first || printf ','; first=false
    printf '\n    "%s": %s' "$p" "${pai_status[$p]}"
  done
  printf '\n  },\n'
  printf '  "network": {\n'
  printf '    "crt_sh_http_status": "%s",\n' "$crtsh"
  printf '    "wayback_http_status": "%s"\n' "$wayback"
  printf '  }\n'
  printf '}\n'
}

if $want_json; then emit_json; else emit_yaml; fi
