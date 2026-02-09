#!/usr/bin/env python3
"""
convert-toml-to-yaml.py
Convert TOML front matter (+++ delimiters) to YAML (--- delimiters) in Markdown files.

Usage:
  python3 convert-toml-to-yaml.py <content-directory>
  python3 convert-toml-to-yaml.py content/

Requirements:
  pip install toml pyyaml --break-system-packages
"""

import sys
import os
import re

try:
    import toml
    import yaml
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install toml pyyaml --break-system-packages")
    sys.exit(1)

TOML_PATTERN = re.compile(r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)', re.DOTALL)
YAML_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)


def convert_file(filepath):
    """Convert a single file from TOML to YAML front matter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already YAML
    if YAML_PATTERN.match(content):
        return 'skip_yaml'

    # Check if TOML
    match = TOML_PATTERN.match(content)
    if not match:
        return 'skip_none'

    toml_str = match.group(1)
    body = match.group(2)

    try:
        front_matter = toml.loads(toml_str)
    except Exception as e:
        return f'error_parse: {e}'

    yaml_str = yaml.dump(
        front_matter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write(yaml_str)
        f.write('---\n')
        f.write(body)

    return 'converted'


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <content-directory>")
        sys.exit(1)

    content_dir = sys.argv[1]
    if not os.path.isdir(content_dir):
        print(f"Error: {content_dir} is not a directory")
        sys.exit(1)

    stats = {'converted': 0, 'skip_yaml': 0, 'skip_none': 0, 'errors': 0}

    for root, _, files in os.walk(content_dir):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(root, filename)
            result = convert_file(filepath)

            if result == 'converted':
                stats['converted'] += 1
                print(f"  ✅ Converted: {filepath}")
            elif result == 'skip_yaml':
                stats['skip_yaml'] += 1
            elif result == 'skip_none':
                stats['skip_none'] += 1
            elif result.startswith('error'):
                stats['errors'] += 1
                print(f"  ❌ Error: {filepath} — {result}")

    print(f"\nDone!")
    print(f"  Converted:    {stats['converted']}")
    print(f"  Already YAML: {stats['skip_yaml']}")
    print(f"  No front matter: {stats['skip_none']}")
    print(f"  Errors:       {stats['errors']}")


if __name__ == '__main__':
    main()
