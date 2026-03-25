# Git Workflow Standards

> **Source:** Conventional Commits v1.0.0, Google Engineering Practices, Gitflow (Driessen 2010), Trunk-Based Development (Paul Hammant), Semantic Versioning 2.0.0

---

## 1. Conventional Commits — Full Specification

Every commit message MUST follow this format (Conventional Commits v1.0.0):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | When to Use | SemVer Impact |
|------|-------------|---------------|
| `feat` | New feature added | MINOR bump |
| `fix` | Bug fix | PATCH bump |
| `docs` | Documentation only | None |
| `style` | Formatting, whitespace — no logic change | None |
| `refactor` | Code restructure — no feature or fix | None |
| `perf` | Performance improvement | PATCH bump |
| `test` | Adding or correcting tests | None |
| `chore` | Build process, dependency updates, tooling | None |
| `ci` | CI/CD configuration changes | None |
| `build` | Build system or external dependency changes | None |
| `revert` | Reverts a previous commit | Depends |

**BREAKING CHANGE** (MAJOR bump): Add `!` after type/scope, or add `BREAKING CHANGE:` footer.

### Complete Examples

```
feat(auth): add OAuth2 PKCE flow for mobile clients

Replaces the implicit flow which is deprecated per RFC 8252.
Mobile apps must now use the /oauth/token endpoint.

BREAKING CHANGE: The /oauth/authorize implicit flow endpoint is removed.
Clients must upgrade to the authorization code + PKCE flow.
Refs: AUTH-2847
```

```
fix(payment): prevent double-charge on network timeout retry

The payment processor was being called twice when the client
timed out and retried. Added idempotency key per Stripe best
practices to prevent duplicate charges.

Closes: #1492
```

```
feat(api): add pagination to /users endpoint
```

```
docs: update README with Docker Compose setup instructions
```

```
refactor(cache): replace redis client with ioredis for connection pooling
```

```
test(auth): add edge cases for expired JWT token validation
```

```
chore(deps): bump axios from 1.6.0 to 1.7.2
```

```
ci: add GitHub Actions workflow for automated security scanning
```

### Commit Message Rules

1. **Subject line**: imperative mood ("add feature", not "added feature" or "adding feature")
2. **Subject line**: max **72 characters** — enforced by commitlint
3. **Subject line**: no period at the end
4. **Body**: separated by a blank line from subject
5. **Body**: explain **WHY**, not WHAT. The diff shows what; the message must explain why.
6. **Body**: wrap at **72 characters** per line
7. **Footer**: `Closes: #123`, `Refs: JIRA-456`, `BREAKING CHANGE: description`

### ❌ Bad Commit Messages

```
fixed stuff
WIP
update
various fixes and improvements
asdfgh
changed the thing that was broken
```

### ✅ Good Commit Messages

```
fix(cache): evict stale entries after TTL expiry, not on read

The previous implementation only evicted entries when they were
read, causing stale data to persist for frequently-accessed keys.
This caused the pricing service to serve outdated prices for up
to 24 hours. Now entries are evicted eagerly via a background job.

Closes: #983
```

---

## 2. Branch Naming Conventions

