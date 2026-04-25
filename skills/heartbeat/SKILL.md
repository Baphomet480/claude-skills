---
name: heartbeat
version: 1.1.0
description: "Agentic OS Orchestrator. Process and execute tasks from the shared .agent/state/tasks.json queue. Use when the user asks to 'check the queue', 'process tasks', or run the heartbeat."
---

# Heartbeat Orchestrator

The Heartbeat skill acts as the background processor for the Agentic OS. It reads the `.agent/state/tasks.json` queue, identifies pending tasks, routes them to the appropriate skills, and updates the task status upon completion.

## How it works

Use the `heartbeat.py` script included in this skill's `scripts/` directory to manage the queue:

1. **Pop Task**: Run `python3 scripts/heartbeat.py pop` to get the highest priority pending task and move it to `in_progress`.
2. **Execute**: Read the task details and use the appropriate skill (e.g., `osint`, `deep-research`) to fulfill the task.
3. **Complete/Fail**: Run `python3 scripts/heartbeat.py complete <task_id> --outcome '{"result": "..."}'` or `python3 scripts/heartbeat.py fail <task_id> --reason "..."` to update the task status and log to `last-run.json`.

## Task Format

The `tasks.json` should contain an object with status arrays:

```json
{
  "pending": [
    {
      "id": "task-123",
      "priority": "high",
      "description": "Deep research the current state of local LLM orchestration.",
      "assigned_skill": "deep-research",
      "created_at": "2026-04-25T12:00:00Z",
      "completed_at": null
    }
  ],
  "in_progress": [],
  "completed": [],
  "failed": []
}
```

Statuses correspond to the array the task resides in.

## Execution

When invoked (or automatically on agent startup), the Heartbeat should process one task at a time to maintain stability and context length, unless explicitly asked to drain the queue.

## Agentic OS Integration

As a core OS component, this skill MUST log its own execution to `.agent/state/last-run.json`, noting which task was processed and what the outcome was.
