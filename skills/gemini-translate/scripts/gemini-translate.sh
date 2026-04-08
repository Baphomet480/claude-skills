#!/usr/bin/env bash
# gemini-translate.sh -- Batch-translate files using Gemini CLI as a subagent.
# Sends all files in a single gemini call with -o json, returns JSON array to stdout.
#
# Usage:
#   bash gemini-translate.sh [OPTIONS] FILE [FILE...]
#
# Options:
#   --source-lang LANG    Source language code (default: en)
#   --target-lang LANG    Target language code (default: es)
#   --glossary FILE       Path to glossary file with term mappings
#   --instructions TEXT   Additional style/tone instructions
#   --model MODEL         Gemini model override
#   --max-tokens N        Max estimated input tokens per batch (default: 80000)
#   --gemini-bin PATH     Path to gemini binary (bypasses wrapper detection)
#   --dry-run             Print prompt to stderr, do not call Gemini
#
# Exit codes: 0=success, 1=missing gemini, 2=no files, 3=gemini error

set -uo pipefail
# Note: -e intentionally omitted so we can handle gemini exit codes ourselves

# ── Defaults ──────────────────────────────────────────────────────────────────

SOURCE_LANG="en"
TARGET_LANG="es"
GLOSSARY_FILE=""
INSTRUCTIONS=""
MODEL_FLAG=""
MAX_TOKENS=80000
DRY_RUN=false
GEMINI_BIN=""
FILES=()

# ── Parse args ────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-lang) SOURCE_LANG="$2"; shift 2 ;;
    --target-lang) TARGET_LANG="$2"; shift 2 ;;
    --glossary)    GLOSSARY_FILE="$2"; shift 2 ;;
    --instructions) INSTRUCTIONS="$2"; shift 2 ;;
    --model)       MODEL_FLAG="-m $2"; shift 2 ;;
    --max-tokens)  MAX_TOKENS="$2"; shift 2 ;;
    --gemini-bin)  GEMINI_BIN="$2"; shift 2 ;;
    --dry-run)     DRY_RUN=true; shift ;;
    -*)            echo "Unknown option: $1" >&2; exit 2 ;;
    *)             FILES+=("$1"); shift ;;
  esac
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "Error: no input files provided." >&2
  echo "Usage: gemini-translate.sh [OPTIONS] FILE [FILE...]" >&2
  exit 2
fi

# ── Locate Gemini CLI ────────────────────────────────────────────────────────
# Many users wrap `gemini` in a shell alias that adds --yolo/-y. To avoid
# conflicts, we resolve the actual binary via pnpx. Override with --gemini-bin.

if [[ -n "$GEMINI_BIN" ]]; then
  GEMINI_CMD="$GEMINI_BIN"
elif command -v pnpx &>/dev/null; then
  GEMINI_CMD="pnpx @google/gemini-cli"
elif command -v gemini &>/dev/null; then
  GEMINI_CMD="gemini"
else
  echo "Error: gemini CLI not found. Install with: npm i -g @google/gemini-cli" >&2
  exit 1
fi

echo "Using: $GEMINI_CMD" >&2

# ── Build glossary section ────────────────────────────────────────────────────

GLOSSARY_SECTION=""
if [[ -n "$GLOSSARY_FILE" && -f "$GLOSSARY_FILE" ]]; then
  GLOSSARY_SECTION="
## Glossary (${SOURCE_LANG} -> ${TARGET_LANG})
Use these exact translations when you encounter these terms:

$(cat "$GLOSSARY_FILE")
"
fi

# ── Build file payloads with token budgeting ─────────────────────────────────
# Rough estimate: 1 token ~ 4 chars. We budget input tokens to leave room
# for output (translation is roughly 1.2x the input length for most pairs).

FILE_PAYLOADS=""
FILE_COUNT=0
TOTAL_CHARS=0
SKIPPED_FILES=()

