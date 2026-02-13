# Track Specification: Audit and standardize existing skills

## Overview
This track focuses on auditing the existing skills in the `skills/` directory to ensure they strictly adhere to the project's standards as defined in `product-guidelines.md`. The goal is to bring all legacy and new skills into compliance with a consistent structure, documentation style, and metadata format.

## Objectives
- Verify that every skill has a root `SKILL.md` with valid YAML frontmatter.
- Ensure consistent directory structure (`references/`, `templates/`, `examples/`, `scripts/`).
- Validate that instructions are authoritative, direct, and concise.
- Standardize naming conventions (kebab-case).

## Scope
- **In Scope:**
    - `kitchen-sink-design-system`
    - `nextjs-tinacms`
    - `cloudflare-pages`
    - `deep-research`
    - `design-lookup`
    - `hugo-sveltia-cms`
    - `pitolandia-visual-identity`
- **Out of Scope:**
    - Adding new features to skills (unless critical for standardization).
    - Changes to the distribution mechanism (`dist/` or pre-commit hooks).

## Acceptance Criteria
1.  All skills pass a manual or automated compliance check against the `product-guidelines.md`.
2.  `SKILL.md` files have correct `name` and `description` in YAML frontmatter.
3.  No "loose" files in skill roots other than `SKILL.md` (everything else in subdirs).
4.  All filenames use kebab-case.
