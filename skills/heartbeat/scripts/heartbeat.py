#!/usr/bin/env python3

import json
import os
import sys
import uuid
from datetime import datetime
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

def log_last_run(task, status, outcome_details=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "task_id": task.get("id"),
        "status": status,
        "description": task.get("description"),
        "assigned_skill": task.get("assigned_skill"),
        "outcome": outcome_details or {}
    }
    with open(LAST_RUN_FILE, 'w') as f:
        json.dump(log_entry, f, indent=2)

def add_task(priority, assigned_skill, description):
    ensure_dirs()
    tasks = load_tasks()
    task = {
        "id": f"task-{str(uuid.uuid4())[:8]}",
        "priority": priority,
        "description": description,
        "assigned_skill": assigned_skill,
        "created_at": datetime.utcnow().isoformat() + "Z",
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

def complete_task(task_id, status="completed", outcome=None):
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
    task["completed_at"] = datetime.utcnow().isoformat() + "Z"
    
    if status == "completed":
        tasks["completed"].append(task)
    else:
        tasks["failed"].append(task)
        
    save_tasks(tasks)
    log_last_run(task, status, outcome)
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
    add_parser.add_argument("description", help="Task description")
    
    subparsers.add_parser("pop", help="Pop the highest priority pending task and move to in_progress")
    
    complete_parser = subparsers.add_parser("complete", help="Mark an in_progress task as completed")
    complete_parser.add_argument("task_id", help="ID of the task")
    complete_parser.add_argument("--outcome", help="Optional outcome details (JSON string)")
    
    fail_parser = subparsers.add_parser("fail", help="Mark an in_progress task as failed")
    fail_parser.add_argument("task_id", help="ID of the task")
    fail_parser.add_argument("--reason", help="Optional failure reason")
    
    subparsers.add_parser("list", help="List all tasks")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_task(args.priority, args.skill, args.description)
    elif args.command == "pop":
        pop_task()
    elif args.command == "complete":
        outcome = None
        if args.outcome:
            try:
                outcome = json.loads(args.outcome)
            except:
                outcome = {"result": args.outcome}
        complete_task(args.task_id, "completed", outcome)
    elif args.command == "fail":
        outcome = {"reason": args.reason} if args.reason else {}
        complete_task(args.task_id, "failed", outcome)
    elif args.command == "list":
        list_tasks()

if __name__ == "__main__":
    main()
