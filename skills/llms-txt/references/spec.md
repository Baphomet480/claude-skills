# llmstxt.org Specification Summary

Source: [llmstxt.org](https://llmstxt.org/) by Jeremy Howard (fast.ai / Answer.AI), published 2024-09-03.

## Core Concept

A `/llms.txt` file is a **Markdown file** served at a site's root path that provides LLM-friendly context about the site. It solves the problem of LLMs needing to understand a site's content without crawling and parsing complex HTML.

The file is for **inference time** (when an agent needs to understand a site to help a user), not primarily for training.

## Format Rules

The file is standard Markdown with this specific structure:

1. **H1 heading** (required) -- the project or site name
2. **Blockquote** (optional) -- short summary with key information
3. **Body paragraphs** (optional) -- additional context, no headings allowed here
4. **H2 sections** (optional) -- each containing a list of links to detailed pages
5. **"Optional" H2 section** (optional) -- links that can be skipped for shorter context

Link format within H2 sections:
```markdown
- [Link title](https://url): Optional description of the linked content
```

## File Variants

| Path | Content | Convention |
|------|---------|------------|
| `/llms.txt` | Curated index with links. Small, always fits in context. | Spec-defined |
| `/llms-full.txt` | Complete documentation content inlined. Large. | Community convention |
| `/llms-small.txt` | Compact version, non-essential content removed. | Community convention |
| `*.html.md` | Markdown version of any HTML page (append `.md` to URL). | Proposed in spec |

## What the Spec Does NOT Define

- No required sections beyond the H1
- No schema for metadata or frontmatter
- No `style` parameter or structured brand fields
- No versioning mechanism
- No authentication or access control

The spec is deliberately minimal. The "Instructions for LLMs" section (used by Stripe and others) is a community convention, not part of the spec.

## Relationship to Other Standards

| Standard | Purpose | Relationship |
|----------|---------|-------------|
| `robots.txt` | Controls crawler access | Different purpose; llms.txt is for inference |
| `sitemap.xml` | Lists all indexable pages | Too large; llms.txt is curated |
| `humans.txt` | Credits the team behind a site | Complementary |
| JSON-LD / Schema.org | Structured page metadata | Complementary |

## Tooling

- `llms_txt2ctx` -- CLI tool that expands llms.txt by fetching and inlining linked content
- VitePress, Docusaurus, Drupal plugins for auto-generation
- [llmstxt.site](https://llmstxt.site/) and [directory.llmstxt.cloud](https://directory.llmstxt.cloud/) -- directories of known files
