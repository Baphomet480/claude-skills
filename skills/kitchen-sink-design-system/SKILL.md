---
name: kitchen-sink-design-system
description: Kitchen Sink design system workflow for any frontend stack — Next.js, Hugo, Astro, SvelteKit, Nuxt, or plain HTML. Use when asked for a Kitchen Sink page, Design System, UI Audit, Style Guide, or Component Inventory, or when a project needs a component inventory plus component creation and a sink page implementation.
---

# Kitchen Sink Design System

Build every component for real, wire it into a single sink page, and let the page prove the design system works.

## Core Philosophy

- **Source of truth** — The sink page is the canonical reference for design direction. If it's not in the sink, it doesn't exist.
- **No placeholders** — Every component rendered on the sink page must be a real, importable module. Never use draft placeholders or TODO stubs.
- **Layered semantics** — Every component follows a base + variant architecture. Shared structure in the base, visual differences in the variant layer.
- **Progressive disclosure** — Start with core primitives, layer in app-level components, finish with data display. Each tier builds on the last.
- **Design-forward** — Define design direction in the sink first; production pages consume what the sink establishes.
- **Agent-readable** — The design system should be equally consumable by human developers and AI coding agents. Semantic tokens, typed props, and explicit contracts over implicit conventions.
- **Framework-native** — Respect each framework's idioms. Don't impose React conventions on a Hugo project or vice versa.

## Phase 0: Detect Stack

Before anything else, identify the project's framework and lock in the implementation strategy. If you cannot see the file tree, stop and request it.

### Detection Signals

| Signal file / directory | Framework |
|---|---|
| `next.config.*`, `app/` or `pages/` | Next.js (React) |
| `hugo.toml`, `hugo.yaml`, `layouts/partials/` | Hugo |
| `astro.config.*`, `src/components/` | Astro |
| `nuxt.config.*` | Nuxt (Vue) |
| `svelte.config.*` | SvelteKit |
| None of the above | Static HTML/CSS |

### Strategy Table

Once detected, lock in these mappings for the rest of the workflow:

| Concept | React / Next.js | Hugo | Astro | Static HTML |
|---|---|---|---|---|
| **Component** | `.tsx` in `components/` | `.html` partial in `layouts/partials/components/` | `.astro` in `src/components/` | Reusable HTML snippet |
| **Component call** | `<Button variant="primary" />` | `{{ partial "components/button" (dict ...) }}` | `<Button variant="primary" />` | Copy/paste or `include` |
| **Props / params** | React props (TypeScript) | `dict` context | Astro props (TypeScript) | CSS classes / data-attrs |
| **Interactivity** | `useState`, event handlers | Alpine.js `x-data` or `<details>` | `client:load` + framework islands | Vanilla JS or Alpine.js |
| **Sink route** | `app/sink/page.tsx` | `content/sink/_index.md` + `layouts/sink/list.html` | `src/pages/sink.astro` | `sink.html` |
| **Prod guard** | `process.env` check → return `null` | Config overlay or `hugo.Environment` check | `import.meta.env` check | Don't deploy the file |
| **Shortcodes** | N/A (components serve both roles) | `layouts/shortcodes/` wrapping partials | Components usable in MDX | N/A |
| **Content authors** | Components in MDX | Shortcodes in markdown | Components in MDX / `.astro` | N/A |
| **Utility helper** | `cn()` via `clsx` + `tailwind-merge` | `classnames` partial or inline concat | `cn()` or `class:list` | Inline concat |

### Additional Detection Checks

After identifying the framework, also detect:

1. **CSS approach** — Tailwind (which version?), vanilla CSS, CSS modules, Sass, etc.
2. **Icon library** — Lucide, Heroicons, inline SVG, icon fonts, Hugo module, etc.
3. **Interactivity layer** — Alpine.js, HTMX, vanilla JS, React, Vue, Svelte, none.
4. **CMS** — TinaCMS (`tina/`), Decap/Netlify CMS (`static/admin/`), Sanity, Contentful, plain markdown, none.
5. **Existing component patterns** — Where do components live? What naming conventions are in use? Is there an existing helper like `cn()`?

Adapt all subsequent phases to what you detected. Do not impose one framework's conventions on another.

### Tailwind Detection

Detect which Tailwind version is in use, then read the appropriate source:

