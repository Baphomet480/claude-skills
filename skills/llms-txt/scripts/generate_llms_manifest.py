#!/usr/bin/env python3
import os
import argparse
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Deterministic LLMs-txt Manifest Generator")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--out", default="llms_manifest.json", help="Output manifest path")
    args = parser.parse_args()

    root = Path(args.root)
    manifest = {
        "project_name": root.resolve().name,
        "primary_docs": [],
        "content_files": [],
        "brand_guides": [],
        "structure": {}
    }

    # Common patterns
    doc_extensions = [".md", ".mdx", ".txt"]
    ignore_dirs = [".git", "node_modules", "dist", "build", ".next", ".astro"]

    for path in root.rglob("*"):
        if any(ignore in path.parts for ignore in ignore_dirs):
            continue
        
        if path.is_file():
            ext = path.suffix.lower()
            rel_path = str(path.relative_to(root))
            
            # Categorize
            if rel_path.lower() in ["readme.md", "claud.md", "gemini.md", "skill.md"]:
                manifest["brand_guides"].append(rel_path)
            elif ext in doc_extensions:
                manifest["content_files"].append(rel_path)
            
            # Map structure (top level only)
            if len(path.parts) <= 3:
                parent = str(path.parent)
                if parent not in manifest["structure"]:
                    manifest["structure"][parent] = []
                manifest["structure"][parent].append(path.name)

    # Extract snippet from README
    readme_path = root / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        first_para = content.split("\n\n")[0]
        manifest["summary_snippet"] = first_para

    with open(args.out, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ LLMs manifest generated.")
    print(f"Brand guides found: {len(manifest['brand_guides'])}")
    print(f"Content files found: {len(manifest['content_files'])}")
    print(f"Report saved to {args.out}. Use this to draft the llms.txt.")

if __name__ == "__main__":
    main()
