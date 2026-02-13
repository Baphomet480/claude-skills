# Product Guidelines

## Documentation Style & Tone
- **Authoritative & Direct:** Instructions should be written in the imperative mood (e.g., "Create file," "Run command"). Avoid ambiguity or passive voice.
- **Concise:** Prioritize brevity. Provide exactly what the agent needs to know to execute the task without unnecessary fluff.
- **Context-Aware:** While direct, ensure instructions provide enough context so the agent understands the *intent* of the operation, not just the mechanical steps.

## File Structure & Naming Conventions
- **Root Requirement:** Every skill directory **MUST** contain a `SKILL.md` file at its root level.
- **Directory Layout:**
    - `references/`: Store deep technical documentation, checklists, and lookup tables here.
    - `templates/`: Place starter code, configuration files, and boilerplate that agents will copy into user projects.
    - `examples/`: Provide reference implementations or finished artifacts for demonstration.
    - `scripts/`: detailed scripts or executables (e.g., Python, Bash) that assist the skill's execution.
- **Naming:**
    - **Directories:** Use `kebab-case` for all skill names and subdirectories (e.g., `kitchen-sink-design-system`).
    - **Files:** Use `kebab-case` or `snake_case` consistently. Avoid spaces or special characters.

## `SKILL.md` Content Requirements
- **YAML Frontmatter:** The file must start with a YAML block defining metadata:
    ```yaml
    ---
    name: skill-name
    description: A brief summary of what the skill does.
    ---
    ```
- **Trigger Definition:** Clearly explicitly state the conditions under which the agent should activate the skill. Use phrases like "Use this skill when..." or "Trigger this skill if the user mentions...".
- **Instruction Body:**
    - Use clear Markdown headers to structure the guide.
    - Reference files in `templates/` or `references/` using relative paths.
    - Provide step-by-step procedural guidance for complex workflows.

## Version Control & Packaging
- **Git Hooks:** Respect the pre-commit hook mechanism. Do not manually edit files in `dist/`; these are auto-generated.
- **Atomic Commits:** When updating a skill, ensure related changes (docs + templates) are committed together to maintain consistency.
