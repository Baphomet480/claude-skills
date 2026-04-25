#!/usr/bin/env python3

import json
import os
import sys
import argparse
import subprocess

def get_project_root():
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        return root
    except Exception:
        return os.getcwd()

AGENT_DIR = os.path.join(get_project_root(), '.agent')
EVALS_DIR = os.path.join(AGENT_DIR, 'evals')

def add_eval(skill, criterion):
    os.makedirs(EVALS_DIR, exist_ok=True)
    eval_file = os.path.join(EVALS_DIR, f"{skill}.json")
    
    if os.path.exists(eval_file):
        with open(eval_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"skill": skill, "criteria": []}
        
    data["criteria"].append(criterion)
    
    with open(eval_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Added eval criterion for skill '{skill}'")

def list_evals(skill=None):
    if not os.path.exists(EVALS_DIR):
        print("No evals directory found.")
        return
        
    if skill:
        eval_file = os.path.join(EVALS_DIR, f"{skill}.json")
        if os.path.exists(eval_file):
            with open(eval_file, 'r') as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            print(f"No evals found for skill '{skill}'")
    else:
        for filename in os.listdir(EVALS_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(EVALS_DIR, filename), 'r') as f:
                    print(f"--- {filename} ---")
                    print(json.dumps(json.load(f), indent=2))

def main():
    parser = argparse.ArgumentParser(description="Agentic OS Evals Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    add_parser = subparsers.add_parser("add", help="Add a new eval criterion for a skill")
    add_parser.add_argument("--skill", required=True, help="The skill name")
    add_parser.add_argument("--criterion", required=True, help="The criterion to add")
    
    list_parser = subparsers.add_parser("list", help="List evals")
    list_parser.add_argument("--skill", help="Filter by skill name")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_eval(args.skill, args.criterion)
    elif args.command == "list":
        list_evals(args.skill)

if __name__ == "__main__":
    main()
