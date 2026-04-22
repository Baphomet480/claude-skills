# Design: Rename `openai-image` to `omni-image`

**Status:** Draft
**Date:** 2026-04-21

## 1. Goal
Rename the `openai-image` skill to `omni-image` to reflect its multi-model (xAI/OpenAI) and multi-functional (generation, vision, editing, restoration) features.

## 2. Structural Changes
- **Directory:** `skills/openai-image/` -> `skills/omni-image/`
- **Main Script:** `skills/omni-image/scripts/openai_image.py` -> `skills/omni-image/scripts/omni_image.py`
- **Binary Alias:** The command invoked by the agent/user will change from `openai-image` to `omni-image`.

## 3. Documentation Updates
- **SKILL.md:** Update `name: omni-image`, version bump to `2.0.0` (major change due to binary rename), and update all internal examples.
- **CLAUDE.md / README.md:** Update the skill table and purpose description.
- **Cross-Skill References:** Update `llms-txt` and `kitchen-sink-design-system` references to point to `omni-image`.

## 4. Internal Logic Updates
- **Metadata:** Update the `Software` metadata tag in `omni_image.py` to `omni-image-skill`.
- **Examples:** Update the Python wrapper example and batch JSON examples.

## 5. Validation Plan
- Run `python3 scripts/audit_skills.py skills` to verify the new structure.
- Run `./scripts/install-skills.sh` to update symlinks in `~/.gemini/skills/` and other agent paths.
- Execute a dry-run of the new `omni-image` command to verify pathing.
