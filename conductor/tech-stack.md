# Technology Stack

## Core Technologies
- **Shell Scripting:** Bash (used for git hooks and automation scripts like `add_custom_domain.sh`).
- **Scripting:** Python (used for helper utilities like `fetch_page.py`, `convert-toml-to-yaml.py`).
- **Configuration & Metadata:** YAML (Frontmatter in `SKILL.md`, config files), Markdown (Documentation).

## Infrastructure & Tooling
- **Version Control:** Git (Source of truth).
- **Automation:** Git Hooks (specifically `pre-commit` for packaging skills).
- **Packaging:** ZIP (Standard archive format for `.skill` distribution).

## Runtime Environment
- **Agent Environment:** Framework-agnostic, but designed for compatibility with Claude (`.agent/skills/`) and Gemini (`~/.gemini/antigravity/skills/`).
- **No Build System:** The repository deliberately avoids `package.json` or complex build chains to maintain portability and simplicity.
