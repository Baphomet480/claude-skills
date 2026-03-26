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

- **SKILL.md** (required) — YAML frontmatter (`name`, `description`, `version`) + detailed markdown instructions
- **references/** — Deep technical docs, checklists, and lookup material
- **templates/** — Starter code files agents can copy into projects
- **examples/** — Reference implementations
- **scripts/** — Helper scripts (scanners, generators, etc.)

Skills are consumed by both Claude (`~/.claude/skills/`) and Gemini (`~/.gemini/antigravity/skills/`).

## Current Skills

| Skill                        | Purpose                                                                      |
| ---------------------------- | ---------------------------------------------------------------------------- |
| `cloudflare-pages`           | Cloudflare Pages deployment, custom domains, and CI/CD                       |
| `deep-research`              | Multi-round deep research producing visual reports with citations            |
| `design-lookup`              | CSS components, SVG icons, and design pattern discovery from the web         |
| `google-workspace`           | Google Workspace (Drive, Docs, Sheets, Gmail, Calendar) via the `gws` CLI   |
| `kitchen-sink-design-system` | Framework-agnostic Kitchen Sink design system workflow and component inventory|
| `nextjs-tinacms`             | Next.js 16 + TinaCMS + Tina Cloud + Vercel -- visual editing, blocks, SEO   |
| `openai-image`               | OpenAI image generation, editing, vision, batch processing, and transforms   |
| `print-css`                  | Print stylesheets: @page, page breaks, colors, images, Next.js/Tailwind     |
| `stitch-mcp`                 | Google Stitch MCP for UI design: screens, design systems, variants, prompts  |

## Workflow

1. Edit skill source in `skills/<name>/`
2. Commit -- the pre-commit hook auto-packages changed skills into `dist/<name>.skill`
3. Install -- copy or symlink skill directory to target location:
   - Canonical: `~/.agents/skills/<name>/` (agent-agnostic, shared by all AIs)
   - Claude reads from `~/.claude/skills/` (symlinks to `~/.agents/skills/`)
   - Gemini reads from `~/.gemini/antigravity/skills/`
   - Or publish via `npx skills` ecosystem (see https://skills.sh/)

## Conventions

- No build system -- this repo has no `package.json` or runtime dependencies
- Franchise placeholder: Star Wars (use for sample data, form labels, empty states)
- `.skill` files are standard ZIP archives renamed for clarity
- Always edit in `skills/`, never edit `dist/` directly

## Versioning

Each SKILL.md frontmatter includes a `version` field using semver (`major.minor.patch`). When you modify a skill's SKILL.md or scripts, bump the version:

- **Patch** (1.0.0 -> 1.0.1): bug fixes, typo corrections, doc clarifications
- **Minor** (1.0.0 -> 1.1.0): new features, new commands, new sections
- **Major** (1.0.0 -> 2.0.0): breaking changes to script CLI, manifest format, or skill structure

## Bug Filing Protocol

When a skill script returns a JSON response with `"type": "UnhandledException"`, the agent must:

1. **Read the `fix` field** for an Agent Directive with specific instructions.
2. **Document the bug** by appending a row to the skill's `KNOWN_BUGS.md` file with: date, the command that was run, the error message, and status "open".
3. **Notify the user** that an internal bug was caught and logged.
4. **Check the `logFile` field** for the path to the full traceback on disk. Reference this path when documenting the bug.

Skills with scripts may have a `KNOWN_BUGS.md` at their root (`skills/<name>/KNOWN_BUGS.md`). Error logs are persisted to disk:
- OpenAI Image: `~/.openai_image/logs/error.log`
