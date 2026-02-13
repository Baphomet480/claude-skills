# Implementation Plan - Audit and standardize existing skills

## Phase 1: Automated Audit Tooling [checkpoint: 20c8c89]
Goal: Create a script to automatically check for compliance issues across all skills.

- [x] Task: Create `scripts/audit_skills.py` [37e9f1f]
    - [x] Sub-task: Write Tests: Create `tests/test_audit_skills.py` to test the auditor's logic (checking for `SKILL.md`, verifying frontmatter, checking directory structure).
    - [x] Sub-task: Implement Feature: Write the Python script to scan `skills/` and report violations (missing files, bad naming, missing frontmatter).
- [x] Task: Run audit and generate initial report [dbaf66c]
    - [x] Sub-task: Execute the script against the current codebase.
    - [x] Sub-task: Save the output to `conductor/tracks/audit_skills_20260213/audit_report_initial.md`.
- [ ] Task: Conductor - User Manual Verification 'Automated Audit Tooling' (Protocol in workflow.md)

## Phase 2: Standardization - Group A (Infrastructure & Setup) [checkpoint: 155f13e]
Goal: Fix issues in scaffolding and deployment skills.

- [x] Task: Standardize `cloudflare-pages` [910c82c]
    - [x] Sub-task: Write Tests: Create `tests/test_skill_structure.py` (generic test) that can verify a specific skill folder structure.
    - [x] Sub-task: Implement Feature: Fix `SKILL.md` frontmatter, move loose files to `references/` or `templates/` if needed, rename non-kebab files.
- [x] Task: Standardize `nextjs-tinacms` [1bc184c]
    - [x] Sub-task: Write Tests: Update generic test to include this skill.
    - [x] Sub-task: Implement Feature: Apply standard structure and naming.
- [x] Task: Standardize `hugo-sveltia-cms` [46b42dd]
    - [x] Sub-task: Write Tests: Update generic test to include this skill.
    - [x] Sub-task: Implement Feature: Apply standard structure and naming.
- [ ] Task: Conductor - User Manual Verification 'Standardization - Group A' (Protocol in workflow.md)

## Phase 3: Standardization - Group B (Design & Research)
Goal: Fix issues in design and research skills.

- [x] Task: Standardize `kitchen-sink-design-system` [a7e54c7]
    - [x] Sub-task: Write Tests: Update generic test.
    - [x] Sub-task: Implement Feature: Apply standard structure.
- [x] Task: Standardize `deep-research` [befa18b]
    - [x] Sub-task: Write Tests: Update generic test.
    - [x] Sub-task: Implement Feature: Apply standard structure.
- [ ] Task: Standardize `design-lookup`
    - [ ] Sub-task: Write Tests: Update generic test.
    - [ ] Sub-task: Implement Feature: Apply standard structure.
- [ ] Task: Standardize `pitolandia-visual-identity`
    - [ ] Sub-task: Write Tests: Update generic test.
    - [ ] Sub-task: Implement Feature: Apply standard structure.
- [ ] Task: Conductor - User Manual Verification 'Standardization - Group B' (Protocol in workflow.md)

## Phase 4: Final Validation
Goal: Ensure all skills are now compliant and the audit script passes cleanly.

- [ ] Task: Run final audit
    - [ ] Sub-task: Execute `scripts/audit_skills.py` again.
    - [ ] Sub-task: Verify zero violations.
- [ ] Task: Conductor - User Manual Verification 'Final Validation' (Protocol in workflow.md)
