# Universal Engineering Standards

These documents apply to **every project, regardless of language or framework**. They define the cross-cutting principles that all engineers must follow when writing code, reviewing peers' work, managing git history, and designing systems.

## Contents

| File | Topic |
|------|-------|
| [code-principles.md](code-principles.md) | SOLID, DRY, KISS, YAGNI, Law of Demeter |
| [git-workflow.md](git-workflow.md) | Commits, branching, PRs, SemVer, merge strategies |
| [code-review.md](code-review.md) | Review process, checklists, tone guidelines |
| [testing-strategy.md](testing-strategy.md) | Test pyramid, unit/integration/E2E rules, coverage targets |
| [security.md](security.md) | OWASP Top 10, secrets management, input validation |
| [architecture.md](architecture.md) | Clean Architecture, Hexagonal, design patterns |
| [documentation.md](documentation.md) | Docstrings, READMEs, ADRs, changelog standards |
| [performance.md](performance.md) | Big-O awareness, profiling, optimization rules |
| [naming-conventions.md](naming-conventions.md) | Cross-language naming patterns and conventions |

## How To Use

1. **Every engineer reads** `code-principles.md` and `git-workflow.md` on day one.
2. **Tech leads enforce** `code-review.md` on every pull request.
3. **Architects reference** `architecture.md` for all design decisions.
4. **Security reviews** use `security.md` before every release.

These standards are enforced via the AI rules in `../ai-rules/` — deploy the appropriate adapter for your AI coding tool.