- **Tailwind v3** — Read `tailwind.config.js` / `tailwind.config.ts` for `theme.extend` (custom colors, spacing, fonts, breakpoints).
- **Tailwind v4** — No config file required. Read `globals.css`, `app.css`, or the project's main CSS entry for `@theme` blocks and CSS custom properties (`--color-*`, `--spacing-*`, `--font-*`). Also check for `@import "tailwindcss"` as a v4 indicator.
- **Detection heuristic:** If `tailwind.config.*` exists → v3. If the CSS entry contains `@theme` or `@import "tailwindcss"` → v4.
- **No Tailwind** — Read the project's main CSS for custom properties, Sass variables, or hardcoded values.

## Phase 0b: Design System Discovery

Before building anything, determine whether the project already has a documented design system or needs one created from scratch. This phase branches into two modes.

### Discovery Manifest

Scan the project root (and common subdirectories like `docs/`, `.github/`, `.cursor/`, `.agent/`) for any of these files:

**Brand & style guides:**
- `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`, `COPILOT.md`
- `.cursorrules`, `.cursor/rules`
- `.github/copilot-instructions.md`
- `brand-guide.md`, `STYLE.md`, `BRAND.md`
- `design-tokens.json`, `tokens.css`, `tokens.json`
- `CONTENT_GUIDELINES.md`, `VOICE.md`, `BRAND_VOICE.md`

**Agent configuration files:**
- `.clinerules`, `.windsurfrules`
- `.agent/skills/*/SKILL.md`
- `README.md` (check for design system or brand sections)

**Hugo-specific:**
- `data/design-tokens.json`, `data/tokens.json`
- `assets/css/` for custom properties

If **any** of these contain design direction (colors, typography, voice, component patterns), enter **Adopt mode**. Otherwise, enter **Establish mode**.

### Adopt Mode — Existing Brand Guide

When the project already has documented design direction:

1. **Ingest** — Read all discovered guide files. Extract:
   - Color palette (named tokens with hex/HSL values)
   - Typography scale (font families, sizes, weights)
   - Spacing system (if documented)
   - Voice & tone adjectives
   - Component patterns already specified
2. **Map** — For every extracted token, identify:
   - The corresponding Tailwind config value, CSS custom property, or Hugo `data/` entry
   - Whether it's a **primitive** token (raw color: `--blue-500`) or **semantic** token (purpose: `--color-interactive`)
3. **Audit** — Scan existing components for drift:
   - Hardcoded hex values instead of tokens
   - Arbitrary Tailwind values (`w-[37px]`) instead of design scale
   - Inconsistent naming conventions
   - Missing dark mode support
4. **Surface gaps** — Report what the guide documents vs. what actually exists in code

### Establish Mode — No Guide Exists

When the project has no documented design system:

1. **Extract** — Scan existing CSS/Tailwind for de-facto tokens:
   - Run through `globals.css`, `tailwind.config.*`, component files (or Hugo's `assets/css/`, Astro's `src/styles/`)
   - Catalog every color, font, and spacing value actually in use
   - Identify the implicit palette and type scale
2. **Propose** — Generate a `design-tokens.md` with:
   - Discovered palette organized as primitive → semantic layers
   - Recommended additions to fill gaps (e.g., missing destructive color, no muted variant)
   - Type scale (H1–H6, body, caption) with sizes and weights
   - Spacing ramp mapped to Tailwind's scale (or CSS custom properties for non-Tailwind projects)
3. **Voice** — Define initial voice & tone:
   - Propose 3–5 voice adjectives based on the project's domain
   - Draft tone map for common UI states
   - Apply the project's franchise placeholder convention (per user rules)
4. **Approve** — Present the proposal to the user. Do NOT proceed to Phase 1 until tokens and voice are approved.

**Automated option:** Run `bash scripts/scan_components.sh [component_dir]` from the skill directory to get a Phase 0 discovery report + EXISTING / MISSING inventory against the tiered checklist.

**Reference:** [design-system-discovery.md](references/design-system-discovery.md)

## Phase 1: Inventory & Plan

Compare existing components against the tiered checklist. Mark each:
- **EXISTING** — import from codebase as-is
- **MISSING** — create the component, then wire it into the sink
- **SHORTCODE/MDX CANDIDATE** — if a component is meant for content authors (not just the sink), also create the content-author-facing wrapper (shortcode for Hugo, MDX export for React/Astro, etc.)

### Tier 1: Core Primitives (mandatory)

