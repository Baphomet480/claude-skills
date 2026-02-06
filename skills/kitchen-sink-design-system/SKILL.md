---
name: kitchen-sink-design-system
description: Build a Kitchen Sink page that serves as the living source of truth for a project's design system. Use when asked for a Kitchen Sink, Design System, UI Audit, Style Guide, or Component Inventory. Triggers on requests to catalog existing components, create missing ones, or assemble a comprehensive sink page in a Next.js App Router + React + Tailwind CSS project.
---

# Kitchen Sink Design System

Build every component for real, wire it into a single sink page, and let the page prove the design system works.

## Core Philosophy

- **Source of truth** — The sink page is the canonical reference for design direction. If it's not in the sink, it doesn't exist.
- **No placeholders** — Every component rendered on the sink page must be a real, importable module from `/components`. Never use Draft placeholders or TODO stubs.
- **Progressive disclosure** — Start with core primitives, layer in app-level components, finish with data display. Each tier builds on the last.
- **Design-forward** — Don't wait on external dependencies or final designs. Define design direction in the sink first; production pages consume what the sink establishes.

## Input Protocol

1. **Inventory scan** — Read the `/components` directory tree (and any subdirectories like `/ui`, `/shared`). If you cannot see the tree, stop and request it.
   - **Automated option:** Run `bash scripts/scan_components.sh [component_dir]` from the skill directory to get an EXISTING / MISSING report against the tiered checklist.
2. **Dependency check** — Read `package.json` for:
   - Icon libraries (Lucide, Heroicons, Tabler, etc.)
   - Utility helpers (`clsx`, `tailwind-merge`, `class-variance-authority`)
   - Animation libraries (`framer-motion`, `react-spring`)
3. **Tailwind config** — Detect which Tailwind version is in use, then read the appropriate source:
   - **Tailwind v3** — Read `tailwind.config.js` / `tailwind.config.ts` for `theme.extend` (custom colors, spacing, fonts, breakpoints).
   - **Tailwind v4** — No config file required. Read `globals.css`, `app.css`, or the project's main CSS entry for `@theme` blocks and CSS custom properties (`--color-*`, `--spacing-*`, `--font-*`). Also check for `@import "tailwindcss"` as a v4 indicator.
   - **Detection heuristic:** If `tailwind.config.*` exists → v3. If the CSS entry contains `@theme` or `@import "tailwindcss"` → v4.

## Phase 1: Inventory & Plan

Compare existing components against the tiered checklist. Mark each:
- **EXISTING** — import from codebase as-is
- **MISSING** — create in `/components`, then import into the sink

**Tier 1: Core Primitives (mandatory)**
- Typography: H1–H6, paragraph, list (ol/ul), inline code, blockquote
- Buttons: primary, secondary, outline, ghost, destructive; sizes sm/md/lg; disabled state
- Badges / Tags: color variants, dismissible
- Avatars: image, initials fallback, sizes, status indicator
- Icons: render a sampler grid from the project's icon library
- Cards: basic, with header/footer, interactive (hover lift)
- Modals / Dialogs: trigger + overlay + close behavior
- Alerts / Toasts: info, success, warning, error variants
- Form controls: text input, textarea, select, checkbox, radio, toggle/switch, with label + error states

**Tier 2: Navigation & Layout (include when app-level complexity exists)**
- Tabs: horizontal, with active/disabled states
- Breadcrumbs: with separator and current-page indicator
- Sidebar / Nav: collapsible, with active link
- Dropdown menu: trigger + item list + keyboard nav
- Accordion / Collapsible: expand/collapse with animation
- Tooltip / Popover: hover and click triggers

**Tier 3: Data Display (include when data-heavy views exist)**
- Table: sortable headers, striped rows, responsive scroll
- Stats / KPI cards: value, label, trend indicator
- Charts: placeholder pattern using the project's chart library (Recharts, Chart.js, etc.)
- Progress bar / Skeleton loaders: determinate and indeterminate states

## Phase 2: Build Components

For every **MISSING** item:

