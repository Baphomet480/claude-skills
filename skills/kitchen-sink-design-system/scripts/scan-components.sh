#!/usr/bin/env bash
# scan-components.sh -- Kitchen Sink Inventory Scanner (Multi-Framework)
#
# Walks a project's component directory and compares found exports
# against the tiered Kitchen Sink checklist. Also performs Phase 0
# design system discovery -- detecting brand guides, design tokens,
# component library (shadcn, etc.), and CVA usage.
#
# Supports: React/Next.js (primary), Astro, SvelteKit, Nuxt, Static HTML
#
# Usage:
#   bash scripts/scan-components.sh [component_dir]
#
# Arguments:
#   component_dir  Path to the components directory (default: auto-detected based on framework)
#
# Output: Framework detection + Phase 0 discovery report + categorized EXISTING / MISSING inventory.

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
  "header|navbar"
  "footer"
)
TIER2_LABELS=(
  "Tabs"
  "Breadcrumbs"
  "Sidebar / Nav"
  "Dropdown Menu"
  "Accordion / Collapsible"
  "Tooltip / Popover"
  "Header / Navbar"
  "Footer"
)

# Tier 3: Content-Author Components (CMS-dependent)
TIER3_PATTERNS=(
  "callout|admonition|notice"
  "figure|image-caption|figcaption"
  "cta|call-to-action"
  "embed|youtube|video"
  "card-grid|cardgrid"
)
TIER3_LABELS=(
  "Callout / Admonition"
  "Figure / Image with Caption"
  "Button / CTA"
  "Embed (YouTube, etc.)"
  "Card Grid"
)

# Tier 4: Data Display
TIER4_PATTERNS=(
  "table|data-table|datatable"
  "stat|kpi|metric"
  "chart|graph"
  "progress|progress-bar|progressbar"
  "skeleton|loader|shimmer"
)
TIER4_LABELS=(
  "Table"
  "Stats / KPI Card"
  "Chart"
  "Progress Bar"
  "Skeleton / Loader"
)

# Phase 0: Discovery file patterns
GUIDE_FILES=(
  "GEMINI.md"
  "CLAUDE.md"
  "AGENTS.md"
  "COPILOT.md"
  ".cursorrules"
  ".clinerules"
  ".windsurfrules"
  "brand-guide.md"
  "BRAND.md"
  "STYLE.md"
  "style-guide.md"
  "CONTENT_GUIDELINES.md"
  "VOICE.md"
  "BRAND_VOICE.md"
)

GUIDE_DIR_FILES=(
  ".cursor/rules"
  ".github/copilot-instructions.md"
)

TOKEN_FILES=(
  "design-tokens.json"
  "tokens.json"
  "tokens.css"
)

# --- Helpers ------------------------------------------------------------------

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

found_count=0
missing_count=0
guide_count=0
discovery_mode=""
detected_framework=""

# --- Framework Detection ------------------------------------------------------

detect_framework() {
  if [[ -f "next.config.js" || -f "next.config.ts" || -f "next.config.mjs" ]]; then
    detected_framework="nextjs"
  elif [[ -f "astro.config.mjs" || -f "astro.config.ts" || -f "astro.config.js" ]]; then
    detected_framework="astro"
  elif [[ -f "nuxt.config.ts" || -f "nuxt.config.js" ]]; then
    detected_framework="nuxt"
  elif [[ -f "svelte.config.js" || -f "svelte.config.ts" ]]; then
    detected_framework="sveltekit"
  else
    detected_framework="static"
  fi
}

framework_label() {
  case "$detected_framework" in
    nextjs)    echo "Next.js (React)" ;;
    astro)     echo "Astro" ;;
    nuxt)      echo "Nuxt (Vue)" ;;
    sveltekit) echo "SvelteKit" ;;
    static)    echo "Static HTML/CSS" ;;
    *)         echo "Unknown" ;;
  esac
}

