#!/bin/bash
# Install skills via symlinks to canonical agent paths.
# Prevents duplicate install warnings in Gemini.

set -euo pipefail

REPO_DIR=$(pwd)
SKILLS_DIR="$REPO_DIR/skills"

AGENTS_SKILLS="$HOME/.agents/skills"
CLAUDE_SKILLS="$HOME/.claude/skills"
GEMINI_SKILLS="$HOME/.gemini/skills"
ANTIGRAVITY_SKILLS="$HOME/github/dotfiles/gemini/antigravity/skills"
# Also clean up the actual ~/.gemini/antigravity/skills if it's a real dir
GEMINI_EXT_ANTIGRAVITY_SKILLS="$HOME/.gemini/antigravity/skills"

echo "Setting up skill symlinks..."

mkdir -p "$AGENTS_SKILLS"
mkdir -p "$CLAUDE_SKILLS"
mkdir -p "$GEMINI_SKILLS"

# Clean up antigravity skills to prevent Gemini duplicate warnings
echo "Cleaning up legacy antigravity links to prevent duplicates..."
if [ -d "$ANTIGRAVITY_SKILLS" ]; then
  find "$ANTIGRAVITY_SKILLS" -type l -exec rm {} +
fi
if [ -d "$GEMINI_EXT_ANTIGRAVITY_SKILLS" ] && [ ! -L "$GEMINI_EXT_ANTIGRAVITY_SKILLS" ]; then
  find "$GEMINI_EXT_ANTIGRAVITY_SKILLS" -type l -exec rm {} +
fi

for skill_path in "$SKILLS_DIR"/*; do
    if [ -d "$skill_path" ]; then
        skill_name=$(basename "$skill_path")
        
        # 1. Canonical symlink in ~/.agents/skills/
        rm -rf "$AGENTS_SKILLS/$skill_name"
        ln -s "$skill_path" "$AGENTS_SKILLS/$skill_name"
        
        # 2. Symlink to Claude
        rm -rf "$CLAUDE_SKILLS/$skill_name"
        ln -s "$AGENTS_SKILLS/$skill_name" "$CLAUDE_SKILLS/$skill_name"
        
        # 3. Symlink to Gemini
        rm -rf "$GEMINI_SKILLS/$skill_name"
        ln -s "$AGENTS_SKILLS/$skill_name" "$GEMINI_SKILLS/$skill_name"
        
        echo "Linked $skill_name"
    fi
done

echo "✅ All skills installed to ~/.agents/skills, ~/.claude/skills, and ~/.gemini/skills."
