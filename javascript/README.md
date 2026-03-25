# JavaScript Standards

JavaScript is used for Node.js backend services, browser applications, serverless functions, and tooling. These standards apply to all JavaScript (non-TypeScript) code.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length (hard limit) | 100 characters | Airbnb Style Guide |
| Indentation | 2 spaces | Airbnb, Google JS Style Guide |
| Semicolons | Required | Airbnb Style Guide |
| Quotes | Single quotes (strings), backticks (templates) | Airbnb Style Guide |
| Max function length | 40 lines | Team convention |
| Max file length | 500 lines | Team convention |
| Max parameters | 4 (use options object if > 4) | Airbnb Style Guide |
| Arrow functions | Preferred over `function` expressions | Airbnb Style Guide |
| `var` | **Forbidden** — use `const` or `let` | ESLint `no-var` |
| Min test coverage | 80% business logic | Team convention |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full formatting and code rules |
| [architecture.md](architecture.md) | Module patterns, Node.js structure |
| [testing.md](testing.md) | Jest conventions, testing async code |
| [tooling.md](tooling.md) | ESLint, Prettier, package.json config |
| [async-patterns.md](async-patterns.md) | Promises, async/await, event emitters |
| [examples/](examples/) | Good and bad code examples |

## Tooling Summary

```bash
# Lint + format
npx eslint . --fix
npx prettier --write .

# Test
npx jest --coverage

# Type-check (if using JSDoc types)
npx tsc --noEmit --allowJs --checkJs
```
