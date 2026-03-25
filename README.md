# Engineering Standards

> The canonical reference and AI coding assistant rules source for all projects.
> Covers 10 languages, 6 AI tools, and every major engineering discipline.

---

## AI Coding Assistant Bootstrap Prompt

When starting a new project that uses this repository as a submodule (mounted at `.standards/`), paste the following prompt at the beginning of your first AI session. Copy it verbatim — it tells the assistant how to load the standards and how to behave for the entire project.

````
You are a senior staff engineer working on this project. Before writing a single line of code, you must fully read and internalize all engineering standards from the `.standards/` folder (the `engineering-foundation` submodule) in this repository. Your behavior must be governed by those standards at all times.

## LOADING ORDER — read these files first, in this order:

1. `.standards/ai-rules/adapters/cursor/.cursor/rules/universal.mdc` — applies to everything, always
2. `.standards/ai-rules/adapters/cursor/.cursor/rules/git-workflow.mdc` — commit discipline
3. `.standards/ai-rules/adapters/cursor/.cursor/rules/architecture.mdc` — structural decisions
4. `.standards/ai-rules/adapters/cursor/.cursor/rules/testing.mdc` — test requirements
5. `.standards/ai-rules/adapters/cursor/.cursor/rules/security.mdc` — security rules
6. Then load the language-specific rule file for whatever language this task involves

## HARD RULES — never violate these regardless of what I ask:

- Every function you write must have at least one corresponding test
- Every commit message must follow Conventional Commits spec exactly
- No hardcoded secrets, credentials, or tokens — ever
- No `print()`, `console.log()`, or debug statements left in committed code
- No commented-out dead code in commits
- Every non-trivial algorithm must include a Big-O comment
- When you are about to write a function longer than the language's defined maximum, stop and refactor first
- Before marking any task complete, run through the corner case checklist in `testing.mdc`

## YOUR WORKFLOW for every task I give you:

1. Read the relevant `.mdc` rule files for the language(s) involved
2. Plan the implementation and state it briefly before writing code
3. Write code that complies 100% with the loaded standards
4. Write the required tests immediately after — not later
5. Propose the exact commit message(s) using Conventional Commits format
6. Flag any decision where two standards conflict or where a tradeoff exists

## HOW TO HANDLE AMBIGUITY:

- If a task is unclear, ask one clarifying question before proceeding
- If I ask you to do something that violates the standards, warn me explicitly with "⚠️ STANDARDS CONFLICT:" and explain the violation before proceeding
- If the standards folder is missing or unreadable, stop and tell me immediately — do not proceed without them

## CONTEXT ABOUT THIS PROJECT:

[Fill this in per project — e.g.: "This is a Python FastAPI backend service", or "This is an Android app in Kotlin", or "This is an n8n automation pipeline"]

The standards in `.standards/` are the non-negotiable foundation. They exist to be followed strictly, not as suggestions.
````

> **How to use:** Add this repository as a Git submodule at `.standards/` in every new project (`git submodule add git@github.com:sanchezbrum-byte/engineering-foundation.git .standards`). Then paste the prompt above at the start of each AI coding session, filling in the `CONTEXT ABOUT THIS PROJECT` section.

---

## Purpose

This repository is the **single source of truth** for engineering standards across all projects. It provides:

1. **Deep, sourced style guides** for 10+ programming languages
2. **Universal standards** for git workflow, testing, security, architecture, and code review
3. **AI tool adapters** that transform these standards into the format required by every major AI coding assistant — so your AI never writes code that violates your standards

Edit once in `ai-rules/core/`. Run `./sync-adapters.sh`. All six tool adapters update automatically.

---

## Supported AI Tools

| Tool | Adapter Location | How to Activate | Setup Command |
|------|-----------------|-----------------|---------------|
| **Cursor** | `ai-rules/adapters/cursor/.cursor/rules/` | Auto-loaded when `.cursor/rules/` exists in project | `cp -r ai-rules/adapters/cursor/.cursor /your/project/` |
| **GitHub Copilot** | `ai-rules/adapters/github-copilot/.github/copilot-instructions.md` | Auto-read from `.github/copilot-instructions.md` | `cp ai-rules/adapters/github-copilot/.github/copilot-instructions.md /your/project/.github/` |
| **Windsurf** | `ai-rules/adapters/windsurf/.windsurf/rules/` | Auto-loaded from `.windsurf/rules/` | `cp -r ai-rules/adapters/windsurf/.windsurf /your/project/` |
| **Continue.dev** | `ai-rules/adapters/continue/.continue/config.json` | Copy to `~/.continue/config.json` | `cp ai-rules/adapters/continue/.continue/config.json ~/.continue/config.json` |
| **Aider** | `ai-rules/adapters/aider/CONVENTIONS.md` | Auto-read from `CONVENTIONS.md` in repo root | `cp ai-rules/adapters/aider/CONVENTIONS.md /your/project/CONVENTIONS.md` |
| **Claude** | `ai-rules/adapters/claude/CLAUDE.md` | Place `CLAUDE.md` in project root | `cp ai-rules/adapters/claude/CLAUDE.md /your/project/CLAUDE.md` |

---

## Language Coverage

