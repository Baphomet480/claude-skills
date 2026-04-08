---
name: llms-txt
version: 1.0.0
description: Generate /llms.txt and /llms-full.txt files for web projects following the llmstxt.org spec. Analyzes project source code and optionally the live site to produce LLM-friendly context files with brand guardrails, content structure, and documentation links. Use this skill when deploying a web project, when site structure or brand identity changes, when the user mentions "llms.txt", or when preparing a site for AI agent consumption. Trigger on "generate llms.txt", "create llms.txt", "add llms.txt", "update llms.txt", "make the site AI-friendly", or any mention of the llmstxt.org standard.
---

# llms.txt Generator

Generate `/llms.txt` and `/llms-full.txt` files for web projects. These files give LLMs instant context about a site's purpose, structure, brand identity, and usage guidelines -- following the [llmstxt.org](https://llmstxt.org/) specification.

## When to Use

- Deploying a web project to production
- Site structure, brand, or documentation has changed
- User asks for `/llms.txt` or wants the site to be "AI-friendly"
- As part of any new project setup (required by global convention)

## Output Files

| File | Purpose | Size |
|------|---------|------|
| `/llms.txt` | Curated index with links and LLM instructions. Always fits in context. | Small (1-5 KB) |
| `/llms-full.txt` | Complete site content inlined into one file. For deep analysis. | Large (10-500+ KB) |
| `/llms-small.txt` | Compact version with non-essential content stripped. Optional (`--small` flag). | Medium (5-50 KB) |

## Workflow

### Phase 1: Source Analysis

Read the project to understand what it is and what it contains.

1. **Identify the framework** -- check `package.json`, config files, directory structure:
   - Next.js: `next.config.*`, `app/` or `pages/`
   - Astro: `astro.config.*`, `src/pages/`
   - Nuxt: `nuxt.config.*`, `pages/`
   - SvelteKit: `svelte.config.*`, `src/routes/`
   - Static: `index.html`, `public/`
   - Other: infer from structure

2. **Map public routes/pages** -- list all user-facing pages:
   - For file-based routing: scan `app/`, `pages/`, `src/pages/`, `src/routes/`
   - For static sites: scan all `.html` files
   - Note dynamic routes (e.g., `[slug]`, `[...catchall]`) and describe the pattern
   - Group routes by section (docs, blog, API, marketing, etc.)

3. **Read existing docs** -- extract project context from:
   - `README.md`, `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`
   - `package.json` (name, description, keywords)
   - Any `docs/` directory
   - API documentation if present
   - Content schemas (TinaCMS `tina/config.ts`, Contentful models, etc.)

4. **Identify key resources** -- find files an LLM would need:
   - API routes and their purposes
   - Component library or design system docs
   - Configuration files that affect behavior
   - Database schemas or data models

### Phase 2: Brand Context

Extract brand identity from the project source and optionally the live site.

**From source code:**
- CSS custom properties / design tokens (colors, fonts, spacing)
- Tailwind config (`tailwind.config.*`) -- theme colors, font families
- Brand asset directories (`public/brand/`, `assets/brand/`, etc.)
- Style guides or voice guidelines in the repo
- `voice-reviewer` skill config if present

**From live site (if a URL is provided or discoverable):**
- `<meta>` tags: description, keywords, author, theme-color
- Open Graph tags: og:title, og:description, og:image
- Favicon and apple-touch-icon (visual identity)
- CSS custom properties from the rendered stylesheet
- Existing `/robots.txt` and `/sitemap.xml` for structure hints

**Compose the brand profile:**
```
Name: [project/company name]
Description: [one-line purpose]
Visual style: [e.g., "editorial travel photography, muted warm tones"]
Color palette: [extracted hex values with names]
Typography: [font families]
Tone: [e.g., "professional but approachable, concise, no jargon"]
Photography: [e.g., "real photos preferred over AI-generated, Fujifilm aesthetic"]
```

### Phase 3: Generate /llms.txt

The file is **Markdown** following the llmstxt.org spec. Structure it in this order:

```markdown
# {Project Name}

> {One-line description of what the project/site is}

{2-3 sentences of key context: what the site does, who it serves, what technology it uses.}

## Instructions for LLMs

{Brand guardrails and behavioral guidance for any AI agent working with or referencing this site.}

### Visual Identity
- Color palette: {extracted colors with names}
- Typography: {font families}
- Photography style: {e.g., "editorial, warm tones, shot on Fujifilm X-T4 aesthetic"}
- Image generation: {e.g., "always edit real photos, never generate from scratch. Use --prefix for steering."}

### Tone and Voice
- {tone guidelines extracted from voice docs, README, or inferred from content}
- {specific dos and don'ts}

### Technical Guidelines
- {framework-specific guidance, e.g., "this is a Next.js 16 app with App Router"}
- {API usage patterns, preferred endpoints, deprecated features}
- {version pinning notes if relevant}

## Documentation

- [Page Title](https://url): Brief description of what this page covers
- [Page Title](https://url): Brief description
{... one entry per key documentation page}

## API

- [Endpoint or API doc](https://url): Description
{... if the site has an API}

## Content

- [Section or page](https://url): Description
{... key content pages grouped logically}

## Optional

- [Secondary resource](https://url): Description
{... nice-to-have pages that can be skipped for shorter context}
```

