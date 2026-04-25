#!/bin/bash
# Bump the semver version in skills/<name>/SKILL.md frontmatter.
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: bump.sh <skill-name> <patch|minor|major> [--force]" >&2
  exit 64
fi

NAME="$1"
LEVEL="$2"
FORCE=0
[ "${3:-}" = "--force" ] && FORCE=1

case "$LEVEL" in patch|minor|major) ;; *)
  echo "ERROR: level must be one of: patch, minor, major" >&2
  exit 1
;; esac

REPO="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
SKILL_MD="$REPO/skills/$NAME/SKILL.md"

if [ ! -f "$SKILL_MD" ]; then
  echo "ERROR: $SKILL_MD does not exist." >&2
  exit 1
fi

if [ $FORCE -eq 0 ] && ! git -C "$REPO" diff --quiet -- "$SKILL_MD" 2>/dev/null; then
  echo "ERROR: $SKILL_MD has uncommitted changes. Commit or stash first, or pass --force." >&2
  exit 1
fi

OLD=$(awk '/^version:/ { print $2; exit }' "$SKILL_MD")
if [ -z "$OLD" ]; then
  echo "ERROR: no 'version:' line found in $SKILL_MD frontmatter." >&2
  exit 1
fi

if ! [[ "$OLD" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
  echo "ERROR: version '$OLD' is not semver (X.Y.Z)." >&2
  exit 1
fi
MAJOR=${BASH_REMATCH[1]}; MINOR=${BASH_REMATCH[2]}; PATCH=${BASH_REMATCH[3]}

case "$LEVEL" in
  patch) PATCH=$((PATCH+1));;
  minor) MINOR=$((MINOR+1)); PATCH=0;;
  major) MAJOR=$((MAJOR+1)); MINOR=0; PATCH=0;;
esac
NEW="$MAJOR.$MINOR.$PATCH"

# Replace only the first matching version: line (frontmatter).
awk -v old="$OLD" -v new="$NEW" '
  !done && /^version:[[:space:]]/ { sub(old, new); done=1 }
  { print }
' "$SKILL_MD" > "$SKILL_MD.tmp" && mv "$SKILL_MD.tmp" "$SKILL_MD"

echo "$NAME: $OLD -> $NEW ($LEVEL)"
