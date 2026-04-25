#!/bin/bash
# PostToolUse hook: when a SKILL.md is edited, run the structural audit.
# Surfaces frontmatter / naming errors immediately rather than at commit time.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[ -z "$FILE_PATH" ] && exit 0
[[ "$FILE_PATH" != *SKILL.md ]] && exit 0

REPO="$CLAUDE_PROJECT_DIR"
OUTPUT=$(python3 "$REPO/scripts/audit_skills.py" "$REPO/skills" 2>&1)
STATUS=$?

if [ $STATUS -ne 0 ]; then
  echo "audit_skills.py reported failures after editing $FILE_PATH:" >&2
  echo "$OUTPUT" | grep -E '^❌|^  -' >&2
fi

exit 0
