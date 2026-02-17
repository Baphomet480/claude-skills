#!/usr/bin/env bash
# Google Workspace Skill — Upgrade from v1 (per-service skills)
#
# Consolidates credentials and replaces old per-service skill installations
# with the unified google-workspace skill.
#
# Usage:
#   bash scripts/upgrade.sh            # run migration
#   bash scripts/upgrade.sh --dry-run  # preview changes without modifying anything

set -euo pipefail

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "=== DRY RUN — no changes will be made ==="
    echo
fi

WORKSPACE_DIR="$HOME/.google_workspace"

# Legacy per-service credential directories
LEGACY_DIRS=(
    "$HOME/.gmail_credentials"
    "$HOME/.calendar_credentials"
    "$HOME/.contacts_credentials"
    "$HOME/.drive_credentials"
    "$HOME/.photos_credentials"
)

# Old skill directory names to remove from agent installations
OLD_SKILLS=(gmail google-calendar google-contacts google-drive google-photos)

# Possible agent skill installation paths
SKILL_INSTALL_PATHS=(
    ".agent/skills"
    ".claude/skills"
)

# ─── Step 1: Consolidate Credentials ─────────────────────────────────

echo "Step 1: Consolidate credentials into $WORKSPACE_DIR"

# Find a token.json from any legacy directory
SOURCE_TOKEN=""
SOURCE_CREDS=""

for dir in "${LEGACY_DIRS[@]}"; do
    if [[ -f "$dir/token.json" && -z "$SOURCE_TOKEN" ]]; then
        SOURCE_TOKEN="$dir/token.json"
    fi
    if [[ -f "$dir/credentials.json" && -z "$SOURCE_CREDS" ]]; then
        SOURCE_CREDS="$dir/credentials.json"
    fi
done

if [[ -n "$SOURCE_TOKEN" ]]; then
    if $DRY_RUN; then
        echo "  Would copy $SOURCE_TOKEN -> $WORKSPACE_DIR/token.json"
    else
        mkdir -p "$WORKSPACE_DIR"
        if [[ ! -f "$WORKSPACE_DIR/token.json" ]]; then
            cp "$SOURCE_TOKEN" "$WORKSPACE_DIR/token.json"
            echo "  Copied token from $SOURCE_TOKEN"
        else
            echo "  Token already exists at $WORKSPACE_DIR/token.json (skipped)"
        fi
    fi
else
    echo "  No legacy token.json found. Run setup_workspace.py to authenticate."
fi

if [[ -n "$SOURCE_CREDS" ]]; then
    if $DRY_RUN; then
        echo "  Would copy $SOURCE_CREDS -> $WORKSPACE_DIR/credentials.json"
    else
        mkdir -p "$WORKSPACE_DIR"
        if [[ ! -f "$WORKSPACE_DIR/credentials.json" ]]; then
            cp "$SOURCE_CREDS" "$WORKSPACE_DIR/credentials.json"
            echo "  Copied credentials from $SOURCE_CREDS"
        else
            echo "  credentials.json already exists at $WORKSPACE_DIR/ (skipped)"
        fi
    fi
fi

echo

# ─── Step 2: Remove Old Skill Installations ──────────────────────────

echo "Step 2: Remove old per-service skill installations"

# Search from the current directory upward for project roots with agent skills
SEARCH_DIR="$(pwd)"
FOUND_ANY=false

while [[ "$SEARCH_DIR" != "/" ]]; do
    for install_path in "${SKILL_INSTALL_PATHS[@]}"; do
        SKILLS_ROOT="$SEARCH_DIR/$install_path"
        if [[ -d "$SKILLS_ROOT" ]]; then
            for old_skill in "${OLD_SKILLS[@]}"; do
                OLD_DIR="$SKILLS_ROOT/$old_skill"
                if [[ -d "$OLD_DIR" ]]; then
                    FOUND_ANY=true
                    if $DRY_RUN; then
                        echo "  Would remove: $OLD_DIR"
                    else
                        rm -rf "$OLD_DIR"
                        echo "  Removed: $OLD_DIR"
                    fi
                fi
            done
        fi
    done
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

# Also check home directory agent configs
for install_path in ".agent/skills" ".claude/skills"; do
    SKILLS_ROOT="$HOME/$install_path"
    if [[ -d "$SKILLS_ROOT" ]]; then
        for old_skill in "${OLD_SKILLS[@]}"; do
            OLD_DIR="$SKILLS_ROOT/$old_skill"
            if [[ -d "$OLD_DIR" ]]; then
                FOUND_ANY=true
                if $DRY_RUN; then
                    echo "  Would remove: $OLD_DIR"
                else
                    rm -rf "$OLD_DIR"
                    echo "  Removed: $OLD_DIR"
                fi
            fi
        done
    fi
done

if ! $FOUND_ANY; then
    echo "  No old skill installations found (clean slate)."
fi

echo

# ─── Step 3: Summary ─────────────────────────────────────────────────

echo "Step 3: Summary"
echo

if $DRY_RUN; then
    echo "  DRY RUN complete. Re-run without --dry-run to apply changes."
else
    echo "  Credentials:  $WORKSPACE_DIR/"
    if [[ -f "$WORKSPACE_DIR/token.json" ]]; then
        echo "  Token:        $WORKSPACE_DIR/token.json"
    fi
    if [[ -f "$WORKSPACE_DIR/credentials.json" ]]; then
        echo "  Client:       $WORKSPACE_DIR/credentials.json"
    fi
    echo
    echo "  Legacy credential directories were preserved (not deleted)."
    echo "  You can safely remove them once you've verified everything works:"
    for dir in "${LEGACY_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            echo "    rm -rf $dir"
        fi
    done
    echo
    echo "  Migration complete. The unified google-workspace skill is ready."
fi
