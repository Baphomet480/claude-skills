---
name: llms-txt
version: 2.0.0
description: "Script-First llms.txt generator. Uses a deterministic script to crawl the project structure, identify brand guides, and catalog content files. Provides a repo manifest for the agent to draft context-aware /llms.txt and /llms-full.txt files."
---

# LLMs.txt Generator

Generate `/llms.txt` and `/llms-full.txt` files for web projects following the llmstxt.org spec.

This workflow uses a **Script-First** approach: a crawler script handles the "labor" of mapping the repo structure and finding brand rules, leaving the agent to handle the "judgment" of writing the LLM-friendly context files.

## Usage

When asked to "generate llms.txt", "make the site AI-friendly", or "add llms-full.txt":

1. **Run the manifest script:**
   ```bash
   python3 ~/.agents/skills/llms-txt/scripts/generate_llms_manifest.py \
     --root "." \
     --out "llms_manifest.json"
   ```

2. **Read the manifest:**
   Load `llms_manifest.json` to see:
   - Discovered brand guides (README.md, GEMINI.md, etc.).
   - List of all content files (.md, .mdx, .txt).
   - High-level project structure and summary snippet.

3. **Draft Context Files:**
   Use the manifest to create the two required files:
   - `/public/llms.txt`: Brief summary, brand guardrails, and top-level links.
   - `/public/llms-full.txt`: Comprehensive manifest including all content links.

## File Standards

### llms.txt (The Brief)
- Start with a H1 title and brief description.
- **LLM Instructions section**: Explicit rules for how other agents should write for this project.
- **Top-level links**: Point to major sections (Docs, API, Components).

### llms-full.txt (The Full Record)
- List every public-facing content file identified in the manifest.
- Group by directory.
- Provide a 1-sentence description for each major section.

## Anti-patterns (The "Hot Take" List)
- **Agent labor:** Don't manually `ls -R` to find files; use the script.
- **Hallucinated links:** Only include files found in the deterministic manifest.
- **Vague descriptions:** Use the `summary_snippet` from the manifest to ground the project purpose.
