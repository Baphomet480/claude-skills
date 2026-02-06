# Component Catalog Reference

Detailed specs for every component in the Kitchen Sink tiered checklist. Use this as the build reference when creating MISSING components and assembling sink sections.

---

## Tier 1: Core Primitives

### Typography

Render the project's type scale. Each heading level, paragraph text, lists, and inline elements.

| Element | Props / Variants | Accessibility |
|---------|-----------------|---------------|
| H1–H6 | Default weight and size per level | Use semantic heading hierarchy (no skipping levels) |
| Paragraph | `text-sm`, `text-base`, `text-lg` sizes | Sufficient color contrast (4.5:1 minimum) |
| Ordered / Unordered list | Nested up to 3 levels | Use native `<ol>` / `<ul>` elements |
| Inline code | Monospace background highlight | Distinguish visually from surrounding text |
| Blockquote | Left border accent, italic or muted style | Use `<blockquote>` element |

### Button

| Prop | Type | Notes |
|------|------|-------|
| `variant` | `"primary" \| "secondary" \| "outline" \| "ghost" \| "destructive"` | Visual style |
| `size` | `"sm" \| "md" \| "lg"` | Padding and font-size scale |
| `disabled` | `boolean` | Reduced opacity, `pointer-events-none`, `aria-disabled` |
| `loading` | `boolean` (optional) | Swap children for spinner, disable click |
| `asChild` | `boolean` (optional) | Render as child element (Radix pattern) |

States to render: default, hover, focus-visible ring, active/pressed, disabled, loading.

### Badge / Tag

| Prop | Type | Notes |
|------|------|-------|
| `variant` | `"default" \| "success" \| "warning" \| "error" \| "info"` | Semantic color |
| `dismissible` | `boolean` | Show × button, call `onDismiss` |
| `size` | `"sm" \| "md"` | Compact or standard |

### Avatar

| Prop | Type | Notes |
|------|------|-------|
| `src` | `string \| undefined` | Image URL; show initials fallback when missing |
| `alt` | `string` | Required for accessibility |
| `initials` | `string` | 1–2 character fallback |
| `size` | `"sm" \| "md" \| "lg"` | Width/height scale |
| `status` | `"online" \| "offline" \| "away"` (optional) | Colored dot indicator |

### Icon Sampler

Not a component to create — instead, render a grid of 20–30 icons from the project's icon library with their names underneath. Demonstrates icon availability and sizing.

### Card

| Prop | Type | Notes |
|------|------|-------|
| `children` | `ReactNode` | Card body content |
| `header` | `ReactNode` (optional) | Top section with border-bottom |
| `footer` | `ReactNode` (optional) | Bottom section with border-top |
| `interactive` | `boolean` (optional) | Add hover:shadow-lg, cursor-pointer, transition |
| `padding` | `"none" \| "sm" \| "md" \| "lg"` | Control inner spacing |

### Modal / Dialog

| Prop | Type | Notes |
|------|------|-------|
| `open` | `boolean` | Controlled visibility |
| `onClose` | `() => void` | Callback to close |
| `title` | `string` | Rendered in header |
| `children` | `ReactNode` | Body content |

Behavior: overlay click closes, Escape key closes, focus trapped inside, `aria-modal="true"`, `role="dialog"`.

### Alert

| Prop | Type | Notes |
|------|------|-------|
| `variant` | `"info" \| "success" \| "warning" \| "error"` | Icon + color scheme |
| `title` | `string` (optional) | Bold heading line |
| `children` | `ReactNode` | Message body |
| `dismissible` | `boolean` | Show close button |

### Form Controls

Each form control should accept `label`, `error` (error message string), `disabled`, and standard HTML attributes.

| Control | Key Props | Notes |
|---------|-----------|-------|
| TextInput | `type`, `placeholder`, `value`, `onChange` | Support `"text"`, `"email"`, `"password"` |
| Textarea | `rows`, `resize` | Default 3–4 rows |
| Select | `options: {label, value}[]`, `placeholder` | Native or custom dropdown |
| Checkbox | `checked`, `onChange`, `label` | Visible checkmark, `role="checkbox"` |
| Radio | `options: {label, value}[]`, `name`, `selected` | Radio group with `fieldset` |
| Toggle / Switch | `checked`, `onChange`, `label` | Animated track and thumb, `role="switch"` |

