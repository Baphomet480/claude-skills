#!/usr/bin/env python3

import json
import os
import sys
import subprocess
from datetime import datetime, timezone

def get_project_root():
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        return root
    except Exception:
        return os.getcwd()

AGENT_DIR = os.path.join(get_project_root(), '.agent')
STATE_DIR = os.path.join(AGENT_DIR, 'state')
TASKS_FILE = os.path.join(STATE_DIR, 'tasks.json')
LAST_RUN_FILE = os.path.join(STATE_DIR, 'last-run.json')
ERRORS_FILE = os.path.join(STATE_DIR, 'errors.json')
STATUS_FILE = os.path.join(STATE_DIR, 'status.md')

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_value

def generate_status():
    tasks = load_json(TASKS_FILE, {"pending": [], "in_progress": [], "completed": [], "failed": []})
    last_run = load_json(LAST_RUN_FILE, {})
    errors = load_json(ERRORS_FILE, [])

    lines = []
    lines.append("# Agentic OS Command Center Status")
    lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}Z\n")
    
    # 1. Queue Status
    lines.append("## Task Queue Status")
    lines.append(f"- **Pending**: {len(tasks.get('pending', []))}")
    lines.append(f"- **In Progress**: {len(tasks.get('in_progress', []))}")
    lines.append(f"- **Completed**: {len(tasks.get('completed', []))}")
    lines.append(f"- **Failed**: {len(tasks.get('failed', []))}\n")
    
    if tasks.get('pending'):
        lines.append("### Next 3 Pending Tasks:")
        for t in tasks['pending'][:3]:
            lines.append(f"- `[{t.get('priority', 'medium').upper()}]` {t.get('assigned_skill', 'unknown')} - {t.get('description', '')}")
        lines.append("")

    # 2. Last Run Status
    lines.append("## Last Run Information")
    if last_run:
        lines.append(f"- **Time**: {last_run.get('timestamp', 'Unknown')}")
        lines.append(f"- **Skill**: {last_run.get('assigned_skill', 'Unknown')}")
        lines.append(f"- **Status**: {last_run.get('status', 'Unknown')}")
        lines.append(f"- **Task**: {last_run.get('description', 'Unknown')}")
    else:
        lines.append("No previous runs logged.")
    lines.append("")

    # 3. Errors / Failures Action Items
    lines.append("## Active Errors & Action Items")
    unresolved_errors = [e for e in errors if not e.get("resolved", False)]
    if unresolved_errors:
        for e in unresolved_errors:
            lines.append(f"- `[Task {e.get('task_id', 'Unknown')}]` **{e.get('assigned_skill', 'Unknown')}**: {e.get('reason', 'Unknown reason')}")
    else:
        lines.append("No unresolved errors. All systems green.")
    
    return "\n".join(lines)

def main():
    status_md = generate_status()
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        f.write(status_md)
    print(status_md)

if __name__ == "__main__":
    main()
