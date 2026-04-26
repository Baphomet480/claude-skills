---
name: kitchen-sink-design-system
version: 2.0.0
description: "Script-First design system workflow. Uses a deterministic auditor script to detect frameworks, inventory components, and detect design drift (hardcoded hex, arbitrary Tailwind). Provides a clear report for the agent to judge and implement a Kitchen Sink page."
---

# Kitchen Sink Design System

Build every component for real, wire it into a single sink page, and let the page prove the design system works.

This workflow uses a **Script-First** approach: an auditor script handles the "labor" of crawling the codebase and identifying drift, leaving the agent to handle the "judgment" of fixing components and assembling the sink.

## Usage

When asked for a Kitchen Sink page, Design System Audit, or Component Inventory:

1. **Run the auditor script:**
   ```bash
   python3 ~/.agents/skills/kitchen-sink-design-system/scripts/audit_design_system.py \
     --root "." \
     --out "design_audit.json"
   ```

2. **Read the report:**
   Load `design_audit.json` to see:
   - Detected framework (Next.js, Astro, etc.).
   - Inventory of existing components.
   - **Design Drift Report:** Hardcoded hex values and arbitrary Tailwind values (`-[...]`) found in component files.
   - **Checklist Gap:** Tier 1 primitives (Button, Card, etc.) missing from the codebase.

3. **Establish/Adopt:**
   - If a guide exists: Map discovered tokens to the guide.
   - If no guide exists: Propose a `design-tokens.md` based on de-facto tokens found in the drift report.

## Phase 1: Build & Fix Components

For every **MISSING** item or file with **DRIFT**:
- Refactor to use semantic design tokens.
- Apply the **base + variant** pattern (CVA for React, Props for Astro).
- Wire into the sink page immediately.

## Phase 2: Assemble Sink Page

Create the sink route (e.g., `app/sink/page.tsx` or `src/pages/sink.astro`) following the standard section order:
1. Header & Franchise declaration
2. Design Tokens visualization
3. Voice & Tone
4. Illustration Gallery (via **omni-image**)
5. Component categories (Typography, Buttons, Forms, etc.)

## Phase 3: Verify

```bash
pnpm build
pnpm lint
pnpm dlx @axe-core/cli http://localhost:3000/sink
```

## Anti-patterns (The "Hot Take" List)
- **Agent labor:** Don't manually `grep` for hex codes; use the script.
- **Draft placeholders:** Build real components or nothing.
- **Arbitrary values:** `w-[37px]` is a failure of the design system.
- **Count drift:** Deriving counts from collections, not hardcoding strings.
