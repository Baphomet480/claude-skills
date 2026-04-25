#!/bin/bash
# Scaffold a new skill at skills/<name>/ that passes audit_skills.py.
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: scaffold.sh <skill-name> \"<description>\"" >&2
  exit 64
fi

NAME="$1"
DESC="$2"
REPO="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

# Mirror the audit script's kebab-case regex.
if ! [[ "$NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: '$NAME' is not kebab-case (lowercase letters/digits, hyphens only)." >&2
  exit 1
fi

DEST="$REPO/skills/$NAME"
if [ -e "$DEST" ]; then
  echo "ERROR: $DEST already exists. Refusing to overwrite." >&2
  exit 1
fi

TEMPLATE="$REPO/.claude/skills/new-skill/templates/SKILL.md"
if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: template not found at $TEMPLATE" >&2
  exit 1
fi

mkdir -p "$DEST"
# Substitute placeholders. Use a delimiter unlikely to appear in descriptions.
sed -e "s|{{name}}|$NAME|g" \
    -e "s|{{description}}|$DESC|g" \
    "$TEMPLATE" > "$DEST/SKILL.md"

echo "Created $DEST/SKILL.md"
echo
echo "Running audit..."
if python3 "$REPO/scripts/audit_skills.py" "$REPO/skills" | grep -E "^(❌|  -) " | grep -F "$NAME"; then
  echo "Audit reported issues for $NAME above."
  exit 1
else
  echo "✅ $NAME passes audit_skills.py"
fi
