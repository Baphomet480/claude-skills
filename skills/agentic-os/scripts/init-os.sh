#!/usr/bin/env bash
set -euo pipefail

echo "Initializing Agentic OS framework..."

# Determine project root (assumes we are inside a git repo, otherwise use pwd)
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  PROJECT_ROOT=$(git rev-parse --show-toplevel)
else
  PROJECT_ROOT=$(pwd)
fi

AGENT_DIR="$PROJECT_ROOT/.agent"

echo "Creating directories in $AGENT_DIR..."
mkdir -p "$AGENT_DIR/state"
mkdir -p "$AGENT_DIR/learnings"
mkdir -p "$AGENT_DIR/evals"

# Create last-run.json
if [ ! -f "$AGENT_DIR/state/last-run.json" ]; then
  cat > "$AGENT_DIR/state/last-run.json" << 'EOF'
{
  "timestamp": "",
  "task_id": "",
  "status": "",
  "description": "Agentic OS initialized.",
  "assigned_skill": "init",
  "project_id": "",
  "agent_id": "",
  "user_id": "",
  "outcome": {},
  "trace_id": "",
  "decision_log": ""
}
EOF
  echo "Created .agent/state/last-run.json"
fi

# Create tasks.json
if [ ! -f "$AGENT_DIR/state/tasks.json" ]; then
  cat > "$AGENT_DIR/state/tasks.json" << 'EOF'
{
  "pending": [],
  "in_progress": [],
  "completed": [],
  "failed": []
}
EOF
  echo "Created .agent/state/tasks.json"
fi

# Create errors.json
if [ ! -f "$AGENT_DIR/state/errors.json" ]; then
  cat > "$AGENT_DIR/state/errors.json" << 'EOF'
[]
EOF
  echo "Created .agent/state/errors.json"
fi

# Create a template learnings file
if [ ! -f "$AGENT_DIR/learnings/template.json" ]; then
  cat > "$AGENT_DIR/learnings/template.json" << 'EOF'
{
  "skill": "template",
  "history": [
    {
      "date": "YYYY-MM-DD",
      "what_worked": "",
      "what_didnt": "",
      "rule_change": "This is a template. Duplicate this file and rename to <skill-name>.json to implement a feedback loop."
    }
  ]
}
EOF
  echo "Created .agent/learnings/template.json"
fi

# Create a template evals file
if [ ! -f "$AGENT_DIR/evals/template.json" ]; then
  cat > "$AGENT_DIR/evals/template.json" << 'EOF'
{
  "skill": "template",
  "criteria": [
    "This is a template. Duplicate this file and rename to <skill-name>.json to define quality gates.",
    "Must output valid markdown."
  ]
}
EOF
  echo "Created .agent/evals/template.json"
fi

echo "✅ Agentic OS successfully initialized."
echo "Agents (Claude, Gemini, Antigravity) will now share persistent memory and learnings in this project."

# Sync skill eval templates from global skills directory
SKILLS_DIR=$(cd "$(dirname "$0")/../.." && pwd)
for eval_file in "$SKILLS_DIR"/*/templates/eval.json; do
  if [ -f "$eval_file" ]; then
    skill_name=$(basename $(dirname $(dirname "$eval_file")))
    cp "$eval_file" "$AGENT_DIR/evals/${skill_name}.json"
    echo "Imported eval template for skill: $skill_name"
  fi
done

# Inject startup routine into agent instructions if they exist
read -r -d '' HEARTBEAT_INSTRUCTION << 'EOF' || true

## Agentic OS Startup
Upon every invocation, before responding to the user's prompt, check if `.agent/state/tasks.json` has pending tasks. If so, automatically execute the `heartbeat` skill (via `python3 ~/.gemini/skills/heartbeat/scripts/heartbeat.py pop` for Gemini/Antigravity or `python3 ~/.claude/skills/heartbeat/scripts/heartbeat.py pop` for Claude) to process the queue.
EOF

if [ -f "$PROJECT_ROOT/GEMINI.md" ]; then
  if ! grep -q "Agentic OS Startup" "$PROJECT_ROOT/GEMINI.md"; then
    echo "$HEARTBEAT_INSTRUCTION" >> "$PROJECT_ROOT/GEMINI.md"
    echo "Injected Agentic OS startup routine into GEMINI.md"
  fi
fi

if [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
  if ! grep -q "Agentic OS Startup" "$PROJECT_ROOT/CLAUDE.md"; then
    echo "$HEARTBEAT_INSTRUCTION" >> "$PROJECT_ROOT/CLAUDE.md"
    echo "Injected Agentic OS startup routine into CLAUDE.md"
  fi
fi
