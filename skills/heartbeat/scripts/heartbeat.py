#!/usr/bin/env python3

import json
import os
import sys
import uuid
from datetime import datetime, timezone
import subprocess
import argparse

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

def ensure_dirs():
    os.makedirs(STATE_DIR, exist_ok=True)

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {"pending": [], "in_progress": [], "completed": [], "failed": []}
    with open(TASKS_FILE, 'r') as f:
        data = json.load(f)
        if "failed" not in data:
            data["failed"] = []
        return data

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def log_error(task, reason, trace_id=None, decision_log=None):
    if not os.path.exists(ERRORS_FILE):
        errors = []
    else:
        try:
            with open(ERRORS_FILE, 'r') as f:
                errors = json.load(f)
        except json.JSONDecodeError:
            errors = []
            
    error_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "task_id": task.get("id"),
        "assigned_skill": task.get("assigned_skill"),
        "reason": reason,
        "trace_id": trace_id,
        "decision_log": decision_log,
        "resolved": False
    }
    errors.append(error_entry)
    with open(ERRORS_FILE, 'w') as f:
        json.dump(errors, f, indent=2)

def log_last_run(task, status, outcome_details=None, trace_id=None, decision_log=None):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "task_id": task.get("id"),
        "status": status,
        "description": task.get("description"),
        "assigned_skill": task.get("assigned_skill"),
        "project_id": task.get("project_id"),
        "agent_id": task.get("agent_id"),
        "user_id": task.get("user_id"),
        "outcome": outcome_details or {},
        "trace_id": trace_id,
        "decision_log": decision_log
    }
    with open(LAST_RUN_FILE, 'w') as f:
        json.dump(log_entry, f, indent=2)

def add_task(priority, assigned_skill, description, project_id=None, agent_id=None, user_id=None):
    ensure_dirs()
    tasks = load_tasks()
    task = {
        "id": f"task-{str(uuid.uuid4())[:8]}",
        "priority": priority,
        "description": description,
        "assigned_skill": assigned_skill,
        "project_id": project_id,
        "agent_id": agent_id,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "completed_at": None
    }
    tasks["pending"].append(task)
    # Sort by priority: high > medium > low
    priority_map = {"high": 0, "medium": 1, "low": 2}
    tasks["pending"].sort(key=lambda x: priority_map.get(x.get("priority", "medium"), 1))
    save_tasks(tasks)
    print(f"Added task {task['id']}")
    return task

def pop_task():
    ensure_dirs()
    tasks = load_tasks()
    if not tasks.get("pending"):
        print("No pending tasks.")
        return None
    
    task = tasks["pending"].pop(0)
    tasks["in_progress"].append(task)
    save_tasks(tasks)
    
    print(json.dumps(task, indent=2))
    return task

def complete_task(task_id, status="completed", outcome=None, trace_id=None, decision_log=None):
    ensure_dirs()
    tasks = load_tasks()
    
    # Find in in_progress
    task_idx = None
    for i, t in enumerate(tasks.get("in_progress", [])):
        if t.get("id") == task_id:
            task_idx = i
            break
            
    if task_idx is None:
        print(f"Task {task_id} not found in in_progress.")
        return
        
    task = tasks["in_progress"].pop(task_idx)
    task["completed_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    
    if status == "completed":
        tasks["completed"].append(task)
    else:
        tasks["failed"].append(task)
        reason = outcome.get("reason", "Unknown failure") if outcome else "Unknown failure"
        log_error(task, reason, trace_id, decision_log)
        
    save_tasks(tasks)
    log_last_run(task, status, outcome, trace_id, decision_log)
    print(f"Marked task {task_id} as {status}.")

def list_tasks():
    ensure_dirs()
    tasks = load_tasks()
    print(json.dumps(tasks, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Heartbeat Orchestrator - Task Queue Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("--priority", choices=["high", "medium", "low"], default="medium")
    add_parser.add_argument("--skill", required=True, help="Assigned skill")
    add_parser.add_argument("--project-id", help="Optional project ID for memory scoping")
    add_parser.add_argument("--agent-id", help="Optional agent ID for memory scoping")
    add_parser.add_argument("--user-id", help="Optional user ID for memory scoping")
    add_parser.add_argument("description", help="Task description")
    
    subparsers.add_parser("pop", help="Pop the highest priority pending task and move to in_progress")
    
    complete_parser = subparsers.add_parser("complete", help="Mark an in_progress task as completed")
    complete_parser.add_argument("task_id", help="ID of the task")
    complete_parser.add_argument("--outcome", help="Optional outcome details (JSON string)")
    complete_parser.add_argument("--trace-id", help="Optional trace ID for observability")
    complete_parser.add_argument("--decision-log", help="Optional decision log for observability")
    
    fail_parser = subparsers.add_parser("fail", help="Mark an in_progress task as failed")
    fail_parser.add_argument("task_id", help="ID of the task")
    fail_parser.add_argument("--reason", help="Optional failure reason")
    fail_parser.add_argument("--trace-id", help="Optional trace ID for observability")
    fail_parser.add_argument("--decision-log", help="Optional decision log for observability")
    
    subparsers.add_parser("list", help="List all tasks")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_task(args.priority, args.skill, args.description, args.project_id, args.agent_id, args.user_id)
    elif args.command == "pop":
        pop_task()
    elif args.command == "complete":
        outcome = None
        if args.outcome:
            try:
                outcome = json.loads(args.outcome)
            except:
                outcome = {"result": args.outcome}
        complete_task(args.task_id, "completed", outcome, args.trace_id, args.decision_log)
    elif args.command == "fail":
        outcome = {"reason": args.reason} if args.reason else {}
        complete_task(args.task_id, "failed", outcome, args.trace_id, args.decision_log)
    elif args.command == "list":
        list_tasks()

if __name__ == "__main__":
    main()
