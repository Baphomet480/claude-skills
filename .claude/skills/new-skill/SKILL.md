---
name: new-skill
description: Scaffold a new skill directory under skills/ that passes scripts/audit_skills.py on first run. Use when adding a new portable agent skill to this repo.
version: 1.0.0
disable-model-invocation: true
---

# new-skill

Creates a new skill at `skills/<name>/` with a valid `SKILL.md` (correct frontmatter, kebab-case name, semver version) so it passes `python3 scripts/audit_skills.py skills` immediately.

## Usage

```bash
bash "$CLAUDE_PROJECT_DIR/.claude/skills/new-skill/scripts/scaffold.sh" <skill-name> "<one-line description>"
```

`<skill-name>` must be kebab-case (lowercase letters, digits, hyphens — no underscores, no dots).

## What it does

1. Validates the name against the audit script's kebab-case regex.
2. Refuses to overwrite an existing `skills/<skill-name>/`.
3. Copies `templates/SKILL.md` into `skills/<skill-name>/SKILL.md`, substituting `{{name}}` and `{{description}}`.
4. Runs `python3 scripts/audit_skills.py skills` and reports the result.

## After scaffolding

- Flesh out the SKILL.md body (Workflow, references, examples).
- Add `references/`, `templates/`, `scripts/`, `examples/` directories only if the skill needs them.
- Bump the `version` in frontmatter when you make changes (see CLAUDE.md → Versioning).
- The `package-skill.sh` PostToolUse hook will rebuild `dist/<skill-name>.skill` automatically on the first edit.
