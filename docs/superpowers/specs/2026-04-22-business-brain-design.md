# Design: `business-brain` Skill

**Status:** Draft
**Date:** 2026-04-22

## 1. Goal
Implement the "Business Brain Pattern" as a reusable AI agent skill. This skill will provide a standardized way for other skills (or the agent itself) to query shared brand context—such as brand voice, audience profiles, product positioning, and content rules—without bloating the context window of every individual task.

## 2. Architecture
Following "Pattern 2" from the MindStudio blog post, we will create a dedicated skill that acts as an on-demand context provider.

- **Skill Name:** `business-brain`
- **Trigger:** "get brand context", "what is our brand voice", "query the business brain", "load audience profiles"
- **Functionality:** 
  1. The skill will define a standard directory structure (`.claude/brain/` or `.gemini/brain/`) for storing modular markdown files (`brand-voice.md`, `audience-profiles.md`, etc.).
  2. The skill will provide instructions to the agent on how to read only the requested piece of context when a specific task requires it, avoiding loading the entire brain.
  3. Provide an initialization script to scaffold the `brain/` directory with template files for new projects.

## 3. Directory Structure
```text
skills/business-brain/
├── SKILL.md
└── scripts/
    └── init-brain.sh (scaffolds the brain/ directory with templates)
```

## 4. SKILL.md Contents
- **Instructions:** Tell the agent to act as a router. When asked for brand context, it should look in the project's `brain/` directory and use the `read_file` tool to load only the specific markdown files requested (e.g., `brand-voice.md` for a social media post, `content-rules.md` for a blog).
- **Setup:** Instructions on how the user can run `init-brain.sh` to get started.

## 5. Validation Plan
- Run `python3 scripts/audit_skills.py skills` to ensure compliance.
- Run `./scripts/install-skills.sh` to link the new skill.