---

## Tier 2: Navigation & Layout

### Tabs

| Prop | Type | Notes |
|------|------|-------|
| `tabs` | `{label: string, content: ReactNode, disabled?: boolean}[]` | Tab definitions |
| `defaultIndex` | `number` | Initially active tab |

Behavior: keyboard arrow navigation between tabs, `role="tablist"` / `role="tab"` / `role="tabpanel"`.

### Breadcrumbs

| Prop | Type | Notes |
|------|------|-------|
| `items` | `{label: string, href?: string}[]` | Last item has no href (current page) |
| `separator` | `ReactNode` | Default `/` or `>` |

Render inside `<nav aria-label="Breadcrumb">`.

### Dropdown Menu

| Prop | Type | Notes |
|------|------|-------|
| `trigger` | `ReactNode` | Button or element that opens menu |
| `items` | `{label: string, onClick: () => void, icon?: ReactNode, disabled?: boolean}[]` | Menu entries |

Behavior: click to open, Escape to close, arrow keys to navigate items, focus management.

### Accordion / Collapsible

| Prop | Type | Notes |
|------|------|-------|
| `items` | `{title: string, content: ReactNode}[]` | Expandable sections |
| `multiple` | `boolean` | Allow multiple open at once |

Animate height transition. Use `aria-expanded`.

### Tooltip / Popover

| Prop | Type | Notes |
|------|------|-------|
| `content` | `ReactNode` | Tooltip/popover body |
| `trigger` | `"hover" \| "click"` | Activation mode |
| `side` | `"top" \| "right" \| "bottom" \| "left"` | Preferred placement |

Tooltip: brief text, appears on hover, `role="tooltip"`. Popover: richer content, click to toggle.

---

## Tier 3: Data Display

### Table

| Prop | Type | Notes |
|------|------|-------|
| `columns` | `{key: string, label: string, sortable?: boolean}[]` | Column definitions |
| `data` | `Record<string, any>[]` | Row data |
| `striped` | `boolean` | Alternating row backgrounds |

Wrap in a horizontally scrollable container for mobile. Use `<table>`, `<thead>`, `<tbody>` semantics.

### Stats / KPI Card

| Prop | Type | Notes |
|------|------|-------|
| `label` | `string` | Metric name |
| `value` | `string \| number` | Current value |
| `trend` | `"up" \| "down" \| "flat"` (optional) | Arrow icon + color |
| `change` | `string` (optional) | e.g., "+12.5%" |

### Progress Bar

| Prop | Type | Notes |
|------|------|-------|
| `value` | `number` | 0–100 percentage |
| `variant` | `"default" \| "success" \| "warning" \| "error"` | Color |
| `indeterminate` | `boolean` | Animated shimmer when true |

Use `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`.

### Skeleton Loader

| Prop | Type | Notes |
|------|------|-------|
| `width` | `string` | Tailwind width class |
| `height` | `string` | Tailwind height class |
| `rounded` | `boolean` | Circle vs rectangle |

Pulsing animation via `animate-pulse`.

---

## Sink Page Architecture

### Route file skeleton

