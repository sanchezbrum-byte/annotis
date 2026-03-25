# Git Workflow AI Rules

> Full reference: `universal/git-workflow.md`

---

## Commit Format (Conventional Commits v1.0.0)

```
<type>[(scope)]: <description>
                               ← blank line
[body — explains WHY]
                               ← blank line
[footer — Closes: #123, BREAKING CHANGE: ...]
```

**Types:** `feat` `fix` `docs` `style` `refactor` `perf` `test` `chore` `ci` `build` `revert`

**Rules:**
- Subject: imperative mood, max **72 chars**, no period
- Body: wrap at 72 chars; explains WHY, not WHAT
- `feat!:` or `BREAKING CHANGE:` footer for breaking changes

**Examples:**
```
feat(auth): add OAuth2 PKCE flow for mobile clients
fix(pay): prevent double-charge on network timeout retry
docs: update getting-started guide with Docker Compose setup
chore(deps): bump axios from 1.6.0 to 1.7.2
```

---

## Branch Naming

```
feat/AUTH-123-oauth2-pkce
fix/PAY-456-double-charge-retry
hotfix/SEC-789-xss-in-markdown-renderer
release/v2.4.0
chore/update-node-20
```

Rules: lowercase, hyphens only, include ticket number when available

---

## SemVer Tagging

- `MAJOR.MINOR.PATCH`
- MAJOR: breaking change; MINOR: new feature; PATCH: bug fix
- Always use annotated tags: `git tag -a v2.4.0 -m "release: v2.4.0"`

---

## PR Rules

- Max **400 lines changed** per PR (Google recommendation)
- Self-review before requesting reviewer
- CI must pass before requesting review
- Reviewer responds within **1 business day**

---

## Never Commit

- Secrets, API keys, passwords, tokens
- `.env` files with real values
- `node_modules/`, `__pycache__/`, `*.pyc`, `target/`, `dist/`
- `.DS_Store`, IDE files (unless sharing settings intentionally)
- Compiled binaries, large files > 50 MB

---

## Merge Strategy

| Situation | Strategy |
|-----------|---------|
| Feature branch → main | **Squash and merge** |
| Release branch → main | **Merge commit** |
| Never on shared branches | **rebase --force-push** |
