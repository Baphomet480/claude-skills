---
name: familysearch
description: FamilySearch API — person lookup, pedigree trees, record search, sources, and memories.
---

# FamilySearch Skill

Read-only access to the FamilySearch Family Tree and historical records. Two tools working together:

| Tool | Install | Purpose |
|------|---------|---------|
| **getmyancestors** | `pip install getmyancestors` | Download full GEDCOM trees (ancestors + descendants + spouses). Uses your regular FamilySearch login. |
| **familysearch.py** | `pip install httpx` | JSON API queries: person lookup, search, sources, memories, relationship paths. |

> **No developer account required.** `getmyancestors` ships a pre-registered client ID, so you authenticate with your normal FamilySearch username and password. The custom `familysearch.py` script reuses the same approach.

## Setup

### Install

```bash
# CLI tool — install with pipx
pipx install getmyancestors

# Library dependency for familysearch.py
pip install httpx
```

### Authenticate (familysearch.py)

```bash
# Prompts for username and password (password is hidden)
python3 scripts/familysearch.py auth

# Or pass credentials directly
python3 scripts/familysearch.py auth -u USERNAME -p PASSWORD
```

Logs in programmatically (same as getmyancestors) and saves an OAuth2 token to `~/.familysearch/token.json`.

### Verify

```bash
python3 scripts/familysearch.py verify
```

---

## GEDCOM Export (getmyancestors)

The fastest way to grab a full family tree as a GEDCOM file. Ideal for updating a project's master GEDCOM.

### Download Ancestors

```bash
# 4 generations of ancestors (default), outputs to stdout
getmyancestors -u USERNAME -p PASSWORD

# 6 generations, save to file, verbose log
getmyancestors -u USERNAME -p PASSWORD -a 6 -o tree.ged -l tree.log -v

# Start from a specific person instead of the tree root
getmyancestors -u USERNAME -p PASSWORD -i KWCJ-RN4 -o tree.ged -v
```

### Download Ancestors + Descendants + Spouses

```bash
# 6 gen ancestors + 2 gen descendants, include spouse/marriage data
getmyancestors -u USERNAME -p PASSWORD -a 6 -d 2 -m -o tree.ged -v

# Multiple starting individuals
getmyancestors -u USERNAME -p PASSWORD -i L4S5-9X4 LHWG-18F -a 6 -d 2 -m -o tree.ged
```

### Merge GEDCOM Files

```bash
mergemyancestors -i old-tree.ged new-additions.ged -o merged.ged
```

### Rate Limiting

```bash
# Limit to 5 requests/second (be respectful)
getmyancestors -u USERNAME -p PASSWORD --rate-limit 5 -o tree.ged -v
```

---

## Person (familysearch.py)

Look up individuals by their person ID (format: `XXXX-XXX`).

### Get a Person

```bash
# Full person record with names, gender, facts (birth, death, etc.)
python3 scripts/familysearch.py get-person --pid KWCJ-RN4

# Get the currently authenticated user's tree person
python3 scripts/familysearch.py get-current-user
```

### Get Person with Relationships

```bash
# Person + their immediate family connections
python3 scripts/familysearch.py get-person --pid KWCJ-RN4 --relationships
```

---

## Pedigree (familysearch.py)

### Ancestry (Ascending)

```bash
# Default 4 generations of ancestors (JSON, not GEDCOM)
python3 scripts/familysearch.py ancestry --pid KWCJ-RN4

# Up to 8 generations
python3 scripts/familysearch.py ancestry --pid KWCJ-RN4 --generations 8
```

### Descendancy (Descending)

```bash
python3 scripts/familysearch.py descendancy --pid KWCJ-RN4 --generations 4
```

---

## Search (familysearch.py)

### Search Persons in the Tree

```bash
# Search by name
python3 scripts/familysearch.py search --name "George Goodman"

# Search with date and place filters
python3 scripts/familysearch.py search \
  --name "George Goodman" \
  --birth-year 1870 \
  --birth-place "Arizona"

# Search with death info
python3 scripts/familysearch.py search \
  --name "Clara Platt" \
  --death-year 1961 \
  --death-place "Mesa, Arizona"

# Limit results
python3 scripts/familysearch.py search --name "Hofstätter" --limit 5
```

### Match Hints (Research Hints)

```bash
# Get potential record matches for a person already in the tree
python3 scripts/familysearch.py match --pid KWCJ-RN4
```

---

## Sources (familysearch.py)

### List Sources for a Person

```bash
python3 scripts/familysearch.py sources --pid KWCJ-RN4
```

### Search Historical Records

```bash
python3 scripts/familysearch.py search-records \
  --name "George Nicholas Goodman" \
  --birth-year 1870
```

---

## Memories (familysearch.py)

### List Memories for a Person

```bash
python3 scripts/familysearch.py memories --pid KWCJ-RN4
```

### Download a Memory

```bash
python3 scripts/familysearch.py download-memory \
  --url "https://familysearch.org/photos/artifacts/12345" \
  --output ./downloads/photo.jpg
```

---

## Relationships (familysearch.py)

### Direct Family

```bash
python3 scripts/familysearch.py parents --pid KWCJ-RN4
python3 scripts/familysearch.py spouses --pid KWCJ-RN4
python3 scripts/familysearch.py children --pid KWCJ-RN4
```

### Relationship Path

```bash
# How are two people related?
python3 scripts/familysearch.py relationship-path \
  --from KWCJ-RN4 --to XXXX-YYY
```

---

## Export (familysearch.py)

### Export Person Subtree as JSON

```bash
# Export a person and their immediate network as structured JSON
python3 scripts/familysearch.py export-person --pid KWCJ-RN4 --output ./research/person-export.json

# Include N generations of ancestors in the export
python3 scripts/familysearch.py export-person --pid KWCJ-RN4 --ancestors 4 --output ./research/tree-export.json
```

This produces a JSON file compatible with the Goodman history project's `parse-gedcom.mjs` output shape (individuals + families + relationships).

---

## JSON Output

All `familysearch.py` commands produce JSON to stdout. Pipe to `jq` for filtering:

```bash
# Get just the display name
python3 scripts/familysearch.py get-person --pid KWCJ-RN4 | jq '.display.name'

# Get all ancestor birth places
python3 scripts/familysearch.py ancestry --pid KWCJ-RN4 --generations 4 \
  | jq '[.persons[].facts[]? | select(.type == "http://gedcomx.org/Birth") | .place.original]'
```

## When to Use Which Tool

| Goal | Tool |
|------|------|
| Download a full family tree as GEDCOM | `getmyancestors` |
| Update your project's master GEDCOM file | `getmyancestors` |
| Look up a specific person by ID | `familysearch.py get-person` |
| Search for people by name/date/place | `familysearch.py search` |
| Find attached sources or record hints | `familysearch.py sources` / `match` |
| Download photos and documents | `familysearch.py memories` / `download-memory` |
| Get JSON-formatted pedigree data | `familysearch.py ancestry` / `descendancy` |
| Find how two people are related | `familysearch.py relationship-path` |

## Safety Guidelines

1. This skill is **read-only**. No write operations against the Family Tree.
2. FamilySearch rate limits API requests. Both tools include automatic retry with backoff.
3. Tokens expire after 2 hours. `familysearch.py` auto-refreshes using the stored refresh token.
4. Use `--rate-limit` with `getmyancestors` to be respectful of FamilySearch servers.
