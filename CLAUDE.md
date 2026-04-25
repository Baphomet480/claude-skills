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
| `buffer-api`                 | Schedule, create, and manage social media posts via the Buffer GraphQL API   |
| `client-feedback`            | Process client feedback emails into tracked issues and draft responses       |
| `cloudflare-pages`           | Cloudflare Pages deployment, custom domains, and CI/CD                       |
| `deep-research`              | Multi-round deep research producing visual reports with citations            |
| `design-lookup`              | CSS components, SVG icons, and design pattern discovery from the web         |
| `gemini-translate`           | Batch-translate content files using Gemini CLI subagent with glossary support|
| `google-workspace`           | Google Workspace (Drive, Docs, Sheets, Gmail, Calendar) via the `gws` CLI   |
| `gs-brand-doc`               | Generate branded PDF documents using GS brand assets                         |
| `kitchen-sink-design-system` | Framework-agnostic Kitchen Sink design system workflow and component inventory|
| `linkedin-chrome`            | LinkedIn content management via Chrome browser automation                    |
| `llms-txt`                   | Generate /llms.txt and /llms-full.txt for web projects (llmstxt.org spec)   |
| `nextjs-tinacms`             | Next.js 16 + TinaCMS + Tina Cloud + Vercel -- visual editing, blocks, SEO   |
| `omni-image`               | xAI/OpenAI image generation, editing, vision, batch processing (xAI default)|
| `print-css`                  | Print stylesheets: @page, page breaks, colors, images, Next.js/Tailwind     |
| `stitch-mcp`                 | Google Stitch MCP for UI design: screens, design systems, variants, prompts  |
| `tina-schema-sync`           | Sync TinaCMS schema definitions with content models                          |
| `voice-reviewer`             | Review and critique voice/tone in written content                            |

## Agent Best Practices

When operating within this repository, agents should adhere to the following directives:

1. **Validation:** Always run `python3 scripts/audit_skills.py skills` before committing changes to ensure new or modified skills comply with repository standards (e.g., kebab-case naming, `SKILL.md` presence, no forbidden loose files).
2. **Installation:** If you add a new skill or fix symlinks, run `./scripts/install-skills.sh` to ensure it is correctly mapped to `~/.agents/skills/`, `~/.claude/skills/`, and `~/.gemini/skills/`.
3. **Versioning:** If you modify a skill's logic or documentation, increment its semver `version` in the `SKILL.md` frontmatter.
4. **No Direct `dist/` Edits:** Never attempt to modify the `.skill` ZIP archives in `dist/`. Edit the source in `skills/` and let the git hooks handle packaging.
5. **Agentic OS Startup:** Upon every invocation, before responding to the user's prompt, check if `.agent/state/tasks.json` has pending tasks. If so, automatically execute the `heartbeat` skill (via `python3 ~/.claude/skills/heartbeat/scripts/heartbeat.py pop`) to process the queue.

## Workflow

1. Edit skill source in `skills/<name>/`
2. `dist/` is rebuilt automatically:
   - **On edit**: PostToolUse hook (`.claude/hooks/package-skill.sh`) rebuilds `dist/<name>.skill` on every Edit/Write
   - **On commit**: Pre-commit hook (`hooks/pre-commit`) packages any remaining staged changes
3. Install -- run the install script to symlink skill directories to all install locations:
   - `./scripts/install-skills.sh`
   This script creates the following symlinks:
   - `~/.agents/skills/<name>/` -> `skills/<name>/` (canonical, agent-agnostic)
   - `~/.claude/skills/<name>/` -> `~/.agents/skills/<name>/`
   - `~/.gemini/skills/<name>/` -> `~/.agents/skills/<name>/`
   (Note: Do not symlink directly to Gemini extensions like Antigravity as Gemini natively loads `~/.gemini/skills/` globally, which would cause duplicate install warnings.)
   - Or publish via `npx skills` ecosystem (see https://skills.sh/)

All install paths are symlinks. Editing any copy edits the upstream source.

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
- OpenAI Image: `~/.omni_image/logs/error.log`
