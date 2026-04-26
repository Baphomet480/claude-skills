#!/usr/bin/env python3
import os
import re
import json
import argparse
from pathlib import Path

def detect_framework(root):
    if (root / "next.config.js").exists() or (root / "next.config.ts").exists():
        return "Next.js"
    if (root / "astro.config.mjs").exists() or (root / "astro.config.ts").exists():
        return "Astro"
    if (root / "nuxt.config.js").exists() or (root / "nuxt.config.ts").exists():
        return "Nuxt"
    if (root / "svelte.config.js").exists():
        return "SvelteKit"
    return "Static/Unknown"

def find_components(root):
    component_dirs = ["components", "src/components", "app/components"]
    found = []
    for d in component_dirs:
        path = root / d
        if path.exists():
            for ext in ["*.tsx", "*.jsx", "*.astro", "*.vue", "*.svelte"]:
                found.extend([str(p.relative_to(root)) for p in path.glob(f"**/{ext}")])
    return found

def audit_drift(root, files):
    # Patterns for drift
    hex_pattern = re.compile(r'#(?:[0-9a-fA-F]{3}){1,2}\b')
    arbitrary_tw = re.compile(r'-\[.*?\]') # e.g., w-[37px]
    
    report = {}
    for f in files:
        file_path = root / f
        try:
            content = file_path.read_text()
            hex_matches = hex_pattern.findall(content)
            tw_matches = arbitrary_tw.findall(content)
            
            if hex_matches or tw_matches:
                report[f] = {
                    "hardcoded_hex": list(set(hex_matches)),
                    "arbitrary_tailwind": list(set(tw_matches))
                }
        except Exception:
            continue
    return report

def main():
    parser = argparse.ArgumentParser(description="Deterministic Design System Auditor")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--out", default="design_audit.json", help="Output report path")
    args = parser.parse_args()

    root = Path(args.root)
    
    results = {
        "framework": detect_framework(root),
        "inventory": {
            "components": find_components(root),
        },
        "audit": {
            "drift": audit_drift(root, find_components(root))
        },
        "checklist_gap": []
    }
    
    # Simple check against Tier 1 Primitives
    tier1 = ["Button", "Card", "Input", "Badge", "Avatar", "Alert"]
    found_names = [Path(f).stem.lower() for f in results["inventory"]["components"]]
    for t in tier1:
        if t.lower() not in found_names:
            results["checklist_gap"].append(t)

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Design system audit complete.")
    print(f"Framework: {results['framework']}")
    print(f"Components found: {len(results['inventory']['components'])}")
    print(f"Drift detected in {len(results['audit']['drift'])} files.")
    print(f"Missing Tier 1 primitives: {', '.join(results['checklist_gap']) if results['checklist_gap'] else 'None'}")
    print(f"\nReport saved to {args.out}. Read this file to judge the next steps.")

if __name__ == "__main__":
    main()