1. **File naming** — Use the project's existing convention (e.g., `Button.tsx`, `button.tsx`, `ui/button.tsx`). Match what's already there.
2. **Export convention** — Named exports preferred (`export function Button`). Match the project's pattern.
3. **Props interface** — Define a typed props interface. Extend native HTML element props where appropriate (`ButtonHTMLAttributes<HTMLButtonElement>`).
4. **Tailwind usage** — Use tokens from `tailwind.config`; avoid arbitrary values (`w-[37px]`). Use `cn()` or equivalent for conditional classes.
5. **Interactivity** — Components must actually work. Modals open/close with `useState`, toggles toggle, dropdowns expand. No static mockups.
6. **Self-contained** — Rely only on dependencies already in `package.json`. If `clsx`/`tailwind-merge` is missing, add a local `cn()` helper.

## Phase 3: Assemble Sink Page

Create the sink route file based on the project's framework. Use `examples/minimal-sink.tsx` as a starter template.

**Framework routing:**

| Framework | Route file | Notes |
|-----------|-----------|-------|
| Next.js App Router | `/app/sink/page.tsx` | Default. Use `"use client"` directive. |
| Vite + React | `/src/pages/sink.tsx` | Requires a route entry in the router config. |
| Astro | `/src/pages/sink.astro` | Wrap the React sink component in a client island (`client:load`). |

**Architecture rules:**
- `"use client"` directive at top of file (Next.js / React)
- Environment guard: `if (process.env.NEXT_PUBLIC_VERCEL_ENV === "production") return null;`
- Never import other `page.tsx` files — only import components or define helpers locally

**Layout structure:**
- Navigation sidebar (left) — links to each section with scroll anchoring via `id` attributes
- Main content area — sections grouped by tier, each with a heading and `id`

**Section pattern** (repeat for each component):
- Section heading with `id` for anchor linking
- Brief description of the component
- Variant grid: render all variants side-by-side (sizes, colors, states)
- Interactive demo: working example with state (where applicable)

**Chaos laboratory** (dedicated section at end):
- **Token visualization** — Programmatically render the project's Tailwind color palette and spacing scale
- **State matrix** — Side-by-side rendering: default, hover, focus, disabled, loading
- **Dark/light test** — Two columns: one wrapped in a `.dark` class, one in light, showing the same components in both themes

## Phase 4: Verify

Run these checks before considering the sink complete:

### Automated checks

Run these commands from the project root. All must pass.

```bash
# 1. Build — confirms no import cycles, type errors, or missing exports
pnpm build

# 2. Lint — confirms code quality and consistent formatting
pnpm lint

# 3. Accessibility audit (optional but recommended)
pnpm dlx @axe-core/cli http://localhost:3000/sink
```

### Manual checklist

- [ ] **A. Completeness** — Every Tier 1 item is present. Tier 2/3 items included where relevant.
- [ ] **B. Real components** — Every rendered element is imported from `/components` (no inline-only markup pretending to be a component).
- [ ] **C. Interactivity** — Modals open, toggles toggle, tabs switch, dropdowns expand. Every stateful component works.
- [ ] **D. Theming** — Dark/light columns render correctly. No hard-coded colors bypassing Tailwind tokens.
- [ ] **E. Production guard** — Sink page returns `null` in production.
- [ ] **F. No import cycles** — Sink page does not import any `page.tsx` file.

## Anti-patterns

- **Draft placeholders** — `{/* TODO: add button */}` is never acceptable. Build the real component.
- **Arbitrary Tailwind values** — `w-[35px]` or `text-[#ff0000]` instead of using config tokens.
- **Importing page files** — `import X from "../other-page/page"` creates coupling and build issues.
- **Skipping tiers** — Don't jump to Tier 3 charts before Tier 1 buttons exist.
- **Static mockups** — A modal that doesn't open, a toggle that doesn't toggle, a tab bar that doesn't switch.
- **One-off inline components** — If it's rendered in the sink, it belongs in `/components` as an importable module.

## Reference

For detailed per-component specs (expected props, variants, states, accessibility), the sink page section template, and concrete code examples:

**Read:** [references/component-catalog.md](references/component-catalog.md)
