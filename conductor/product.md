# Product Definition

## Vision
To build and maintain a robust, portable library of AI agent skills that empower both developers and end-users to enhance their agentic workflows. The repository serves as a centralized source of truth for high-quality, framework-agnostic instructions and templates, ensuring seamless interoperability across different agent runtimes like Claude and Gemini.

## Target Audience
- **AI Agent Developers:** Individuals creating, refining, and extending the capabilities of AI agents through new skills.
- **AI Agent Users:** Developers and integrators who consume and install these skills to accelerate their specific project workflows.
- **Repository Maintainers:** Contributors responsible for the infrastructure, packaging, and distribution standards of the skill library.

## Core Goals
- **High-Quality Collection:** Curate and maintain a set of production-ready, reliable skills for common software engineering and creative tasks.
- **Cross-Compatibility:** Ensure all skills are designed to work seamlessly across different agent environments (e.g., Claude, Gemini) without platform-specific lock-in.

## Key Features & Mechanisms
- **Modular Architecture:** Each skill exists as a strictly self-contained directory with its own documentation and assets, ensuring no brittle inter-dependencies.
- **Automated Packaging:** Utilizes git hooks to automatically package source directories into distributable archives, removing manual release overhead.
- **Universal Compatibility:** Content, templates, and instructions are authored to be universally understandable and executable by various LLM-based agents.

## Success Criteria
- **Comprehensive Documentation:** Every skill must include a detailed `SKILL.md`, checklist references, and clear, unambiguous instructions.
- **Framework Agnosticism:** Skills should focus on high-level logic and workflows, avoiding strict dependencies on specific tool versions unless absolutely necessary for the skill's specific function.

## Primary Usage Scenarios
- **Project Scaffolding:** Bootstrapping new applications (e.g., Next.js + TinaCMS) with best-practice configurations and file structures.
- **Specialized Workflows:** Executing complex, multi-step tasks such as design system generation, deep research, or brand identity creation.
