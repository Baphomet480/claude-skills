# Design System Discovery Reference

Detailed guidance for Phase 0 of the Kitchen Sink workflow. Use this reference to determine whether a project has an existing design system to adopt or needs one established from scratch.

---

## Discovery Manifest — Full Checklist

Scan the project root and common subdirectories for design direction. Check files in this order (stop at each category if found):

### Agent & Editor Configuration

These files often contain design constraints, component conventions, and styling rules:

| File | Location(s) | What to extract |
|---|---|---|
| `GEMINI.md` | Root, `docs/` | Brand colors, typography, voice, component patterns |
| `CLAUDE.md` | Root | Design constraints, coding conventions, component rules |
| `AGENTS.md` | Root | Shared agent instructions including design |
| `COPILOT.md` | Root | Design system references |
| `.cursorrules` | Root | Styling rules, token conventions |
| `.cursor/rules` | `.cursor/` | Same as above, directory format |
| `.clinerules` | Root | Design constraints for Cline |
| `.windsurfrules` | Root | Design constraints for Windsurf |
| `.github/copilot-instructions.md` | `.github/` | Design system references |
| `.agent/skills/*/SKILL.md` | `.agent/skills/` | Project-specific design skills |

### Brand & Style Guides

Dedicated design documentation:

| File | What to extract |
|---|---|
| `brand-guide.md`, `BRAND.md` | Color palette, typography, logo usage, voice |
| `STYLE.md`, `style-guide.md` | Component patterns, spacing, layout rules |
| `CONTENT_GUIDELINES.md` | Voice, tone, content patterns |
| `VOICE.md`, `BRAND_VOICE.md` | Voice adjectives, tone map |
| `design-tokens.json`, `tokens.json` | Structured token definitions |
| `tokens.css` | CSS custom property token definitions |

### Framework-Specific Configuration

| File | Framework | What to extract |
|---|---|---|
| `components.json` | shadcn/ui | Style preset, CSS variables, base color, icon library, aliases, Tailwind config path |
| `tailwind.config.ts` / `.js` | Tailwind v3 | `theme.extend` — custom colors, fonts, spacing, breakpoints |
| `globals.css` (with `@theme`) | Tailwind v4 | CSS custom properties for all tokens |
| `tina/config.ts` | TinaCMS | Collections that define CMS-managed content schemas (affects content patterns) |
| `next.config.ts` | Next.js | Image domains, rewrites, redirects (layout context) |

### shadcn/ui Detection

shadcn/ui projects have a distinctive fingerprint. When detected, the sink skill should leverage its patterns:

**Detection signals:**
- `components.json` exists in project root
- Components in `src/components/ui/` or `components/ui/` follow shadcn naming
- `@/lib/utils` exports a `cn()` function using `clsx` + `tailwind-merge`
- `class-variance-authority` is in `package.json`

**When detected:**
- **Do not recreate** components that shadcn already provides — import them
- Verify installed shadcn components match tier checklist (the scanner handles this)
- Check for customizations: the user may have modified shadcn defaults
- The sink should prove the customized versions work, not the vanilla ones

### TinaCMS Detection

When TinaCMS is present, the sink should account for CMS-managed content:

**Detection signals:**
- `tina/config.ts` or `tina/config.js` exists
- `@tinacms/cli` or `tinacms` in `package.json`

**When detected:**
- Note which content is CMS-managed vs. hardcoded
- Voice & tone guidance should cover both CMS-authored content AND UI chrome (labels, buttons, errors)
- If the project uses TinaCMS for a global collection (e.g., homepage hero, site settings), the sink should reference those schemas for sample content structure

---

## Adopt Mode — Detailed Workflow

When discovery finds existing design direction:

### Step 1: Ingest

Read every discovered file. Build a structured summary:

```markdown
## Design System Summary

### Colors
- Primary: hsl(222, 47%, 31%) — `--primary`
- Secondary: hsl(210, 40%, 96%) — `--secondary`
- Accent: hsl(43, 96%, 56%) — `--accent`
- Destructive: hsl(0, 84%, 60%) — `--destructive`
- Muted: hsl(210, 40%, 96%) — `--muted`

### Typography
- Headings: "Outfit", sans-serif — weight 600–800
- Body: "Inter", sans-serif — weight 400
- Mono: "JetBrains Mono", monospace

### Voice
- Adjectives: confident, approachable, precise
- Tone: professional but warm

### Component Library
- Using shadcn/ui as base
- Custom modifications to Button, Card, Alert
```

