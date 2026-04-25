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
  "agent_runtime": "",
  "skill_executed": "init",
  "summary": "Agentic OS initialized.",
  "decisions": [],
  "next_steps": []
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
  "completed": []
}
EOF
  echo "Created .agent/state/tasks.json"
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

# Inject startup routine into agent instructions if they exist
HEARTBEAT_INSTRUCTION="
## Agentic OS Startup
Upon every invocation, before responding to the user's prompt, check if \`.agent/state/tasks.json\` has pending tasks. If so, automatically execute the \`heartbeat\` skill (via \`python3 scripts/heartbeat.py pop\`) to process the queue.
"

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
