#!/bin/bash
# PostToolUse hook: rebuild dist/<skill>.skill when a skill source file changes
# Receives JSON on stdin from Claude Code hook protocol

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[ -z "$FILE_PATH" ] && exit 0

# Extract skill name from path (matches skills/<name>/...)
if [[ "$FILE_PATH" =~ /skills/([^/]+)/ ]]; then
  SKILL="${BASH_REMATCH[1]}"
  REPO="$CLAUDE_PROJECT_DIR"

  if [ -d "$REPO/skills/$SKILL" ]; then
    rm -f "$REPO/dist/${SKILL}.skill"
    (cd "$REPO/skills" && zip -r "$REPO/dist/${SKILL}.skill" "$SKILL/" > /dev/null 2>&1)
    echo "Rebuilt dist/${SKILL}.skill" >&2
  fi
fi

exit 0
