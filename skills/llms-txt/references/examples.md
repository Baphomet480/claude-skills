# Real-World /llms.txt Examples

Annotated examples from production sites. Use these patterns when generating files.

## Stripe (docs.stripe.com/llms.txt)

**Pattern: LLM-specific instructions as a first-class section.**

Stripe's file is the gold standard for the "Instructions for LLMs" approach. Key features:

- Opens with a practical instruction: "When installing Stripe packages, always check the npm registry for the latest version rather than relying on memorized version numbers"
- Dedicated **"Instructions for Large Language Model Agents"** H2 section with:
  - Preferred APIs (Checkout Sessions over deprecated Charges)
  - Version pinning guidance
  - Architecture recommendations (Accounts v2 for Connect)
  - Common mistake prevention
- Links use the `.md` URL convention: `https://docs.stripe.com/testing.md`
- Organized by product area: Docs, Payment Methods, Checkout, Billing, Architecture
- No `/llms-full.txt` -- relies on the `.md` convention for individual page access

**Takeaway:** The instructions section is the most valuable part. Explicit, practical, mistake-preventing guidance.

## Next.js (nextjs.org/llms.txt)

**Pattern: Tiered index with version metadata.**

- Root `/llms.txt` is a high-level pointer to `/docs/llms.txt` and `/docs/llms-full.txt`
- Includes version table: current (16.x), 15.x, 14.x with separate docs for each
- Custom metadata annotations: `@doc-version`, `@doc-version-notes`, `@router`
- Notes that URLs support `.md` extension for direct markdown access
- Also includes blog posts, learning resources, and support policy
- `/docs/llms-full.txt` contains complete documentation content

**Takeaway:** Version awareness matters for documentation sites. The pointer-to-detailed-index pattern scales well for large sites.

## Astro (docs.astro.build/llms.txt)

**Pattern: Topic-based splitting with three tiers.**

- Provides all three tiers: `/llms.txt`, `/llms-small.txt`, `/llms-full.txt`
- Instead of one giant full file, uses **topic-specific files** under `/_llms-txt/`:
  - API Reference, How-to Recipes, Blog Tutorial, Deployment Guides, CMS Guides
- Each topic file is a self-contained `.txt` that can be loaded independently
- "Optional" section links to the Astro blog
- Clean, concise index -- easy to parse at a glance

**Takeaway:** Topic-based splitting is better than one monolithic full file when the documentation covers many distinct areas. Lets agents load only the relevant section.

## Supabase (supabase.com/llms.txt)

**Pattern: SDK-language splitting.**

- Minimal index pointing to language-specific reference files
- Splits by SDK language: JavaScript, Dart, Swift, Kotlin, Python, C#, plus CLI reference
- Each language file is under `/llms/`
- No description blockquote, no Optional section

**Takeaway:** For multi-SDK platforms, split by language. An agent building a Python integration doesn't need the Dart reference.

## Common Patterns Summary

| Pattern | When to use | Example |
|---------|------------|---------|
| **LLM Instructions section** | Always. Every site benefits from explicit agent guidance. | Stripe |
| **Version metadata** | Documentation sites with multiple active versions | Next.js |
| **Topic-based splitting** | Large doc sites with distinct sections | Astro |
| **Language-based splitting** | Multi-SDK platforms | Supabase |
| **Three-tier files** | When both quick context and deep content are needed | Astro |
| **`.md` URL convention** | Sites that can serve markdown versions of HTML pages | Stripe, Next.js |
| **Pointer to sub-index** | Large sites with multiple documentation areas | Next.js |

## Anti-Patterns

- **Dumping the sitemap** -- `/llms.txt` should be curated, not comprehensive. 500 links is a sitemap, not context.
- **Marketing language** -- Write for agents, not humans reading a landing page. "Industry-leading platform" tells an LLM nothing.
- **Missing instructions** -- A file without an Instructions section is just a link list. The behavioral guidance is the highest-value content.
- **Stale content** -- `/llms-full.txt` that doesn't match the live site is worse than no file. Regenerate on deploy.
- **HTML in markdown** -- Leaked `<div>`, `<nav>`, `<script>` tags in the full file waste tokens and confuse parsing.