```tsx
"use client";

import { useState } from "react";
// Component imports...

const SECTIONS = [
  { id: "typography", label: "Typography" },
  { id: "buttons", label: "Buttons" },
  { id: "badges", label: "Badges" },
  // ... one entry per section
] as const;

export default function SinkPage() {
  if (process.env.NEXT_PUBLIC_VERCEL_ENV === "production") return null;

  return (
    <div className="flex min-h-screen">
      {/* Sidebar navigation */}
      <nav className="sticky top-0 hidden h-screen w-56 shrink-0 overflow-y-auto border-r p-4 lg:block">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Components
        </h2>
        <ul className="space-y-1">
          {SECTIONS.map((s) => (
            <li key={s.id}>
              <a
                href={`#${s.id}`}
                className="block rounded px-2 py-1 text-sm hover:bg-accent"
              >
                {s.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Main content */}
      <main className="flex-1 space-y-16 p-8 lg:p-12">
        <header>
          <h1 className="text-4xl font-bold">Kitchen Sink</h1>
          <p className="mt-2 text-muted-foreground">
            Component inventory and design system reference.
          </p>
        </header>

        {/* Sections go here */}
      </main>
    </div>
  );
}
```

### Section template

Each component section follows this structure:

```tsx
{/* ── Buttons ── */}
<section id="buttons" className="space-y-6">
  <h2 className="text-2xl font-semibold border-b pb-2">Buttons</h2>

  {/* Variant grid */}
  <div>
    <h3 className="text-sm font-medium text-muted-foreground mb-3">Variants</h3>
    <div className="flex flex-wrap items-center gap-3">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  </div>

  {/* Size scale */}
  <div>
    <h3 className="text-sm font-medium text-muted-foreground mb-3">Sizes</h3>
    <div className="flex flex-wrap items-end gap-3">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  </div>

  {/* States */}
  <div>
    <h3 className="text-sm font-medium text-muted-foreground mb-3">States</h3>
    <div className="flex flex-wrap items-center gap-3">
      <Button>Default</Button>
      <Button disabled>Disabled</Button>
      <Button loading>Loading</Button>
    </div>
  </div>
</section>
```

---

## Chaos Laboratory Patterns

### Tailwind Token Visualization

Programmatically render the project's color palette by reading from the Tailwind config or CSS custom properties:

```tsx
{/* ── Color Palette ── */}
<section id="colors" className="space-y-6">
  <h2 className="text-2xl font-semibold border-b pb-2">Color Palette</h2>
  <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
    {Object.entries(colors).map(([name, value]) => (
      <div key={name} className="space-y-1.5">
        <div
          className="h-16 rounded-lg border shadow-sm"
          style={{ backgroundColor: value }}
        />
        <p className="text-xs font-medium">{name}</p>
        <p className="text-xs text-muted-foreground">{value}</p>
      </div>
    ))}
  </div>
</section>
```

For Tailwind v4 / CSS variable-based themes, enumerate the CSS custom properties instead:

```tsx
const THEME_COLORS = [
  { name: "background", var: "var(--background)" },
  { name: "foreground", var: "var(--foreground)" },
  { name: "primary", var: "var(--primary)" },
  { name: "secondary", var: "var(--secondary)" },
  { name: "accent", var: "var(--accent)" },
  { name: "destructive", var: "var(--destructive)" },
  { name: "muted", var: "var(--muted)" },
  // ...extend to match the project's theme
];
```

### Spacing Scale

```tsx
<section id="spacing" className="space-y-6">
  <h2 className="text-2xl font-semibold border-b pb-2">Spacing Scale</h2>
  <div className="space-y-2">
    {[1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24].map((n) => (
      <div key={n} className="flex items-center gap-4">
        <span className="w-12 text-right text-xs text-muted-foreground">
          {n}
        </span>
        <div
          className={`h-4 rounded bg-primary`}
          style={{ width: `${n * 4}px` }}
        />
        <span className="text-xs text-muted-foreground">{n * 4}px</span>
      </div>
    ))}
  </div>
</section>
```

### Dark / Light Mode Side-by-Side

Render the same components inside forced light and dark wrappers:

```tsx
<section id="theme-test" className="space-y-6">
  <h2 className="text-2xl font-semibold border-b pb-2">Theme Test</h2>
  <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
    {/* Light column */}
    <div className="rounded-xl border bg-background p-6" data-theme="light">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider">
        Light Mode
      </h3>
      <ThemeTestContent />
    </div>

    {/* Dark column */}
    <div className="dark rounded-xl border bg-background p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider">
        Dark Mode
      </h3>
      <ThemeTestContent />
    </div>
  </div>
</section>
```

Where `ThemeTestContent` is a local component rendering a representative sample: a card with text, a button row, an alert, and a form input. This verifies that all theme tokens resolve correctly in both modes.

---

## Accessibility Baseline

Every component in the sink should meet these minimums:

- **Color contrast** — 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- **Focus indicators** — Visible `focus-visible` ring on all interactive elements
- **Keyboard navigation** — All interactive components operable via keyboard alone
- **ARIA attributes** — Correct roles, labels, and states (see per-component notes above)
- **Motion** — Respect `prefers-reduced-motion` for animations