**Key rules for the LLM Instructions section:**
- Be specific and actionable. "Use muted warm tones" is better than "be on-brand."
- Include extracted color hex values -- agents generating images or CSS need exact values.
- Reference specific tools or techniques when relevant (e.g., `--prefix` for the openai-image skill).
- If the site has voice guidelines, summarize them here.
- If the site has API endpoints, note which to prefer and which are deprecated.
- Stripe's pattern is the gold standard: explicit, practical instructions that prevent common mistakes.

**Link format:**
- Use absolute URLs for deployed sites
- Use relative paths for pre-deploy generation (the agent or build step can absolutize later)
- Include the `.md` suffix convention if the site supports it: `https://example.com/docs/setup.md`

### Phase 4: Generate /llms-full.txt

Concatenate key page content into a single file. Structure:

```markdown
# {Project Name} -- Full Documentation

> {Same description as /llms.txt}

## Instructions for LLMs

{Same instructions section as /llms.txt -- always include this at the top}

---

## {Section: e.g., Getting Started}

{Full content of the page, converted to clean markdown}

---

## {Section: e.g., API Reference}

{Full content of the page}

{... repeat for all key pages}
```

**Content sources (in priority order):**
1. Markdown/MDX source files in the repo (cleanest, no HTML stripping needed)
2. Built output (`.next/`, `dist/`, `out/`) parsed to markdown
3. Live site pages fetched and converted to markdown

**What to include:** Documentation, guides, API reference, key content pages.
**What to exclude:** Navigation chrome, footers, cookie banners, marketing boilerplate, duplicate content from shared layouts.

### Phase 5: Generate /llms-small.txt (Optional)

Only when requested or when `--small` flag is used. Create a compact version by:

1. Start from `/llms.txt` (the index)
2. Inline only the most critical 3-5 pages (getting started, API overview, key concepts)
3. Summarize rather than dump -- one paragraph per page instead of full content
4. Keep the LLM Instructions section intact (never abbreviate this)
5. Drop the "Optional" section entirely

## Output Placement

Place generated files based on the framework:

| Framework | Output directory |
|-----------|-----------------|
| Next.js | `public/` |
| Astro | `public/` |
| Nuxt | `public/` |
| SvelteKit | `static/` |
| Static HTML | root `/` |
| Other | root `/` (ask user if unclear) |

The files must be served at the root URL path: `https://example.com/llms.txt`, not nested under a subdirectory.

## Agent Behavior

When invoked, the agent should:

1. **Check for existing files.** If `/llms.txt` already exists, read it and ask whether to regenerate or update.
2. **Ask for the live URL** if not obvious from the project config (e.g., `vercel.json`, `CNAME`, deployment config).
3. **Run all five phases** in order. Phases 1-2 are analysis, Phases 3-5 are generation.
4. **Show the LLM Instructions section** to the user for review before writing. This section captures brand identity and behavioral rules -- the user should validate it.
5. **Write the files** to the correct output directory.
6. **Report what was generated** with file sizes and a summary of content coverage.

## Updating Existing Files

When a site's `/llms.txt` needs updating (new pages, changed brand, etc.):

1. Read the existing file
2. Re-run Phase 1 (source analysis) to detect changes
3. Diff the route map against the existing links
4. Add new pages, remove deleted pages, update descriptions for changed pages
5. Preserve any manually-added content in the Instructions section
6. Regenerate `/llms-full.txt` from scratch (content changes make diffs unreliable)

## Integration with Other Skills

- **openai-image**: The LLM Instructions section should include image generation guidance (style, prefix templates, provider preference). Any agent hitting `/llms.txt` before generating images for the site gets brand-appropriate defaults.
- **voice-reviewer**: If voice guidelines exist, summarize them in the Tone and Voice subsection.
- **gs-brand-doc**: Brand colors and typography extracted here can inform PDF generation.
- **kitchen-sink-design-system**: Design token extraction overlaps -- reuse the component inventory if available.
- **nextjs-tinacms**: Content schema from TinaCMS config informs the content structure section.

## Validation

After generation, verify:

- [ ] H1 heading is present and matches the project name
- [ ] Blockquote summary is present and under 200 characters
- [ ] Instructions for LLMs section exists with at least Visual Identity and Tone subsections
- [ ] All links resolve (no 404s for absolute URLs, no missing files for relative paths)
- [ ] `/llms-full.txt` starts with the Instructions section
- [ ] Files are in the correct output directory for the framework
- [ ] No HTML tags leaked into the markdown (clean conversion)
- [ ] File sizes are reasonable: `/llms.txt` under 10 KB, `/llms-full.txt` under 1 MB

## Examples

See `references/examples.md` for annotated real-world examples from Stripe, Next.js, Astro, and Supabase.
See `templates/llms.txt.md` for the starter template.