### Step 2: Map Tokens

For every extracted value, identify its token type:

| Layer | Example | Purpose |
|---|---|---|
| **Primitive** | `--blue-500: hsl(222, 47%, 31%)` | Raw color value |
| **Semantic** | `--primary: var(--blue-500)` | Purpose mapping |
| **Component** | `--button-bg: var(--primary)` | Component-specific (optional layer) |

### Step 3: Audit for Drift

Scan component files for violations:

```bash
# Find hardcoded hex values in component files
grep -rn '#[0-9a-fA-F]\{3,8\}' src/components/

# Find arbitrary Tailwind values
grep -rn '\[#' src/components/
grep -rn 'w-\[' src/components/
grep -rn 'h-\[' src/components/

# Find non-semantic color usage
grep -rn 'bg-blue-\|bg-red-\|bg-green-\|text-blue-\|text-red-' src/components/
```

### Step 4: Gap Report

Output a delta between documented and implemented:

```
DOCUMENTED but NOT BUILT:
  - Badge (destructive variant) — in brand guide, no component
  - Toast — referenced in guidelines, not implemented

BUILT but NOT DOCUMENTED:
  - Spinner component — exists in /components/ui/spinner.tsx, not in any guide
  - "link" button variant — exists in code, not in brand guide
```

---

## Establish Mode — Detailed Workflow

When no design direction exists:

### Step 1: Extract De-Facto Tokens

Scan the codebase for implicit design decisions:

```bash
# Extract all color values from Tailwind classes
grep -rohn 'bg-[a-z]*-[0-9]*\|text-[a-z]*-[0-9]*\|border-[a-z]*-[0-9]*' src/ \
  | sort | uniq -c | sort -rn | head -30

# Extract font families
grep -rn 'font-family\|fontFamily' src/ tailwind.config.*

# Extract spacing patterns
grep -rohn 'p-[0-9]*\|px-[0-9]*\|py-[0-9]*\|m-[0-9]*\|gap-[0-9]*' src/ \
  | sort | uniq -c | sort -rn | head -20
```

### Step 2: Propose Token System

Generate a `design-tokens.md` with the discovered + recommended palette:

```markdown
# Design Tokens — [Project Name]

## Color Palette

### Primitives
| Token | Value | Source |
|---|---|---|
| `--slate-50` | `hsl(210, 40%, 98%)` | Extracted from existing usage |
| `--slate-900` | `hsl(222, 47%, 11%)` | Extracted from existing usage |
| `--blue-600` | `hsl(222, 47%, 31%)` | Recommended (no primary defined) |

### Semantic Mapping
| Token | Light Mode | Dark Mode | Purpose |
|---|---|---|---|
| `--background` | `var(--slate-50)` | `var(--slate-900)` | Page background |
| `--foreground` | `var(--slate-900)` | `var(--slate-50)` | Default text |
| `--primary` | `var(--blue-600)` | `var(--blue-400)` | Interactive elements |

## Typography Scale
| Level | Size | Weight | Line Height |
|---|---|---|---|
| H1 | 3rem / 48px | 800 | 1.1 |
| H2 | 2.25rem / 36px | 700 | 1.2 |
| Body | 1rem / 16px | 400 | 1.6 |
| Caption | 0.875rem / 14px | 400 | 1.4 |
```

### Step 3: Define Voice

Draft initial voice guidance (see [voice-and-tone.md](voice-and-tone.md) for templates).

### Step 4: Get Approval

Present the token proposal and voice definition to the user. **Do not proceed to Phase 1 until approved.**

---

## Decision Flowchart

```
Start
  │
  ├── Scan for guide files
  │     │
  │     ├── Found? ──→ ADOPT MODE
  │     │                ├── Ingest guides
  │     │                ├── Map tokens (primitive → semantic)
  │     │                ├── Audit components for drift
  │     │                ├── Report gaps
  │     │                └── Proceed to Phase 1
  │     │
  │     └── Not found? ──→ ESTABLISH MODE
  │                        ├── Extract de-facto tokens from code
  │                        ├── Propose token system + voice
  │                        ├── Get user approval
  │                        └── Proceed to Phase 1
  │
  └── (In either mode, check for companion skills to leverage)
```
