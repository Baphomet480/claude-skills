# GEMINI.md — claude-skills

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
| `google-workspace`           | Unified Gmail, Calendar, Contacts, Drive, Docs, Sheets, and Photos — includes HTML email support and robust auth maintenance.                                                |
| `familysearch`               | FamilySearch API — person lookup, pedigree trees, record search, sources, and memories                                                                                       |

## Workflow

1. **Edit** skill source in `skills/<name>/`
2. **Commit** — the pre-commit hook auto-packages changed skills into `dist/<name>.skill`
3. **Install** — copy skill directory to target agent's skill location:
   - Claude: `<project>/.agent/skills/<name>/`
   - Gemini: `~/.gemini/antigravity/skills/<name>/`

## Conventions

- **No build system** — this repo has no `package.json` or runtime dependencies
- **Franchise placeholder**: Star Wars (use for sample data, form labels, empty states)
- **ZIP format** — `.skill` files are standard ZIP archives renamed for clarity

## Bug Filing Protocol

When a skill script returns a JSON response with `"type": "UnhandledException"`, the agent must:

1. **Read the `fix` field** for an Agent Directive with specific instructions.
2. **Document the bug** by appending a row to the skill's `KNOWN_BUGS.md` file with: date, the command that was run, the error message, and status "open".
3. **Notify the user** that an internal bug was caught and logged.
4. **Check the `logFile` field** for the path to the full traceback on disk. Reference this path when documenting the bug.

Each skill with scripts has a `KNOWN_BUGS.md` at its root (`skills/<name>/KNOWN_BUGS.md`). Error logs are persisted to disk:
- FamilySearch: `~/.familysearch/logs/error.log`
- Google Workspace: `~/.google_workspace/logs/error.log`
- OCR: `~/.ocr/logs/error.log`