```
<prefix>/<ticket-or-issue>-<short-description>
```

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feat/` | New feature development | `feat/AUTH-123-oauth2-pkce` |
| `fix/` | Bug fix | `fix/PAY-456-double-charge-on-retry` |
| `hotfix/` | Critical production fix | `hotfix/PAY-789-null-pointer-checkout` |
| `release/` | Release preparation | `release/v2.4.0` |
| `chore/` | Maintenance, tooling | `chore/update-node-18` |
| `docs/` | Documentation only | `docs/api-authentication-guide` |
| `refactor/` | Refactoring | `refactor/extract-payment-service` |
| `experiment/` | Spikes, proof of concepts | `experiment/graphql-federation` |

**Rules:**
- Use lowercase and hyphens only (no underscores, no spaces)
- Include ticket/issue number when applicable
- Keep description brief but meaningful (3–5 words max)
- Delete branches after merging

---

## 3. Semantic Versioning (SemVer 2.0.0)

Format: `MAJOR.MINOR.PATCH[-prerelease][+build]`

| Version Component | When to Increment | Example Trigger |
|-------------------|-------------------|-----------------|
| **MAJOR** | Breaking, backward-incompatible change | Removed API endpoint, changed return type |
| **MINOR** | New backward-compatible feature | Added new API endpoint, new optional param |
| **PATCH** | Backward-compatible bug fix | Fixed off-by-one error, fixed null pointer |

**Pre-release suffixes:** `1.0.0-alpha.1`, `1.0.0-beta.3`, `1.0.0-rc.1`

**Rules:**
- Start at `0.1.0` for initial development; `1.0.0` when API is public and stable
- Once a version is released, its contents MUST NOT change — create a new release
- MAJOR version zero (`0.y.z`) is for initial development; anything may change at any time
- Monotonically increasing — never decrement any component

### Git Tagging

```bash
git tag -a v2.4.0 -m "release: version 2.4.0 — adds OAuth2 PKCE flow"
git push origin v2.4.0
```

Always use annotated tags (`-a`), never lightweight tags for releases.

---

## 4. Gitflow vs Trunk-Based Development

### Gitflow

**When to use:** Projects with scheduled release cycles, multiple supported versions, compliance-heavy environments (regulated industries, enterprise software shipped quarterly).

**Branch model:**
```
main           ←── protected; only release commits
develop        ←── integration branch; nightly builds
feature/*      ←── branch off develop, merge to develop
release/*      ←── branch off develop, merge to main + develop
hotfix/*       ←── branch off main, merge to main + develop
```

**Pros:** Clear separation of concerns, supports multiple parallel releases, audit trail  
**Cons:** Complex, slow feedback loops, merge conflicts accumulate, discourages CI/CD

### Trunk-Based Development (TBD)

**When to use:** Teams practicing continuous delivery, microservices, SaaS products with frequent deploys (Google, Facebook, Netflix, Etsy all use TBD).

**Branch model:**
```
main  ←── the trunk; every engineer merges here daily
feat/* ←── short-lived (< 2 days); merge to main via PR
```

**Key practices:**
- Feature flags control feature visibility, not branches
- Every commit to `main` is production-releasable
- CI must pass before merge (no broken trunk rule)
- Pair programming or small PRs reviewed within hours, not days

**Pros:** Fast feedback, less merge conflict, encourages CI/CD discipline  
**Cons:** Requires mature CI/CD, feature flags infrastructure, engineering discipline

**Recommendation:** Default to TBD for new projects. Use Gitflow only when you have contractual release cycles or must support multiple major versions simultaneously.

---

## 5. Pull Request / Merge Request Standards

### PR Size Limit

**Maximum 400 lines changed per PR** — this is Google's recommended limit and is backed by data: reviewers become less effective at catching bugs above 400 LOC. Aim for ≤ 200 lines for complex logic.

If a feature requires more changes:
1. Split into a stack of dependent PRs
2. Use feature flags to ship code dark
3. Separate refactoring PRs from behavior-change PRs

### PR Description Template

```markdown
## What

[One paragraph: what changed and why]

## How

[Key technical decisions made. Link to relevant design docs or ADRs]

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing done (describe steps)

## Checklist

- [ ] No debug logs, print statements, or commented-out code
- [ ] No hardcoded secrets or credentials
- [ ] Breaking changes documented in BREAKING_CHANGES.md (if applicable)
- [ ] CHANGELOG.md updated (for public-facing changes)

## Related

Closes: #<issue>
Refs: <JIRA ticket>
```

### PR Author Rules

1. Self-review before requesting review — read your own diff as a reviewer
2. Respond to all review comments before re-requesting review
3. Do not force-push to a PR branch after review has started (unless rebasing for conflicts)
4. Delete the branch after merge

### Reviewer Rules

1. **First response within 1 business day** — acknowledge receipt even if you can't review fully
2. Distinguish blocking comments from non-blocking suggestions:
   - `[blocking]` — must fix before merge
   - `[nit]` — minor style; author's discretion
   - `[question]` — curious, not blocking
3. Approve when the code is good enough — not when it is perfect
4. Never block on purely stylistic issues covered by linters/formatters

---

## 6. Merge Strategies

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Merge commit** | Gitflow; preserving full history; merging release branches | Full history; reverts are easy | Noisy history; mainline has merge commits |
| **Squash and merge** | Feature branches; keeping mainline clean | Linear, clean history; one commit per feature | Loses granular commit history |
| **Rebase and merge** | Small PRs; when linear history is critical | Fully linear history; atomic commits | Rewrites commit hashes; can confuse contributors |

**Recommendation:** Default to **squash and merge** for feature branches into `main`. Use **merge commit** for release/hotfix branches. Never rebase public branches.

---

## 7. What NEVER to Commit

The following MUST be in `.gitignore` and MUST NEVER appear in a commit:

| Category | Examples |
|----------|----------|
| Secrets & credentials | API keys, passwords, tokens, private keys, `.env` files with real values |
| Build artifacts | `dist/`, `build/`, `*.class`, `*.pyc`, `__pycache__/`, `target/` |
| Dependencies | `node_modules/`, `vendor/`, `.venv/`, virtual environments |
| IDE/OS files | `.DS_Store`, `Thumbs.db`, `.idea/`, `.vscode/` (unless sharing settings intentionally) |
| Compiled binaries | `*.exe`, `*.dll`, `*.so`, `*.dylib` |
| Log files | `*.log`, `*.log.*` |
| Temporary files | `*.tmp`, `*.swp`, `*.bak` |
| Large files | Files > 50 MB (use Git LFS or object storage) |

**If a secret is accidentally committed:**
1. Rotate the secret immediately — assume it is compromised
2. Use `git filter-repo` (not `git filter-branch`) to remove from history
3. Force-push all branches (coordinate with team)
4. Notify security team

---

## 8. Commit Frequency

- Commit every **small, logical unit of work** — not every file save, not every feature
- A commit should pass all tests and leave the codebase in a working state
- Never commit code that breaks the build or fails tests to a shared branch
- WIP commits are acceptable on personal branches; squash before merging

---

## 9. git bisect and git blame Best Practices

### git bisect

Use `git bisect` to binary-search for the commit that introduced a regression:

```bash
git bisect start
git bisect bad HEAD           # current state is broken
git bisect good v2.3.0        # known good version
# git will checkout commits automatically; test and mark each
git bisect good               # or: git bisect bad
git bisect reset              # when done
```

Good commit messages make bisect effective — this is why commit message quality matters.

### git blame

```bash
git blame -w -C -C -C <file>   # ignore whitespace; follow code across renames/moves
git log --follow -p -- <file>  # full history for a file including renames
```

Never use `git blame` to assign fault — use it to understand context and decision history.