- Typography: H1–H6, paragraph, list (ol/ul), inline code, blockquote
- Buttons: primary, secondary, outline, ghost, destructive; sizes sm/md/lg; disabled state
- Badges / Tags: color variants, dismissible
- Avatars: image, initials fallback, sizes, status indicator
- Icons: render a sampler grid from the project's icon library
- Cards: basic, with header/footer, interactive (hover lift)
- Modals / Dialogs: trigger + overlay + close behavior
- Alerts / Toasts: info, success, warning, error variants
- Form controls: text input, textarea, select, checkbox, radio, toggle/switch, with label + error states

### Tier 2: Navigation & Layout (include when app-level complexity exists)

- Tabs: horizontal, with active/disabled states
- Breadcrumbs: with separator and current-page indicator
- Sidebar / Nav: collapsible, with active link
- Dropdown menu: trigger + item list + keyboard nav
- Accordion / Collapsible: expand/collapse with animation
- Tooltip / Popover: hover and click triggers
- Navigation patterns: header, sidebar, mobile menu
- Footer variants

### Tier 3: Content-Author Components (CMS-dependent)

Include when the site has a CMS or content authors who write markdown/MDX:

- Callout / admonition (info, warning, tip, caution)
- Figure / image with caption
- Button / CTA (link styled as button)
- Embed (YouTube, etc.)
- Card grid (n-up layout of cards from content)

For Hugo, each of these should have both a partial (for templates) and a shortcode (for content authors). For React/Astro, the component serves both roles via MDX.

### Tier 4: Data Display (include when data-heavy views exist)

- Table: sortable headers, striped rows, responsive scroll
- Stats / KPI cards: value, label, trend indicator
- Charts: placeholder pattern using the project's chart library (Recharts, Chart.js, etc.)
- Progress bar / Skeleton loaders: determinate and indeterminate states

## Phase 2: Layered Component Architecture

Every component — whether EXISTING or newly created — must follow the **base + variant** pattern. This makes components predictable for both humans and AI agents. The exact mechanism depends on the framework detected in Phase 0.

### React / Next.js — CVA Pattern

Use `class-variance-authority` (CVA) or an equivalent pattern to separate structural base classes from variant-specific classes:

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils"; // clsx + tailwind-merge wrapper

// ── Base + Variants ──────────────────────────────────────────────
const buttonVariants = cva(
  // Base: shared structure (always applied)
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary:     "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary:   "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        outline:     "border border-input bg-transparent hover:bg-accent",
        ghost:       "hover:bg-accent hover:text-accent-foreground",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
      },
    },
    compoundVariants: [
      { variant: "destructive", size: "lg", class: "font-semibold" },
    ],
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

// ── Component ────────────────────────────────────────────────────
interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size }), className)} {...props} />
  );
}
```

### Hugo — Dict Context Pattern

Hugo components use Go template partials with a `dict` context contract:

```go-html-template
{{/* layouts/partials/components/button.html */}}
{{/* 
  Params:
    .label    (string, required) — Button text
    .variant  (string, optional) — "primary"|"secondary"|"outline"|"ghost"|"destructive", default "primary"
    .size     (string, optional) — "sm"|"md"|"lg", default "md"
    .disabled (bool, optional)   — default false
    .href     (string, optional) — If set, renders as <a> instead of <button>
    .class    (string, optional) — Additional CSS classes
*/}}

{{- $variant := .variant | default "primary" -}}
{{- $size := .size | default "md" -}}
{{- $disabled := .disabled | default false -}}

{{- $baseClass := "btn" -}}
{{- $variantClass := printf "btn--%s" $variant -}}
{{- $sizeClass := printf "btn--%s" $size -}}
{{- $disabledClass := cond $disabled "btn--disabled" "" -}}

{{- $classes := delimit (slice $baseClass $variantClass $sizeClass $disabledClass .class) " " -}}

{{ if .href }}
  <a href="{{ .href }}" class="{{ $classes }}">{{ .label }}</a>
{{ else }}
  <button class="{{ $classes }}"{{ if $disabled }} disabled{{ end }}>{{ .label }}</button>
{{ end }}
```

Call it: `{{ partial "components/button" (dict "label" "Submit" "variant" "primary") }}`

### Astro — Props Interface Pattern

Astro components use TypeScript `Props` in frontmatter:

```astro
---
// src/components/Button.astro

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  href?: string;
  class?: string;
}

const {
  variant = 'primary',
  size = 'md',
  disabled = false,
  href,
  class: extraClass,
} = Astro.props;

