---
name: command-center
description: Aggregates state across all tasks, errors, and runs to produce a global status dashboard.
version: 1.0.0
---

# Command Center Skill

The `command-center` skill generates a global overview of the Agentic OS framework's state. It aggregates information from `.agent/state/tasks.json`, `.agent/state/last-run.json`, and `.agent/state/errors.json` into a single markdown dashboard (`status.md`).

## Agentic OS Integration
When invoked, this skill reads the persistent memory files and outputs the `status.md` directly. 

## Usage

```bash
python3 scripts/command_center.py
```

This will create/update `.agent/state/status.md` and print the status dashboard to standard output.
