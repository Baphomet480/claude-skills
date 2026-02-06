#!/usr/bin/env bash
# scan_components.sh — Kitchen Sink Inventory Scanner
#
# Walks a project's component directory and compares found exports
# against the tiered Kitchen Sink checklist. Outputs a report of
# EXISTING and MISSING component categories.
#
# Usage:
#   bash scripts/scan_components.sh [component_dir]
#
# Arguments:
#   component_dir  Path to the components directory (default: auto-detected)
#
# The script auto-detects the components directory by checking:
#   1. src/components/
#   2. components/
#   3. app/components/
#
# Output: a categorized EXISTING / MISSING inventory ready for Phase 1 planning.

set -euo pipefail

# --- Configuration -----------------------------------------------------------

# Tier 1: Core Primitives (mandatory)
TIER1_PATTERNS=(
  "button"
  "badge|tag"
  "avatar"
  "card"
  "modal|dialog"
  "alert|toast|notification"
  "input|text-input|textinput"
  "textarea"
  "select|dropdown"
  "checkbox"
  "radio"
  "toggle|switch"
)
TIER1_LABELS=(
  "Button"
  "Badge / Tag"
  "Avatar"
  "Card"
  "Modal / Dialog"
  "Alert / Toast"
  "Text Input"
  "Textarea"
  "Select"
  "Checkbox"
  "Radio"
  "Toggle / Switch"
)

# Tier 2: Navigation & Layout
TIER2_PATTERNS=(
  "tabs|tab-bar|tabbar"
  "breadcrumb"
  "sidebar|sidenav|nav"
  "dropdown-menu|dropdownmenu|menu"
  "accordion|collapsible"
  "tooltip|popover"
)
TIER2_LABELS=(
  "Tabs"
  "Breadcrumbs"
  "Sidebar / Nav"
  "Dropdown Menu"
  "Accordion / Collapsible"
  "Tooltip / Popover"
)

# Tier 3: Data Display
TIER3_PATTERNS=(
  "table|data-table|datatable"
  "stat|kpi|metric"
  "chart|graph"
  "progress|progress-bar|progressbar"
  "skeleton|loader|shimmer"
)
TIER3_LABELS=(
  "Table"
  "Stats / KPI Card"
  "Chart"
  "Progress Bar"
  "Skeleton / Loader"
)

# --- Helpers ------------------------------------------------------------------

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

found_count=0
missing_count=0

detect_component_dir() {
  local candidates=("src/components" "components" "app/components")
  for dir in "${candidates[@]}"; do
    if [[ -d "$dir" ]]; then
      echo "$dir"
      return 0
    fi
  done
  return 1
}

# Search for a component by pattern in the component directory.
# Returns the matched filename(s) or empty string.
search_component() {
  local pattern="$1"
  local dir="$2"
  # Case-insensitive search for files matching the pattern (tsx, ts, jsx, js)
  find "$dir" -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \) \
    | grep -iE "(^|/)($pattern)\.(tsx|ts|jsx|js)$" \
    | head -5 \
    || true
}

scan_tier() {
  local tier_name="$1"
  shift
  local -n patterns_ref="$1"
  shift
  local -n labels_ref="$1"
  shift
  local dir="$1"

  echo -e "\n${BOLD}${CYAN}── $tier_name ──${NC}"
  echo ""

  for i in "${!patterns_ref[@]}"; do
    local pattern="${patterns_ref[$i]}"
    local label="${labels_ref[$i]}"
    local matches
    matches=$(search_component "$pattern" "$dir")

    if [[ -n "$matches" ]]; then
      local first_match
      first_match=$(echo "$matches" | head -1)
      echo -e "  ${GREEN}EXISTING${NC}  $label  →  $first_match"
      ((found_count++)) || true
    else
      echo -e "  ${RED}MISSING ${NC}  $label"
      ((missing_count++)) || true
    fi
  done
}

# --- Main ---------------------------------------------------------------------

COMPONENT_DIR="${1:-}"

if [[ -z "$COMPONENT_DIR" ]]; then
  if ! COMPONENT_DIR=$(detect_component_dir); then
    echo -e "${RED}Error:${NC} No component directory found."
    echo "Checked: src/components/, components/, app/components/"
    echo ""
    echo "Usage: bash scan_components.sh [component_dir]"
    exit 1
  fi
fi

if [[ ! -d "$COMPONENT_DIR" ]]; then
  echo -e "${RED}Error:${NC} Directory '$COMPONENT_DIR' does not exist."
  exit 1
fi

echo -e "${BOLD}Kitchen Sink Component Inventory${NC}"
echo -e "Scanning: ${CYAN}$COMPONENT_DIR${NC}"
echo -e "$(date -Iseconds)"

scan_tier "Tier 1: Core Primitives" TIER1_PATTERNS TIER1_LABELS "$COMPONENT_DIR"
scan_tier "Tier 2: Navigation & Layout" TIER2_PATTERNS TIER2_LABELS "$COMPONENT_DIR"
scan_tier "Tier 3: Data Display" TIER3_PATTERNS TIER3_LABELS "$COMPONENT_DIR"

echo ""
echo -e "${BOLD}Summary${NC}"
echo -e "  ${GREEN}EXISTING:${NC} $found_count"
echo -e "  ${RED}MISSING:${NC}  $missing_count"
echo ""

if [[ "$missing_count" -gt 0 ]]; then
  echo -e "${YELLOW}→ Build MISSING components before assembling the sink page.${NC}"
else
  echo -e "${GREEN}✓ All tracked components found. Ready to assemble the sink.${NC}"
fi
