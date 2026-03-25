# Changelog

All notable changes to this engineering standards repository are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning 2.0.0](https://semver.org/)

---

## [Unreleased]

_Changes that are ready for review but not yet released._

---

## [1.0.0] — 2026-03-25

### Added — Initial Release

#### Universal Standards
- `universal/code-principles.md` — SOLID, DRY, KISS, YAGNI, Law of Demeter with real-world examples
- `universal/git-workflow.md` — Conventional Commits v1.0.0, SemVer, Gitflow vs TBD comparison
- `universal/code-review.md` — Google Eng Practices review standards, checklists, tone guidelines
- `universal/testing-strategy.md` — Test pyramid (70/20/10), FIRST properties, AAA pattern, corner cases
- `universal/security.md` — OWASP Top 10:2021, secrets management, injection prevention
- `universal/architecture.md` — Clean Architecture, Hexagonal Architecture, design patterns
- `universal/documentation.md` — Docstring standards, ADRs, CHANGELOG format
- `universal/performance.md` — Big-O awareness, profiling, caching strategy, SLOs
- `universal/naming-conventions.md` — Cross-language naming patterns, boolean prefixes, domain vocabulary

#### Language Style Guides
- `python/` — PEP 8, PEP 257, Google Python Style Guide, Black (88 char), Ruff, mypy strict
- `javascript/` — Airbnb Style Guide (100 char), Prettier, ESLint recommended, async patterns
- `typescript/` — TypeScript Handbook strict mode, Zod validation, exhaustive discriminated unions
- `java/` — Google Java Style Guide (100 char, 2-space indent), Effective Java patterns, Spring Boot
- `cpp/` — Google C++ Style Guide (80 char), C++ Core Guidelines, RAII, smart pointers
- `rust/` — Rust API Guidelines, rustfmt (100 char), thiserror, anyhow, Clippy pedantic
- `go/` — Effective Go, Google Go Style, Uber Go Style, gofmt, race detector
- `sql/` — GitLab SQL Style, dbt SQL Style, PostgreSQL best practices, schema design
- `swift/` — Apple API Design Guidelines, Google Swift Style, SwiftLint, async/await
- `kotlin/` — Kotlin Coding Conventions (120 char), Coroutines, Sealed classes, MockK
- `bash/` — Google Shell Style Guide (2-space, 80 char), set -euo pipefail, ShellCheck

#### AI Rules System
- `ai-rules/core/` — 16 concise (≤200 line) rule files, one per language/topic
- `ai-rules/adapters/cursor/` — `.mdc` files with YAML frontmatter for Cursor IDE
- `ai-rules/adapters/github-copilot/` — Merged `copilot-instructions.md` for GitHub Copilot
- `ai-rules/adapters/windsurf/` — Plain `.md` files for Windsurf
- `ai-rules/adapters/continue/` — `config.json` with systemMessage for Continue.dev
- `ai-rules/adapters/aider/` — `CONVENTIONS.md` for Aider (auto-loaded)
- `ai-rules/adapters/claude/` — `CLAUDE.md` for Claude projects (memory file)
- `sync-adapters.sh` — Script to regenerate all adapters from `core/` source files

#### Examples
- Python: `good_function.py`, `bad_function.py`, `test_example.py` (ProcessPaymentUseCase)
- JavaScript: `good_module.js`, `bad_module.js`, `test_example.test.js` (OrderService)
- TypeScript: `good_service.ts`, `bad_service.ts`, `test_example.spec.ts` (NotificationService)
- Bash: `good_script.sh`, `bad_script.sh` (deployment script)

#### Sources Consulted
- PEP 8 (Guido van Rossum), PEP 257 (Goodger & van Rossum)
- Google Python, Java, Go, C++, Swift Style Guides
- Airbnb JavaScript Style Guide
- TypeScript Official Handbook
- Rust API Guidelines + rustfmt
- Uber Go Style Guide
- Kotlin Coding Conventions (JetBrains)
- Apple Swift API Design Guidelines
- Conventional Commits v1.0.0 specification
- Semantic Versioning 2.0.0 specification
- OWASP Top 10:2021
- Google Engineering Practices (eng-practices)
- C++ Core Guidelines (Stroustrup + Sutter)
- "Effective Java" 3rd ed. (Bloch)
- "Clean Architecture" (Martin)
- GitLab SQL Style Guide, dbt SQL Style Guide

---

## Version Notes

- **MAJOR** version bumps when a rule fundamentally changes (e.g., switching line length recommendation)
- **MINOR** version bumps when a new language, tool adapter, or section is added
- **PATCH** version bumps for clarifications, typo fixes, and example improvements
