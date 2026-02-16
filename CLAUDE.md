# CLAUDE.md — claude-skills

## Project Purpose

Portable AI agent skill distribution repo. Skills are framework-agnostic instruction sets that extend agent capabilities for specialized tasks.

## Repository Structure

```
skills/          ← Source directories (edit here)
dist/            ← Packaged .skill ZIP files (auto-generated)
hooks/pre-commit ← Auto-packages modified skills into dist/ on commit
```

## How Skills Work

Each skill is a self-contained directory under `skills/` with:

- **SKILL.md** (required) — YAML frontmatter (`name`, `description`) + detailed markdown instructions
- **references/** — Deep technical docs, checklists, and lookup material
- **templates/** — Starter code files agents can copy into projects
- **examples/** — Reference implementations
- **scripts/** — Helper scripts (scanners, generators, etc.)

Skills are consumed by both Claude (`.agent/skills/`) and Gemini (`~/.gemini/antigravity/skills/`).

## Current Skills

| Skill                        | Purpose                                                                                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `kitchen-sink-design-system` | Framework-agnostic Kitchen Sink design system workflow — component inventory, tiered checklists, CVA patterns, voice/tone, motion tokens |
| `nextjs-tinacms`             | Next.js 16 + React 19 + TinaCMS — scaffolding through production deployment, 247-task checklist                                          |
| `cloudflare-pages`           | Cloudflare Pages deployment and configuration                                                                                            |
| `deep-research`              | Structured deep research methodology                                                                                                     |
| `design-lookup`              | Design system discovery and reference                                                                                                    |
| `hugo-sveltia-cms`           | Hugo + Sveltia CMS integration                                                                                                           |
| `pitolandia-visual-identity` | Pitolandia brand visual identity system                                                                                                  |
| `remini-web`                 | Remini web enhancement workflow with manual login and browser-assisted upload/download automation                                        |

## Workflow

1. Edit skill source in `skills/<name>/`
2. Commit — the pre-commit hook auto-packages changed skills into `dist/<name>.skill`
3. Install — copy skill directory to target agent's skill location:
   - Claude: `<project>/.agent/skills/<name>/`
   - Gemini: `~/.gemini/antigravity/skills/<name>/`

## Conventions

- No build system — this repo has no `package.json` or runtime dependencies
- Franchise placeholder: Star Wars (use for sample data, form labels, empty states)
- `.skill` files are standard ZIP archives renamed for clarity
- Always edit in `skills/`, never edit `dist/` directly