# Detect the component directory based on framework
detect_component_dir() {
  case "$detected_framework" in
    astro)
      local candidates=("src/components" "components")
      for dir in "${candidates[@]}"; do
        if [[ -d "$dir" ]]; then
          echo "$dir"
          return 0
        fi
      done
      ;;
    *)
      # React, Next.js, SvelteKit, Nuxt, Static
      local candidates=("src/components" "components" "app/components")
      for dir in "${candidates[@]}"; do
        if [[ -d "$dir" ]]; then
          echo "$dir"
          return 0
        fi
      done
      ;;
  esac
  return 1
}

# --- Component Search ---------------------------------------------------------

search_component() {
  local pattern="$1"
  local dir="$2"

  case "$detected_framework" in
    astro)
      find "$dir" -maxdepth 3 -type f \( -name "*.astro" -o -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \) \
        | grep -iE "(^|/)($pattern)\.(astro|tsx|ts|jsx|js)$" \
        | head -5 \
        || true
      ;;
    sveltekit)
      find "$dir" -maxdepth 3 -type f \( -name "*.svelte" -o -name "*.ts" -o -name "*.js" \) \
        | grep -iE "(^|/)($pattern)\.(svelte|ts|js)$" \
        | head -5 \
        || true
      ;;
    nuxt)
      find "$dir" -maxdepth 3 -type f \( -name "*.vue" -o -name "*.ts" -o -name "*.js" \) \
        | grep -iE "(^|/)($pattern)\.(vue|ts|js)$" \
        | head -5 \
        || true
      ;;
    *)
      # React / Next.js / Static
      find "$dir" -maxdepth 3 -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" -o -name "*.html" \) \
        | grep -iE "(^|/)($pattern)\.(tsx|ts|jsx|js|html)$" \
        | head -5 \
        || true
      ;;
  esac
}

scan_tier() {
  local tier_name="$1"
  shift
  local -n patterns_ref="$1"
  shift
  local -n labels_ref="$1"
  shift
  local dir="$1"

  echo -e "\n${BOLD}${CYAN}-- $tier_name --${NC}"
  echo ""

  for i in "${!patterns_ref[@]}"; do
    local pattern="${patterns_ref[$i]}"
    local label="${labels_ref[$i]}"
    local matches
    matches=$(search_component "$pattern" "$dir")

    if [[ -n "$matches" ]]; then
      local first_match
      first_match=$(echo "$matches" | head -1)
      echo -e "  ${GREEN}EXISTING${NC}  $label  ->  $first_match"
      ((found_count++)) || true
    else
      echo -e "  ${RED}MISSING ${NC}  $label"
      ((missing_count++)) || true
    fi
  done
}

# --- Phase 0: Discovery ------------------------------------------------------

