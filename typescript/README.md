# TypeScript Standards

TypeScript is the default language for all frontend (React, Vue) and backend (Node.js) projects. JavaScript is used only for simple scripts or legacy projects.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length (hard limit) | 100 characters | Airbnb + Google |
| Indentation | 2 spaces | Airbnb, Google |
| Strict mode | Required (`"strict": true`) | TypeScript Handbook |
| `any` type | **Forbidden** — use `unknown` or proper types | TypeScript team guidance |
| `as` type assertions | Avoid; use type guards or `satisfies` | TypeScript best practices |
| `!` non-null assertions | Avoid; use optional chaining `?.` | TypeScript best practices |
| `enum` | Prefer `const` objects + `typeof` | Matt Pocock (Total TypeScript) |
| Max parameters | 4 (use interface for options if > 4) | Team convention |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full TypeScript formatting and code rules |
| [type-safety.md](type-safety.md) | Advanced type patterns, generics, narrowing |
| [architecture.md](architecture.md) | Project structure, module patterns |
| [testing.md](testing.md) | Jest + TypeScript, type-safe tests |
| [tooling.md](tooling.md) | tsconfig, ESLint + TypeScript, Prettier |
| [examples/](examples/) | Good and bad TypeScript examples |

## Tooling Summary

```bash
npx tsc --noEmit          # type check
npx eslint . --fix        # lint
npx prettier --write .    # format
npx jest --coverage       # test
```
