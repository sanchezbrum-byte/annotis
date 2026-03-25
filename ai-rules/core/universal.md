# Universal Engineering Rules

> Single source of truth — applies to ALL languages and projects.
> Full reference: `universal/` directory.

---

## Commit Message Format (Conventional Commits v1.0.0)

```
<type>[(scope)]: <description>     ← max 72 chars; imperative mood
                                    ← blank line
[body]                              ← explains WHY, not WHAT
                                    ← blank line
[footer]                            ← Closes: #123, BREAKING CHANGE: ...
```

Types: `feat` `fix` `docs` `style` `refactor` `perf` `test` `chore` `ci` `build` `revert`

✅ `feat(auth): add OAuth2 PKCE flow for mobile clients`
✅ `fix(payment): prevent double-charge on network timeout retry`
❌ `fixed stuff` / `WIP` / `update` / `various fixes`

Breaking change: `feat!: remove deprecated /api/v1 endpoints`

---

## Corner Case Checklist

Before marking any task complete, verify test coverage for:

- [ ] `null` / `nil` / `None` / `undefined` inputs
- [ ] Empty collections (`[]`, `{}`, `""`)
- [ ] Single-element collections
- [ ] Boundary values: `0`, `1`, `max_int`, `min_int`, `-1`
- [ ] Very large inputs (10M+ items)
- [ ] Negative numbers where positive expected
- [ ] Unicode / non-ASCII / emoji inputs
- [ ] Whitespace-only strings
- [ ] Concurrent/parallel execution
- [ ] Network failure / timeout scenarios
- [ ] Partial failures in multi-step operations
- [ ] Idempotency (calling twice = same result)

---

## Code Quality Rules

### Never in commits:
- `print()`, `console.log()`, `fmt.Println()`, `println!()`, `System.out.println()` debug output
- Commented-out dead code (delete it — git history preserves it)
- TODO without `(author, date, ticket)` reference
- Hardcoded secrets, passwords, API keys, tokens

### Every new function requires:
- At least one test covering the happy path
- At least one test covering the primary error case
- Docstring/JSDoc/GoDoc for all public functions

---

## Security Rules (Non-Negotiable)

```
NEVER hardcode:
  - API keys / tokens
  - Database passwords
  - Private keys / certificates
  - OAuth client secrets

ALWAYS:
  - Use env vars or secret managers for secrets
  - Parameterize SQL queries (never string concatenation)
  - Validate inputs at the boundary (HTTP layer, CLI args)
  - Check authorization on every data access operation
```

---

## Performance Rules

- Always comment Big-O complexity for non-trivial algorithms
- Prefer O(n) or O(n log n) over O(n²) — explain if O(n²) is acceptable
- Avoid N+1 query patterns — load related data in one query
- No string concatenation in loops — use builders/join
- Profile before optimizing critical paths

---

## Architecture Rules

- Dependency direction: inward only (infrastructure → application → domain)
- No database calls in domain entities
- No HTTP calls in use cases (use port interfaces)
- No business logic in HTTP controllers
- Validate at the boundary; trust inside the boundary

---

## Code Review Requirements

- PR size: ≤ 400 lines changed (Google recommendation)
- All CI checks pass before requesting review
- No self-merges without at least 1 reviewer approval
- Blocking comments: `[blocking]` must be resolved before merge
- Non-blocking suggestions: `[nit]` author's discretion

---

## Testing Requirements

| Code Type | Min Coverage |
|-----------|-------------|
| Business logic | 80% line coverage |
| Critical paths (auth, payments, data integrity) | 100% |
| Infrastructure adapters | 60% |

Test naming: `<method>_<scenario>_<expected_behavior>`