const classes = [
  'btn',
  `btn--${variant}`,
  `btn--${size}`,
  disabled && 'btn--disabled',
  extraClass,
].filter(Boolean).join(' ');
---

{href ? (
  <a href={href} class:list={[classes]}><slot /></a>
) : (
  <button class:list={[classes]} disabled={disabled}><slot /></button>
)}
```

### Static HTML — BEM + Data-Attribute Pattern

For projects without a framework, use BEM class conventions and document the contract in a comment:

```html
<!--
  Button Component
  Classes: .btn, .btn--primary|secondary|outline|ghost|destructive, .btn--sm|md|lg, .btn--disabled
  Data attrs: none
-->
<button class="btn btn--primary btn--md">Submit</button>
```

### Rules (All Frameworks)

1. **Base layer** — Shared structural classes: layout, border-radius, font-size, focus ring, transitions, disabled state. These NEVER change between variants.
2. **Variant layer** — Only what differs: colors, borders, shadows, backgrounds. Defined as named variants.
3. **Type / param export** — Always export the variant types (React: `VariantProps<>`, Hugo: param comment block, Astro: `Props` interface) so consumers (including AI agents) can discover available variants.
4. **Escape hatch** — Accept an additional class prop and merge it last so consumers can override when necessary.
5. **No raw conditionals** — Never use `isDestructive ? "bg-red-500" : "bg-blue-500"` inline. All visual branching goes through the variant API.

### Semantic Design Tokens

Components should reference **semantic** token names, not primitive color names:

| ❌ Primitive | ✅ Semantic |
|---|---|
| `bg-blue-500` | `bg-primary` |
| `text-gray-500` | `text-muted-foreground` |
| `border-red-500` | `border-destructive` |
| `bg-gray-100` | `bg-muted` |

The semantic layer means dark mode, theme changes, and brand pivots only require updating the token definitions — component code stays unchanged.

### Utility Fallback

If the project lacks a class-merging utility:

- **React** — Add a local `cn()` using `clsx` + `tailwind-merge`, or a minimal version if those aren't in `package.json`.
- **Hugo** — Create a `layouts/partials/helpers/classnames.html` partial:
  ```go-html-template
  {{- $classes := slice -}}
  {{- range . -}}{{- if . -}}{{- $classes = $classes | append . -}}{{- end -}}{{- end -}}
  {{- delimit $classes " " -}}
  ```
- **Astro** — Use `class:list={[...]}` (built-in).
- **Static** — Inline concatenation or a tiny JS helper.

## Phase 3: Voice & Tone

Every design system is incomplete without content guidance. The sink page should include a **Voice & Tone** section that documents how the product communicates.

### Voice Definition

Voice is the brand's consistent personality. Define it with 3–5 adjectives:

```
Voice: [adjective], [adjective], [adjective]
Example: "Confident, approachable, precise"
```

Voice rules:
- Voice NEVER changes. It's the same in error messages, onboarding, and marketing.
- If the project has a `GEMINI.md` or brand guide with personality descriptors, extract them.
- If not, propose adjectives based on the project's domain and audience.

### Tone Map

Tone is the emotional inflection that adapts to context. Map it to user emotional states:

| User State | Tone | Example |
|---|---|---|
| Pleased / celebrating | Enthusiastic | "You're all set! Your changes are live." |
| Neutral / browsing | Informative | "3 items in your cart." |
| Confused / stuck | Supportive | "Let's get you back on track. Try..." |
| Frustrated / error | Empathetic | "Something went wrong. Here's what you can do." |
| First-time / onboarding | Encouraging | "Welcome! Let's set up your workspace." |

### Content Patterns

Document standard copy patterns for recurring UI states:

**Empty states** — Tell the user what goes here and how to populate it:
- ✅ "No projects yet. Create your first one to get started."
- ❌ "No data."

**Error messages** — Answer three questions: What happened? Why? How to fix it:
- ✅ "We couldn't save your changes. The file may have been modified by someone else. Try refreshing and saving again."
- ❌ "Error: 409"

**Success confirmations** — Concise, affirming, with clear next step:
- ✅ "Profile updated. Changes will appear within a few minutes."
- ❌ "Success!"

**Loading states** — Set expectations:
- ✅ "Loading your dashboard..." or a skeleton with shimmer
- ❌ Empty space with a spinner and no context

**Destructive actions** — Confirm with specifics:
- ✅ "Delete 'Project Alpha'? This action cannot be undone."
- ❌ "Are you sure?"

### Franchise Placeholders

Per project convention, pick a pop-culture franchise for placeholder content (form labels, sample data, empty states, example names). Document the chosen franchise in the sink page header and use it consistently:

- Form input placeholder: "Entered by Gandalf the Grey"
- Sample table row: "Frodo Baggins | Shire | Ring Bearer"
- Empty state: "The Shire is quiet. No hobbits have signed up yet."

**Reference:** [voice-and-tone.md](references/voice-and-tone.md)

## Phase 3b: Image & Illustration

Photography sourced from the web cannot be used directly — copyright, licensing, and brand inconsistency all prevent it. Every kitchen sink / brand guide must define an **illustration style** and a **reinterpretation pipeline** so found reference photos can be transformed into brand-safe illustrated assets.

### Defining the Illustration Style

During discovery (Phase 0b), extract or establish the illustration language:

| Dimension | Example Values |
|---|---|
| **Rendering** | flat vector, line art, watercolor wash, paper-cut, low-poly 3D, ink sketch |
| **Palette** | brand palette only, monochrome + accent, analogous warm, full-spectrum muted |
| **Detail level** | minimal / iconic, moderate / editorial, high / realistic |
| **Stroke** | none (filled shapes), uniform weight, hand-drawn taper, thick outline |
| **Texture** | clean / digital, grain / risograph, paper / organic |
| **Mood keywords** | 3–5 adjectives that align with Voice (Phase 3), e.g. "warm, approachable, confident" |

Document these in the brand guide and render **3–5 sample illustrations** on the sink page as the canonical references.

### Reinterpretation Workflow

When the agent or designer finds a reference photo:

1. **Describe the subject** — Write a concise description of what's depicted (pose, setting, objects, mood), stripping photographer-specific style.
2. **Apply the brand filter** — Compose a generation prompt combining the subject description with the project's illustration style tokens (rendering, palette, detail, stroke, texture, mood).
3. **Generate** — Use AI image generation (`generate_image` tool or equivalent) with the composed prompt. The prompt must explicitly reference the brand's illustration style, not the original photo.
4. **Validate** — Check the output against the sink page's illustration samples for style consistency. Regenerate if drift is detected.
5. **Optimize** — Export at appropriate sizes/formats (WebP for web, SVG if vector-compatible), add `alt` text following content design guidelines.

### Prompt Template

```
[Subject description]. Rendered in [rendering style] with [palette description].
[Detail level] detail, [stroke style] strokes, [texture] finish.
The mood is [mood keywords]. No photographic elements.
```

**Example:**
```
A barber trimming a customer's beard in a classic barbershop chair.
Rendered in flat vector style with a warm palette of cream, rust,
and charcoal. Moderate detail, thick outline strokes, subtle grain
texture. The mood is confident, nostalgic, and welcoming.
No photographic elements.
```

### Sink Page Section

The kitchen sink MUST include an **Illustration Gallery** section:

- 3–5 canonical illustrations showing the brand's visual language
- Side-by-side comparison: photo reference → illustrated output (demonstrating the reinterpretation)
- A rendered prompt template pre-filled with the project's style tokens
- Light/dark mode rendering of each illustration

### Content Rules

- **Never use unmodified photos** — every image must pass through the reinterpretation pipeline
- **Publish the prompt** — store the generation prompt alongside the asset for reproducibility
- **Style drift detection** — if a new illustration doesn't visually match the sink samples, adjust the prompt or flag for review
- **Alt text** — every illustration gets descriptive alt text per content design guidelines (Phase 3)

**Reference:** [image-reinterpretation.md](references/image-reinterpretation.md)

## Phase 4: Motion & Interaction

Animation is the body language of the product. Document motion patterns in the sink to ensure consistent, purposeful animation across the project.

### Motion Principles

1. **Purposeful** — Every animation communicates something (entrance, exit, state change, feedback). No animation for decoration alone.
2. **Informative** — Motion guides attention to what changed and where to look next.
3. **Consistent** — Same type of change = same animation. A modal always enters the same way.
4. **Respectful** — Always honor `prefers-reduced-motion`. Provide fallback behavior.

### Duration Scale

Define named durations mapped to the project's motion needs:

| Token | Duration | Use Case |
|---|---|---|
| `--duration-instant` | 100ms | Micro-interactions: toggles, color changes, hover effects |
| `--duration-fast` | 200ms | Small reveals: tooltips, dropdowns, badges |
| `--duration-normal` | 300ms | Standard transitions: modals, panels, page elements |
| `--duration-slow` | 500ms | Large reveals: full-page transitions, complex orchestration |

### Easing Curves

| Token | Curve | Use Case |
|---|---|---|
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Entrances — element arriving on screen |
| `--ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Exits — element leaving screen |
| `--ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | State changes — element transforming in place |

### Common Patterns

Document these in the sink's **Motion Sampler** section:

- **Hover lift** — `translateY(-2px)` + shadow increase, `--duration-instant`, `--ease-out`
- **Fade in** — opacity 0→1, `--duration-fast`, `--ease-out`
- **Slide in** — translateY(8px→0) + opacity 0→1, `--duration-normal`, `--ease-out`
- **Expand/collapse** — height 0→auto with overflow hidden, `--duration-normal`, `--ease-in-out`
- **Skeleton shimmer** — gradient sweep animation, `--duration-slow`, linear, infinite
- **Modal entrance** — scale(0.95→1) + opacity 0→1, `--duration-normal`, `--ease-out`
- **Modal exit** — scale(1→0.95) + opacity 1→0, `--duration-fast`, `--ease-in`

### Reduced Motion

Wrap all animations in a `prefers-reduced-motion` check:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

For Tailwind, use `motion-safe:` and `motion-reduce:` modifiers.

**Reference:** [motion-guidelines.md](references/motion-guidelines.md)

## Phase 5: Build Components

For every **MISSING** item from Phase 1, create the component using the framework's native patterns.

### File Location & Naming

| Framework | Location | Convention |
|---|---|---|
| React / Next.js | `components/` or `components/ui/` | `Button.tsx`, `card.tsx` — match existing project convention |
| Hugo | `layouts/partials/components/` | `button.html`, `card.html` |
| Astro | `src/components/` | `Button.astro`, `Card.astro` |
| Static HTML | `components/` or `includes/` | `button.html`, `card.html` |

### Component Creation Standard (All Frameworks)

1. **Create the component** in the project's established component location with a stable export/interface.
2. **Document the interface** at the top of the file:
   - React: TypeScript interface or JSDoc props comment.
   - Hugo: Go template comment block listing expected `dict` keys, their types, and defaults.
   - Astro: TypeScript `Props` interface in frontmatter.
   - Static: Comment block describing expected classes/data attributes.
3. **Use design tokens** from the project's Tailwind config, CSS custom properties, or Hugo `data/` entries; avoid arbitrary/magic values.
4. **Keep components self-contained** — rely only on dependencies already in the project.
5. **Make interactive components actually interactive** using whatever the project's interactivity layer is:
   - React: `useState`, event handlers
   - Hugo: Alpine.js `x-data` or `<details>/<summary>` for zero-JS
   - Astro: `client:load` + framework islands
   - Static: vanilla JS, Alpine.js, or `<details>/<summary>`
6. **Apply the variant pattern** from Phase 2 (CVA for React, dict params for Hugo, Props for Astro).
7. **Apply voice & tone** patterns from Phase 3. Error messages answer what/why/fix. Empty states guide the user.
8. **Apply motion** patterns from Phase 4. Use the defined duration and easing tokens.
9. Wire the component into the sink page immediately. No placeholders.

### Content-Author Wrappers

When a component is marked as a **SHORTCODE/MDX CANDIDATE** in Phase 1:

- **Hugo** — Create a shortcode in `layouts/shortcodes/` that wraps the partial. Pass through all relevant parameters.
- **React / Astro** — The component itself is usable in MDX. Ensure it's exported from the project's MDX component registry.
- **Static** — Document usage instructions for copy/paste inclusion.

## Phase 6: Assemble Sink Page

Create the sink route file based on the framework detected in Phase 0.

### Sink Route Creation

**React / Next.js** — `app/sink/page.tsx`
- Add `"use client"` directive.
- Return `null` when `process.env.NEXT_PUBLIC_VERCEL_ENV === "production"`.
- Use `examples/minimal-sink.tsx` as a starter template.

**Hugo** — `content/sink/_index.md` + `layouts/sink/list.html`
- Frontmatter: `type: sink`, exclude from sitemap (`sitemap: exclude`), hide from nav.
- Layout: check `hugo.Environment` or `site.Params.showSink`; redirect in production.
- Preferred production guard: config overlay at `config/production/hugo.toml` with `showSink = false`.
- Use `examples/minimal-sink.html` as a starter template.

**Astro** — `src/pages/sink.astro`
- Check `import.meta.env.PROD` and return redirect or empty page.

**SvelteKit** — `src/routes/sink/+page.svelte`
- Use `$app/environment` to check for production.

**Nuxt** — `pages/sink.vue`
- Use `useRuntimeConfig()` to check environment.

**Static HTML** — `sink.html`
- Simply don't include in production deployment.

### Architecture Rules

- Never import other page/route files — only import components or define helpers locally.
- The sink page is a dev tool — exclude it from production, sitemap, RSS, search indexes, and navigation.

### Sink Page Layout

The sink page follows the same section structure regardless of framework. Adapt the syntax to match.

**Sections (in order):**

1. **Header** — Title, description, last-updated timestamp, franchise declaration
2. **Design Tokens** — Color palette (primitive → semantic), typography scale, spacing ramp
3. **Voice & Tone** — Voice definition, tone map, content pattern examples
4. **Illustration Gallery** — Canonical illustrations, reinterpretation examples, prompt template
5. **Site Header** — Rendered inline to test responsive breakpoints and nav states
6. **Site Footer** — Rendered inline to test link columns and brand consistency
7. **Typography** — H1–H6, body, caption, lists, blockquote, inline code
8. **Buttons** — All variants × sizes × states (variant grid)
9. **Badges** — Color variants, dismissible
10. **Cards** — Basic, with header/footer, interactive
11. **Form Controls** — All input types with label + error states
12. **Modals & Dialogs** — Working open/close demo
13. **Alerts** — All severity variants
14. **Motion Sampler** — Interactive demos of hover lift, fade, slide, expand/collapse
15. **Content-Author Specimens** — How shortcodes/MDX components render (if applicable)
16. **Tier 2 components** — Tabs, breadcrumbs, accordion, tooltip, dropdown (if applicable)
17. **Tier 4 components** — Table, stats cards, progress, skeleton (if applicable)
18. **Chaos Laboratory** — Token visualization, state matrix, dark/light side-by-side

### Chaos Laboratory

1. **Token visualization** — Programmatically render design tokens (colors, spacing).
   - React: Import resolved config via `resolveConfig`.
   - Hugo: Export tokens to `data/design-tokens.json` at build time, read with `site.Data`.
   - Astro: Import config in frontmatter.
   - Static: Maintain a JSON file manually or generate with a script.
2. **State matrix** — Render variants side by side (default, hover, focus, disabled, active).
3. **Theme test** — Light and dark columns, forced via wrapper class.
4. **Responsive stubs** — `iframe` containers with fixed widths (320px, 768px) to verify mobile layouts.

## Phase 7: Verify

Run these checks before considering the sink complete. Commands vary by framework.

### Automated Checks

| Framework | Build | Lint |
|---|---|---|
| Next.js | `pnpm build` | `pnpm lint` |
| Hugo | `hugo --minify` | `hugo --templateMetrics` (check for template errors) |
| Astro | `pnpm build` | `pnpm lint` |
| SvelteKit | `pnpm build` | `pnpm lint` |
| Nuxt | `pnpm build` | `pnpm lint` |
| Static | N/A | HTML validator |

Optional accessibility audit: `pnpm dlx @axe-core/cli http://localhost:<port>/sink`

