# Component Catalog Reference

Detailed specs for every component in the Kitchen Sink tiered checklist. Use this as the build reference when creating MISSING components and assembling sink sections.

Every component MUST follow the **base + variant architecture** (see CVA Pattern below). Each spec now includes:
- **Props** — typed interface for the component
- **CVA structure** — base classes + variant definitions
- **Content guidance** — voice/tone patterns for labels, errors, and states
- **Motion** — animation tokens and patterns for interactive states

---

## CVA Pattern — Universal Template

Every component uses this structure. The tool is `class-variance-authority` (CVA):

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils"; // clsx + tailwind-merge

const componentVariants = cva(
  // Base: always-applied structural classes
  "base-classes here",
  {
    variants: {
      variant: {
        default: "variant-classes",
        // ...more named variants
      },
      size: {
        sm: "size-classes",
        md: "size-classes",
        lg: "size-classes",
      },
    },
    compoundVariants: [
      // Conditional: when variant X + size Y, add extra classes
    ],
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

// Always export VariantProps for type-safe consumption
interface ComponentProps
  extends React.HTMLAttributes<HTMLElement>,
    VariantProps<typeof componentVariants> {}

export function Component({ className, variant, size, ...props }: ComponentProps) {
  return <div className={cn(componentVariants({ variant, size }), className)} {...props} />;
}
```

**Key rules:**
- Base = layout, typography, transitions, focus ring, disabled state
- Variant = colors, borders, shadows — only what changes
- Always accept `className` and merge with `cn()` as escape hatch
- Export `VariantProps<typeof componentVariants>` for AI and IDE consumption

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
| `variant` | `"primary" \| "secondary" \| "outline" \| "ghost" \| "destructive" \| "link"` | Visual style |
| `size` | `"sm" \| "md" \| "lg"` | Padding and font-size scale |
| `disabled` | `boolean` | Reduced opacity, `pointer-events-none`, `aria-disabled` |
| `loading` | `boolean` (optional) | Swap children for spinner, disable click |
| `asChild` | `boolean` (optional) | Render as child element (Radix pattern) |

States to render: default, hover, focus-visible ring, active/pressed, disabled, loading.

**Content guidance:**
- Labels are verbs or short verb phrases: "Save", "Create Project", "Send Invitation"
- Destructive buttons name the action: "Delete Project", not "Delete" or "OK"
- Loading state: swap label for spinner but keep button width stable

**Motion:** `transition-colors duration-100 ease-out` on hover. No transform on standard buttons — reserve hover lift for cards.

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

**Content guidance:**
- Destructive confirmation modals name exactly what will be destroyed: "Delete 'Project Alpha'? This removes all 12 pages and cannot be undone."
- Action buttons use specific verbs: "Delete Project" / "Cancel", not "OK" / "Cancel"

**Motion:**
- Overlay: `opacity 0→1`, `duration-fast`, `ease-out`
- Content: `scale(0.95→1) + opacity 0→1`, `duration-normal`, `ease-out`
- Exit: reverse with `ease-in` and `duration-fast`

### Alert

| Prop | Type | Notes |
|------|------|-------|
| `variant` | `"info" \| "success" \| "warning" \| "error"` | Icon + color scheme |
| `title` | `string` (optional) | Bold heading line |
| `children` | `ReactNode` | Message body |
| `dismissible` | `boolean` | Show close button |

**Content guidance:**
- Error alerts answer: What happened? Why? How to fix it.
- Success alerts are concise + hint at next step: "Saved. Changes appear in a few minutes."
- Warning alerts are actionable: "Approaching storage limit. Free up space or upgrade."

**Motion:** Slide-in from top or fade-in, `duration-fast`, `ease-out`. Dismissal fades out, `duration-fast`, `ease-in`.

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

**Content guidance:**
- Labels are nouns/noun phrases: "Email address", not "Enter your email"
- Placeholders show format/example: `gandalf@shire.com`, not "Type email here"
- Error messages below the field, in error color, answering what's wrong and how to fix it
- Use franchise-appropriate placeholder names per project convention

**Motion:** Toggle/Switch uses `duration-instant`, `ease-in-out` for track color and thumb position transitions.

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

**Motion:** Use CSS grid `grid-template-rows: 0fr → 1fr` trick for smooth height animation, `duration-normal`, `ease-in-out`. Chevron icon rotates 180° in sync.

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

## Accessibility Baseline

Every component in the sink should meet these minimums:

- **Color contrast** — 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- **Focus indicators** — Visible `focus-visible` ring on all interactive elements
- **Keyboard navigation** — All interactive components operable via keyboard alone
- **ARIA attributes** — Correct roles, labels, and states (see per-component notes above)
- **Motion** — Respect `prefers-reduced-motion`. Use `motion-safe:` / `motion-reduce:` Tailwind modifiers
- **Error identification** — Form errors identified by `aria-invalid`, `aria-describedby` pointing to error text
- **Labels** — Every input has an associated `<label>` with `htmlFor`; never rely on placeholder alone
- **Semantic HTML** — Use correct elements: `<button>` for actions, `<a>` for navigation, `<nav>` for nav regions
- **Screen reader text** — Use `sr-only` class for content visible only to assistive technology when visual context is insufficient