| Language | Version | Style Source | Folder |
|----------|---------|-------------|--------|
| **Python** | 3.11+ | PEP 8, PEP 257, Google Python Style Guide, Black | [python/](python/) |
| **JavaScript** | ES2024 | Airbnb Style Guide, Google JS Style Guide | [javascript/](javascript/) |
| **TypeScript** | 5.x | TypeScript Handbook, Airbnb TS ESLint | [typescript/](typescript/) |
| **Java** | 17+ | Google Java Style Guide, Effective Java (Bloch) | [java/](java/) |
| **C++** | C++20/23 | Google C++ Style Guide, C++ Core Guidelines | [cpp/](cpp/) |
| **Rust** | 1.77+ | Rust API Guidelines, rustfmt, Clippy | [rust/](rust/) |
| **Go** | 1.22+ | Effective Go, Google Go Style, Uber Go Style | [go/](go/) |
| **SQL** | PostgreSQL 16 | GitLab SQL Style, dbt SQL Style Guide | [sql/](sql/) |
| **Swift** | 5.10+ | Apple API Design Guidelines, Google Swift Style | [swift/](swift/) |
| **Kotlin** | 2.0+ | Kotlin Coding Conventions, Android Kotlin Style | [kotlin/](kotlin/) |
| **Bash** | bash 5.x | Google Shell Style Guide, ShellCheck | [bash/](bash/) |

---

## Universal Standards

| Topic | File |
|-------|------|
| Code Principles (SOLID, DRY, KISS, YAGNI) | [universal/code-principles.md](universal/code-principles.md) |
| Git Workflow (Conventional Commits, SemVer, Branching) | [universal/git-workflow.md](universal/git-workflow.md) |
| Code Review (Process, Checklists, Tone) | [universal/code-review.md](universal/code-review.md) |
| Testing Strategy (Pyramid, Coverage, Mocking) | [universal/testing-strategy.md](universal/testing-strategy.md) |
| Security (OWASP Top 10, Secrets, Auth) | [universal/security.md](universal/security.md) |
| Architecture (Clean Arch, Hexagonal, SOLID) | [universal/architecture.md](universal/architecture.md) |
| Documentation (Docstrings, ADRs, CHANGELOG) | [universal/documentation.md](universal/documentation.md) |
| Performance (Big-O, Profiling, Caching) | [universal/performance.md](universal/performance.md) |
| Naming Conventions (Cross-language) | [universal/naming-conventions.md](universal/naming-conventions.md) |

---

## Key Numeric Rules Quick Reference

| Language | Max Line Length | Indent | Max Fn Lines | Max Params | Min Coverage |
|----------|----------------|--------|-------------|-----------|-------------|
| Python | 88 chars (Black) | 4 spaces | 50 lines | 5 | 80% business |
| JavaScript | 100 chars (Airbnb) | 2 spaces | 40 lines | 4 | 80% |
| TypeScript | 100 chars | 2 spaces | 40 lines | 4 | 80% |
| Java | 100 chars (Google) | 2 spaces | 40 lines | 4 (Builder) | 80% |
| C++ | 80 chars (Google) | 2 spaces | 50 lines | — | 80% |
| Rust | 100 chars (rustfmt) | 4 spaces | 50 lines | — | 80% |
| Go | ~100 chars (soft) | tabs | 40 lines | — | 80% |
| SQL | 120 chars (soft) | 4 spaces | — | — | — |
| Swift | 100 chars | 2 spaces | 40 lines | — | 80% |
| Kotlin | 120 chars | 4 spaces | 40 lines | — | 80% |
| Bash | 80 chars | 2 spaces | 40 lines | — | — |

---

## How to Update Standards

1. **Edit the core file:** `ai-rules/core/<language>.md` (or a universal file)
2. **Run the sync script:** `./sync-adapters.sh`
3. **Verify adapters:** check that the relevant adapter files were updated
4. **Update detailed guides:** update `<language>/style-guide.md` if needed
5. **Submit a PR:** follow the commit convention; PR description must include the rationale for the change

**Never edit adapter files directly** — they are regenerated on every `sync-adapters.sh` run.

---

## Review Cadence

| Review Type | Frequency | Owner |
|-------------|-----------|-------|
| Full standards review | **Quarterly** | Tech Lead / Staff Engineer |
| New tool/framework additions | **As needed** | Proposing engineer |
| Security rule updates | **After any CVE or incident** | Security team |
| Language version updates | **After LTS release** | Tech Lead |

---

## Repository Structure

```
engineering-standards/
├── README.md                     ← You are here
├── CONTRIBUTING.md
├── CHANGELOG.md
├── sync-adapters.sh              ← Regenerates all adapter files
│
├── ai-rules/
│   ├── README.md                 ← Adapter system documentation
│   ├── core/                     ← SOURCE OF TRUTH (edit these)
│   └── adapters/                 ← Generated — do not edit directly
│       ├── cursor/
│       ├── github-copilot/
│       ├── windsurf/
│       ├── continue/
│       ├── aider/
│       └── claude/
│
├── universal/                    ← Deep guides for cross-cutting concerns
├── python/                       ← Python style guides + examples
├── javascript/                   ← JavaScript style guides + examples
├── typescript/                   ← TypeScript style guides + examples
├── java/                         ← Java style guides + examples
├── cpp/                          ← C++ style guides + examples
├── rust/                         ← Rust style guides + examples
├── go/                           ← Go style guides + examples
├── sql/                          ← SQL style guides + examples
├── swift/                        ← Swift style guides + examples
├── kotlin/                       ← Kotlin style guides + examples
└── bash/                         ← Bash style guides + examples
```

---

## Quick Start for a New Project

```bash
# 1. Clone this repo
git clone git@github.com:your-org/engineering-standards.git

# 2. Copy the adapter(s) for your AI tool(s) to your project
# Cursor:
cp -r engineering-standards/ai-rules/adapters/cursor/.cursor /your/project/
# GitHub Copilot:
cp engineering-standards/ai-rules/adapters/github-copilot/.github/copilot-instructions.md /your/project/.github/
# Aider:
cp engineering-standards/ai-rules/adapters/aider/CONVENTIONS.md /your/project/

# 3. Done — your AI tool now applies these standards automatically
```
