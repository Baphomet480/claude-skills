---
name: bump-skill-version
description: Bump the semver version in a skill's SKILL.md frontmatter following the patch/minor/major rules in CLAUDE.md. Use after modifying a skill's logic or docs.
version: 1.0.0
---

# bump-skill-version

Updates the `version:` field in `skills/<name>/SKILL.md` per the rules in CLAUDE.md → Versioning:

- **patch** — bug fixes, typo corrections, doc clarifications
- **minor** — new features, new commands, new sections
- **major** — breaking changes to script CLI, manifest format, or skill structure

## Usage

```bash
bash "$CLAUDE_PROJECT_DIR/.claude/skills/bump-skill-version/scripts/bump.sh" <skill-name> <patch|minor|major>
```

Reports the old and new version. Refuses to run if the working tree has uncommitted changes to the target SKILL.md (so the bump becomes its own atomic edit) — pass `--force` to override.

## When to use

- After editing any file inside `skills/<skill-name>/` other than trivial whitespace.
- Before committing changes that the agent (or a human reviewer) will publish.

## Notes

- Reads and rewrites the YAML frontmatter in place; preserves all other fields.
- The `package-skill.sh` PostToolUse hook will rebuild `dist/<skill-name>.skill` automatically once the SKILL.md is edited.