scan_discovery() {
  echo -e "\n${BOLD}${MAGENTA}=== Phase 0: Design System Discovery ===${NC}\n"

  # Framework detection
  echo -e "${BOLD}${CYAN}-- Framework Detection --${NC}\n"
  echo -e "  ${GREEN}DETECTED${NC}  $(framework_label)  ${DIM}($detected_framework)${NC}"
  echo ""

  # Check for brand/style guide files
  echo -e "${BOLD}${CYAN}-- Brand & Style Guides --${NC}\n"

  for file in "${GUIDE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
      echo -e "  ${GREEN}FOUND${NC}   $file"
      ((guide_count++)) || true
    fi
  done

  for file in "${GUIDE_DIR_FILES[@]}"; do
    if [[ -f "$file" ]]; then
      echo -e "  ${GREEN}FOUND${NC}   $file"
      ((guide_count++)) || true
    fi
  done

  # Check docs/ directory
  if [[ -d "docs" ]]; then
    local doc_guides
    doc_guides=$(find docs/ -maxdepth 2 -type f \( -iname "*brand*" -o -iname "*style*" -o -iname "*design*" -o -iname "*voice*" -o -iname "*tone*" \) 2>/dev/null || true)
    if [[ -n "$doc_guides" ]]; then
      while IFS= read -r doc; do
        echo -e "  ${GREEN}FOUND${NC}   $doc"
        ((guide_count++)) || true
      done <<< "$doc_guides"
    fi
  fi

  echo ""

  # Check for design token files
  echo -e "${BOLD}${CYAN}-- Design Tokens --${NC}\n"

  for file in "${TOKEN_FILES[@]}"; do
    if [[ -f "$file" ]]; then
      echo -e "  ${GREEN}FOUND${NC}   $file"
      ((guide_count++)) || true
    fi
  done

  # Check for CSS custom properties in common CSS files
  local css_candidates=("globals.css" "src/globals.css" "app/globals.css" "src/app/globals.css" "src/index.css" "src/styles/global.css" "src/styles/globals.css")

  for css_file in "${css_candidates[@]}"; do
    if [[ -f "$css_file" ]]; then
      local token_count
      token_count=$(grep -c '\-\-' "$css_file" 2>/dev/null || echo "0")
      if [[ "$token_count" -gt 0 ]]; then
        echo -e "  ${GREEN}FOUND${NC}   $css_file  ${DIM}($token_count CSS custom properties)${NC}"
      fi

      # Tailwind v4 detection
      if grep -q '@theme\|@import "tailwindcss"' "$css_file" 2>/dev/null; then
        echo -e "  ${GREEN}FOUND${NC}   $css_file  ${DIM}(Tailwind v4 @theme detected)${NC}"
      fi
    fi
  done

  # Check Tailwind v3 config
  for tw_config in "tailwind.config.ts" "tailwind.config.js" "tailwind.config.mjs"; do
    if [[ -f "$tw_config" ]]; then
      echo -e "  ${GREEN}FOUND${NC}   $tw_config  ${DIM}(Tailwind v3)${NC}"
    fi
  done

  echo ""

  # Check for component library
  echo -e "${BOLD}${CYAN}-- Component Library --${NC}\n"

  if [[ -f "components.json" ]]; then
    echo -e "  ${GREEN}FOUND${NC}   components.json  ${DIM}(shadcn/ui detected)${NC}"
    local style
    style=$(grep -o '"style"[[:space:]]*:[[:space:]]*"[^"]*"' components.json 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || true)
    if [[ -n "$style" ]]; then
      echo -e "         ${DIM}Style: $style${NC}"
    fi
    ((guide_count++)) || true
  fi

  # Check for package.json dependencies
  if [[ -f "package.json" ]]; then
    if grep -q '"class-variance-authority"' package.json 2>/dev/null; then
      echo -e "  ${GREEN}FOUND${NC}   class-variance-authority  ${DIM}(CVA installed)${NC}"
    else
      echo -e "  ${YELLOW}MISSING${NC} class-variance-authority  ${DIM}(recommended for variant system)${NC}"
    fi

    if grep -q '"clsx"\|"tailwind-merge"' package.json 2>/dev/null; then
      echo -e "  ${GREEN}FOUND${NC}   clsx / tailwind-merge  ${DIM}(cn() utilities available)${NC}"
    fi

    if grep -q '"tinacms"\|"@tinacms/cli"' package.json 2>/dev/null; then
      echo -e "  ${GREEN}FOUND${NC}   TinaCMS  ${DIM}(CMS-managed content detected)${NC}"
    fi

    if grep -q '"framer-motion"\|"motion"' package.json 2>/dev/null; then
      echo -e "  ${GREEN}FOUND${NC}   Framer Motion  ${DIM}(animation library available)${NC}"
    fi

    if grep -q '"lucide-react"\|"lucide"' package.json 2>/dev/null; then
      echo -e "  ${GREEN}FOUND${NC}   Lucide  ${DIM}(icon library)${NC}"
    fi
  fi

  echo ""

  # Check for CVA usage in component files
  if [[ "$detected_framework" != "static" ]]; then
    echo -e "${BOLD}${CYAN}-- CVA Pattern Usage --${NC}\n"

    local comp_dir="${1:-}"
    if [[ -n "$comp_dir" && -d "$comp_dir" ]]; then
      local cva_files
      cva_files=$(grep -rl "from \"class-variance-authority\"\|from 'class-variance-authority'" "$comp_dir" 2>/dev/null || true)
      local total_components
      total_components=$(find "$comp_dir" -maxdepth 3 -type f \( -name "*.tsx" -o -name "*.jsx" -o -name "*.astro" -o -name "*.svelte" -o -name "*.vue" \) | wc -l)

      if [[ -n "$cva_files" ]]; then
        local cva_count
        cva_count=$(echo "$cva_files" | wc -l)
        echo -e "  ${GREEN}$cva_count${NC} / ${total_components} components use CVA pattern"

        while IFS= read -r f; do
          echo -e "    ${DIM}+ $f${NC}"
        done <<< "$cva_files"
      else
        echo -e "  ${YELLOW}0${NC} / ${total_components} components use CVA pattern"
        echo -e "  ${DIM}Consider adopting CVA for consistent base + variant architecture${NC}"
      fi
    else
      echo -e "  ${DIM}Skipped (no component directory)${NC}"
    fi

    echo ""
  fi

  # Determine discovery mode
  if [[ "$guide_count" -gt 0 ]]; then
    discovery_mode="ADOPT"
    echo -e "${BOLD}Discovery mode: ${GREEN}ADOPT${NC} -- existing design direction found (${guide_count} guide files)${NC}"
    echo -e "${DIM}-> Ingest guides, map tokens, audit for drift, surface gaps${NC}"
  else
    discovery_mode="ESTABLISH"
    echo -e "${BOLD}Discovery mode: ${YELLOW}ESTABLISH${NC} -- no design direction found${NC}"
    echo -e "${DIM}-> Extract de-facto tokens, propose system, define voice, get approval${NC}"
  fi
}