### Manual Checklist

- [ ] **A. Completeness** — Every Tier 1 item is present. Tier 2/3/4 items included where relevant.
- [ ] **B. Real components** — Every rendered element is imported from the project's component location (no inline-only markup pretending to be a component).
- [ ] **C. Layered architecture** — Every component uses the framework-appropriate variant pattern (CVA for React, dict params for Hugo, Props for Astro, BEM for static).
- [ ] **D. Semantic tokens** — No hardcoded hex values or primitive color names in component code.
- [ ] **E. Interactivity** — Modals open, toggles toggle, tabs switch, dropdowns expand. Every stateful component works.
- [ ] **F. Voice & tone** — Content patterns documented. Error messages answer what/why/fix. Empty states guide the user.
- [ ] **G. Motion** — Animations use defined duration/easing tokens. `prefers-reduced-motion` respected.
- [ ] **H. Theming** — Dark/light columns render correctly. No hard-coded colors bypassing tokens.
- [ ] **I. Production guard** — Sink page is excluded from production via the framework's native mechanism.
- [ ] **J. No import cycles** — Sink page does not import any page/route file.
- [ ] **K. Content-author wrappers** — Shortcodes/MDX exports pass through all relevant parameters (if applicable).

## CMS Notes

The sink page is **never** CMS-managed — it's a developer tool.

