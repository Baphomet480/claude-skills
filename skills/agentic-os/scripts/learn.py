#!/usr/bin/env python3

import json
import os
import sys
import argparse
from datetime import datetime, timezone
import subprocess

def get_project_root():
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        return root
    except Exception:
        return os.getcwd()

AGENT_DIR = os.path.join(get_project_root(), '.agent')
LEARNINGS_DIR = os.path.join(AGENT_DIR, 'learnings')

def add_learning(skill, what_worked, what_didnt, rule_change):
    os.makedirs(LEARNINGS_DIR, exist_ok=True)
    learning_file = os.path.join(LEARNINGS_DIR, f"{skill}.json")
    
    if os.path.exists(learning_file):
        with open(learning_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"skill": skill, "history": []}
        
    entry = {
        "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        "what_worked": what_worked,
        "what_didnt": what_didnt,
        "rule_change": rule_change
    }
    data["history"].append(entry)
    
    with open(learning_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Added learning for skill '{skill}'")

def list_learnings(skill=None):
    if not os.path.exists(LEARNINGS_DIR):
        print("No learnings directory found.")
        return
        
    if skill:
        learning_file = os.path.join(LEARNINGS_DIR, f"{skill}.json")
        if os.path.exists(learning_file):
            with open(learning_file, 'r') as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            print(f"No learnings found for skill '{skill}'")
    else:
        for filename in os.listdir(LEARNINGS_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(LEARNINGS_DIR, filename), 'r') as f:
                    print(f"--- {filename} ---")
                    print(json.dumps(json.load(f), indent=2))

def main():
    parser = argparse.ArgumentParser(description="Agentic OS Learnings Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add_parser = subparsers.add_parser("add", help="Add a new learning for a skill")
    add_parser.add_argument("--skill", required=True, help="The skill name")
    add_parser.add_argument("--worked", required=True, help="What worked")
    add_parser.add_argument("--didnt", required=True, help="What didn't work")
    add_parser.add_argument("--rule", required=True, help="The new rule to follow")
    
    list_parser = subparsers.add_parser("list", help="List learnings")
    list_parser.add_argument("--skill", help="Filter by skill name")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_learning(args.skill, args.worked, args.didnt, args.rule)
    elif args.command == "list":
        list_learnings(args.skill)

if __name__ == "__main__":
    main()