for filepath in "${FILES[@]}"; do
  if [[ ! -f "$filepath" ]]; then
    echo "Warning: file not found, skipping: $filepath" >&2
    continue
  fi

  filename=$(basename "$filepath")
  content=$(cat "$filepath")
  file_chars=${#content}

  # Check if adding this file would exceed the token budget
  # 4 chars/token is a conservative estimate for English text
  estimated_tokens=$(( (TOTAL_CHARS + file_chars) / 4 ))
  if [[ $FILE_COUNT -gt 0 && $estimated_tokens -gt $MAX_TOKENS ]]; then
    SKIPPED_FILES+=("$filepath")
    continue
  fi

  FILE_PAYLOADS+="
--- FILE: ${filename} ---
${content}
--- END FILE ---
"
  FILE_COUNT=$((FILE_COUNT + 1))
  TOTAL_CHARS=$((TOTAL_CHARS + file_chars))
done

if [[ $FILE_COUNT -eq 0 ]]; then
  echo "Error: no valid files to translate." >&2
  exit 2
fi

if [[ ${#SKIPPED_FILES[@]} -gt 0 ]]; then
  echo "Warning: ${#SKIPPED_FILES[@]} files skipped (token budget ${MAX_TOKENS} reached at ${FILE_COUNT} files, ~$((TOTAL_CHARS / 4)) tokens)." >&2
  echo "Skipped files:" >&2
  printf '  %s\n' "${SKIPPED_FILES[@]}" >&2
fi

echo "Batch: ${FILE_COUNT} files, ~$((TOTAL_CHARS / 4)) estimated input tokens." >&2

# ── Build prompt ──────────────────────────────────────────────────────────────

PROMPT="You are a professional translator (${SOURCE_LANG} -> ${TARGET_LANG}).

## Task
Translate each file below from ${SOURCE_LANG} to ${TARGET_LANG}. Return your response as a JSON array.

## Output Format
Return ONLY a valid JSON array with no surrounding text, no markdown code fences, no explanation:
[
  {\"file\": \"filename.md\", \"translation\": \"full translated file content here\"},
  {\"file\": \"filename2.md\", \"translation\": \"full translated file content here\"}
]

The \"translation\" value must contain the COMPLETE translated file (frontmatter + body for markdown files, full JSON for JSON files). Escape newlines as \\n within the JSON string values.

## Rules
1. PRESERVE EXACTLY: all frontmatter keys, markdown formatting, links, HTML tags, image paths, URLs, file paths
2. NEVER TRANSLATE: brand names, proper nouns, personal names, credentials (MD, DO, CNM, PA-C, etc.), URLs, email addresses
3. Keep the same frontmatter structure (same keys, same nesting, same order)
4. For medical or domain-specific terms not in the glossary that you are uncertain about, wrap them in <!-- REVIEW: original term -->
5. Match the tone and register of the source document
${GLOSSARY_SECTION}
${INSTRUCTIONS:+
## Style Instructions
${INSTRUCTIONS}
}
## Files to Translate (${FILE_COUNT} files)
${FILE_PAYLOADS}"

# ── Dry run ───────────────────────────────────────────────────────────────────

if [[ "$DRY_RUN" == true ]]; then
  echo "=== DRY RUN: Prompt (${#PROMPT} chars, ~$((${#PROMPT} / 4)) tokens, ${FILE_COUNT} files) ===" >&2
  echo "$PROMPT" >&2
  echo "=== END DRY RUN ===" >&2
  exit 0
fi

# ── Call Gemini ───────────────────────────────────────────────────────────────
# Uses -o json for structured output envelope: {session_id, response, stats}

echo "Translating ${FILE_COUNT} files via Gemini CLI..." >&2

TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

# shellcheck disable=SC2086
$GEMINI_CMD -p "$PROMPT" -o json $MODEL_FLAG 2>/dev/null \
  | tr -d '\0' \
  | sed 's/^MCP issues detected[^{]*//' \
  > "$TMPFILE"

if [[ ! -s "$TMPFILE" ]]; then
  echo "Error: Gemini returned empty response." >&2
  exit 3
fi

# ── Extract translations from JSON ───────────────────────────────────────────
# Gemini -o json MAY wrap output as: {"session_id": "...", "response": "...", "stats": {...}}
# Or it may return the raw model output directly (depends on version/context).
# The parser handles both cases, plus markdown code fences and truncation.

python3 - "$TMPFILE" << 'PYEOF'
import json, sys

filepath = sys.argv[1]
with open(filepath) as f:
    raw = f.read().strip()

# Handle missing opening brace (null-byte stripping can eat it)
if raw and raw[0] not in ('{', '['):
    idx = raw.find('{')
    bracket_idx = raw.find('[')
    if bracket_idx >= 0 and (idx < 0 or bracket_idx < idx):
        idx = bracket_idx
    if idx >= 0:
        raw = raw[idx:]

def strip_fences(text):
    """Remove markdown code fences from text."""
    if "```json" in text:
        text = text.split("```json", 1)[1]
    elif "```" in text:
        text = text.split("```", 1)[1]
    if "```" in text:
        text = text.rsplit("```", 1)[0]
    return text.strip()

def try_parse_array(text):
    """Try to parse text as a JSON array, with truncation recovery.
    Uses raw_decode to handle trailing data (Gemini stats appended after the array)."""
    text = text.strip()
    decoder = json.JSONDecoder()

    # Direct parse with raw_decode (ignores trailing data)
    try:
        result, end = decoder.raw_decode(text)
        if isinstance(result, list):
            return result, False
    except json.JSONDecodeError:
        pass

    # Truncation recovery: trim from end to find valid JSON
    for trim in range(1, min(len(text), 15000)):
        candidate = text[:len(text) - trim].rstrip().rstrip(",")
        for suffix in ['"}]', '"]', "]"]:
            try:
                result, end = decoder.raw_decode(candidate + suffix)
                if isinstance(result, list) and len(result) > 0:
                    # Drop the last entry (likely truncated)
                    return result[:-1], True
            except json.JSONDecodeError:
                continue

    return None, False

# ── Try 1: Parse as Gemini JSON envelope ──────────────────────────────────
try:
    envelope = json.loads(raw)
    if isinstance(envelope, dict) and "response" in envelope:
        response = strip_fences(envelope["response"])
        result, truncated = try_parse_array(response)
        if result is not None:
            json.dump(result, sys.stdout, ensure_ascii=False)
            note = " (partial, output was truncated)" if truncated else ""
            print(f"Extracted {len(result)} translations{note}.", file=sys.stderr)
            sys.exit(0)
except json.JSONDecodeError:
    pass

# ── Try 2: Parse as raw JSON array (no envelope) ─────────────────────────
cleaned = strip_fences(raw)
result, truncated = try_parse_array(cleaned)
if result is not None:
    json.dump(result, sys.stdout, ensure_ascii=False)
    note = " (partial, output was truncated)" if truncated else ""
    print(f"Extracted {len(result)} translations{note}.", file=sys.stderr)
    sys.exit(0)

# ── Try 3: Find JSON array anywhere in the text ──────────────────────────
bracket_idx = raw.find("[")
if bracket_idx >= 0:
    result, truncated = try_parse_array(raw[bracket_idx:])
    if result is not None:
        json.dump(result, sys.stdout, ensure_ascii=False)
        note = " (partial, output was truncated)" if truncated else ""
        print(f"Extracted {len(result)} translations{note}.", file=sys.stderr)
        sys.exit(0)

print("Error: could not extract translation JSON from response.", file=sys.stderr)
print(f"Response length: {len(raw)} chars", file=sys.stderr)
print(f"Response start: {raw[:300]}", file=sys.stderr)
print(f"Response end: {raw[-300:]}", file=sys.stderr)
sys.exit(3)
PYEOF