However, when a CMS is present, content-author-facing components (Tier 3) should respect the CMS content model:

- **TinaCMS** — Component params should align with the fields defined in `tina/config.ts` collections. Note: TinaCMS visual editing requires React — in Hugo projects, Tina functions only as a markdown/frontmatter editor GUI.
- **Decap CMS** — Component params should map to widget types in `static/admin/config.yml`.
- **MDX-based CMS** (Contentful, Sanity, etc.) — Exported components should match the expected props shape from the CMS schema.

## AI Agent Readiness

These practices ensure the design system is optimally consumable by AI coding agents (Cursor, Copilot, Claude, Gemini, etc.):

1. **Semantic tokens over primitives** — `--color-interactive` communicates intent; `--blue-500` does not. AI agents make better decisions when tokens encode purpose.
2. **Machine-readable format** — Store tokens in CSS custom properties AND/OR JSON. Both humans and agents can parse them.
3. **Typed props are the API** — Every component's type interface (React `VariantProps<>`, Hugo dict contract, Astro `Props`) is effectively its API contract. AI agents use this to generate correct usage.
4. **Purpose-based naming** — Name tokens for what they DO, not what they LOOK LIKE:
   - ✅ `color-button-background-brand`, `text-muted-foreground`
   - ❌ `blue-dark`, `gray-light`