# --- Main ---------------------------------------------------------------------

# Detect framework first
detect_framework

COMPONENT_DIR="${1:-}"

if [[ -z "$COMPONENT_DIR" ]]; then
  if ! COMPONENT_DIR=$(detect_component_dir); then
    echo -e "${RED}Error:${NC} No component directory found."
    case "$detected_framework" in
      astro)
        echo "Checked: src/components/, components/"
        ;;
      *)
        echo "Checked: src/components/, components/, app/components/"
        ;;
    esac
    echo ""
    echo "Usage: bash scan-components.sh [component_dir]"
    exit 1
  fi
fi

if [[ ! -d "$COMPONENT_DIR" ]]; then
  echo -e "${RED}Error:${NC} Directory '$COMPONENT_DIR' does not exist."
  exit 1
fi

echo -e "${BOLD}Kitchen Sink Component Inventory${NC}"
echo -e "Framework: ${CYAN}$(framework_label)${NC}"
echo -e "Scanning:  ${CYAN}$COMPONENT_DIR${NC}"
echo -e "$(date -Iseconds)"

# Phase 0: Discovery
scan_discovery "$COMPONENT_DIR"

# Phase 1: Component Inventory
echo -e "\n${BOLD}${MAGENTA}=== Phase 1: Component Inventory ===${NC}"

scan_tier "Tier 1: Core Primitives" TIER1_PATTERNS TIER1_LABELS "$COMPONENT_DIR"
scan_tier "Tier 2: Navigation & Layout" TIER2_PATTERNS TIER2_LABELS "$COMPONENT_DIR"
scan_tier "Tier 3: Content-Author Components" TIER3_PATTERNS TIER3_LABELS "$COMPONENT_DIR"
scan_tier "Tier 4: Data Display" TIER4_PATTERNS TIER4_LABELS "$COMPONENT_DIR"

echo ""
echo -e "${BOLD}Summary${NC}"
echo -e "  ${GREEN}EXISTING:${NC} $found_count"
echo -e "  ${RED}MISSING:${NC}  $missing_count"
echo ""

if [[ "$missing_count" -gt 0 ]]; then
  echo -e "${YELLOW}-> Build MISSING components before assembling the sink page.${NC}"
else
  echo -e "${GREEN}+ All tracked components found. Ready to assemble the sink.${NC}"
fi
