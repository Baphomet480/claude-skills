# Motion Guidelines Reference

Animation and interaction pattern documentation for the Kitchen Sink design system. Motion is the body language of the product — it communicates state changes, guides attention, and reinforces brand personality.

---

## Principles

1. **Purposeful** — Every animation communicates something: an entrance, exit, state change, or feedback signal. No decorative animation.
2. **Informative** — Motion guides the user's eye to what changed and where to look next.
3. **Consistent** — The same type of change always uses the same animation. A modal always enters the same way everywhere.
4. **Respectful** — Always honor `prefers-reduced-motion`. Users who need reduced motion get instant state changes with no compromise in functionality.

---

## Duration Scale

Named duration tokens mapped to use cases. Store these as CSS custom properties or Tailwind config values.

| Token Name | Value | Use Case | Tailwind Config |
|---|---|---|---|
| `--duration-instant` | `100ms` | Micro-interactions: hover effects, color changes, toggle states | `transitionDuration: { instant: '100ms' }` |
| `--duration-fast` | `200ms` | Small reveals: tooltips, dropdown menus, badge appearances | `transitionDuration: { fast: '200ms' }` |
| `--duration-normal` | `300ms` | Standard transitions: modals, panels, slide-ins, accordion expand | `transitionDuration: { normal: '300ms' }` |
| `--duration-slow` | `500ms` | Large orchestrations: page transitions, complex multi-element sequences | `transitionDuration: { slow: '500ms' }` |

### CSS Custom Properties

```css
:root {
  --duration-instant: 100ms;
  --duration-fast: 200ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
}
```

---

## Easing Curves

| Token Name | Value | Use Case |
|---|---|---|
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | **Entrances** — element arriving on screen. Starts fast, decelerates to rest. |
| `--ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | **Exits** — element leaving screen. Starts slow, accelerates away. |
| `--ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | **State changes** — element transforming in place (color, size, position). |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | **Playful emphasis** — slight overshoot for attention. Use sparingly. |

### CSS Custom Properties

```css
:root {
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## Common Patterns

### Hover Lift

Card or button lifts slightly on hover to indicate interactivity.

```css
.hover-lift {
  transition: transform var(--duration-instant) var(--ease-out),
              box-shadow var(--duration-instant) var(--ease-out);
}
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
}
```

Tailwind equivalent:
```
transition-all duration-100 ease-out hover:-translate-y-0.5 hover:shadow-lg
```

### Fade In

Element appears by fading from transparent to opaque.

```css
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.fade-in {
  animation: fade-in var(--duration-fast) var(--ease-out);
}
```

### Slide In (from bottom)

Element slides up while fading in. Used for list items, cards, page sections.

```css
@keyframes slide-in-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.slide-in-up {
  animation: slide-in-up var(--duration-normal) var(--ease-out);
}
```

### Expand / Collapse

Accordion or collapsible section expanding. Uses grid trick for smooth height animation:

```css
.expand-collapse {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows var(--duration-normal) var(--ease-in-out);
}
.expand-collapse[data-open="true"] {
  grid-template-rows: 1fr;
}
.expand-collapse > .content {
  overflow: hidden;
}
```

### Skeleton Shimmer

Loading placeholder with a sweeping gradient.

```css
@keyframes shimmer {
  from { background-position: -200% 0; }
  to { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(
    90deg,
    var(--muted) 0%,
    var(--muted-foreground) / 0.08 50%,
    var(--muted) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s linear infinite;
  border-radius: var(--radius);
}
```

### Modal Entrance / Exit

Modal scales up slightly while fading in. Reverse for exit.

```css
/* Overlay */
@keyframes overlay-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Modal content */
@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.modal-overlay { animation: overlay-in var(--duration-fast) var(--ease-out); }
.modal-content { animation: modal-in var(--duration-normal) var(--ease-out); }

/* Exit — play in reverse with ease-in */
.modal-overlay[data-closing] { animation: overlay-in var(--duration-fast) var(--ease-in) reverse; }
.modal-content[data-closing] { animation: modal-in var(--duration-fast) var(--ease-in) reverse; }
```

---

## Framer Motion

When the project uses `framer-motion`, apply the same duration/easing tokens from above via Framer's `transition` prop. Key patterns: `fadeInUp` variants for page elements, `staggerChildren` for lists, and `AnimatePresence` for mount/unmount animations (modals, toasts). Use `useReducedMotion()` hook for the reduced motion fallback.

---

## Reduced Motion

- **CSS** — Add `@media (prefers-reduced-motion: reduce)` that sets `animation-duration`, `animation-iteration-count`, `transition-duration` to near-zero on `*, *::before, *::after`.
- **Tailwind** — Use `motion-safe:` and `motion-reduce:` modifiers on animation classes.
- **Framer Motion** — Use `useReducedMotion()` hook to conditionally zero out durations and transforms.

---

## Motion Sampler Section (Sink Page)

The sink page should include a **Motion Sampler** section that demonstrates all defined patterns interactively:

1. **Hover lift** — A row of cards that lift on hover
2. **Fade in** — A button that triggers a fade-in element
3. **Slide in** — A button that triggers staggered list items sliding in
4. **Expand/collapse** — An accordion demonstrating smooth height transitions
5. **Skeleton → content** — A toggle that swaps between skeleton loaders and real content
6. **Modal entrance/exit** — A button that opens/closes a modal with the defined animation
7. **Reduced motion toggle** — A switch that simulates `prefers-reduced-motion` to demonstrate the fallback behavior

Each demo should show the animation AND display the duration token and easing curve being used, so the sink serves as both a demo and documentation.