5. **Rules file** — If the project has a `.cursorrules`, `.github/copilot-instructions.md`, `GEMINI.md`, or `CLAUDE.md`, ensure the design system tokens and component conventions are referenced there. AI agents read these files first.
6. **Single source of truth** — The sink page IS the reference. If an AI agent needs to understand the design system, point it at the sink page and the token definitions.

## Companion Skills

This skill works well in conjunction with other design-oriented skills. When available, leverage them:

- **design-lookup** — Use to search for CSS components, SVG icons, and design patterns from the web. Helpful during Establish mode when you need inspiration for component styling or when looking for specific SVG assets (spinners, dividers, icons) to include in the sink.
- **Frontend / web design guidelines skills** — If the project or user has a separate skill for frontend design standards, web design guidelines, or brand identity (e.g., a project-specific visual identity skill), read it during Phase 0b discovery. Its rules and constraints should feed into the token system and voice definition.
- **deep-research** — Use for comprehensive research when establishing a new design system from scratch and the user wants to evaluate design system approaches, compare component libraries, or survey competitor aesthetics.

When multiple skills apply, the kitchen sink skill acts as the **integrator** — it consumes the outputs of companion skills (design references, brand identity, research findings) and codifies them into the component library and sink page.

## Anti-patterns

- **Draft placeholders** — `{/* TODO: add button */}` is never acceptable. Build the real component.
- **Arbitrary Tailwind values** — `w-[35px]` or `text-[#ff0000]` instead of using config tokens.
- **Raw conditional classes** — `isDestructive ? "bg-red-500" : "bg-blue-500"` instead of using variants.
- **Importing page files** — `import X from "../other-page/page"` creates coupling and build issues.
- **Skipping tiers** — Don't jump to Tier 4 charts before Tier 1 buttons exist.
- **Static mockups** — A modal that doesn't open, a toggle that doesn't toggle, a tab bar that doesn't switch.
- **One-off inline components** — If it's rendered in the sink, it belongs in the component directory as an importable module.
- **Appearance-based token names** — `blue-primary` instead of `color-interactive`. Semantic names survive brand pivots.
- **Missing voice guidance** — A sink without content patterns is only half a design system.
- **Decorative animation** — Motion without purpose. Every animation should inform or guide.
- **Framework mismatch** — Imposing React idioms (JSX, hooks) on a Hugo or static HTML project.

## Reference

For detailed per-component specs (expected props, variants, states, accessibility), the sink page section template, and concrete code examples:

- **Components:** [component-catalog.md](references/component-catalog.md)
- **Discovery:** [design-system-discovery.md](references/design-system-discovery.md)
- **Voice & Tone:** [voice-and-tone.md](references/voice-and-tone.md)
- **Image & Illustration:** [image-reinterpretation.md](references/image-reinterpretation.md)
- **Motion:** [motion-guidelines.md](references/motion-guidelines.md)
