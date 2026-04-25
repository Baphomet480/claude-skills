#!/bin/bash
# PreToolUse hook: refuse to write/edit files inside dist/.
# Enforces the CLAUDE.md rule: dist/ is auto-generated; edit skills/<name>/ instead.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[ -z "$FILE_PATH" ] && exit 0

if [[ "$FILE_PATH" =~ /dist/.*\.skill$ ]] || [[ "$FILE_PATH" =~ ^dist/.*\.skill$ ]]; then
  echo "BLOCKED: dist/ contains auto-generated .skill ZIPs. Edit the source in skills/<name>/ instead — the package-skill.sh hook will rebuild dist/ on Edit/Write." >&2
  exit 2
fi

exit 0
