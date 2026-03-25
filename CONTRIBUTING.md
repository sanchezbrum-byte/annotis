# Contributing to Engineering Standards

Thank you for helping maintain these standards. This guide explains how to propose, update, and merge changes.

---

## Guiding Principles for Changes

1. **Cite sources** — every specific rule must cite where it comes from (style guide URL, RFC, etc.)
2. **When standards conflict** — document both positions, explain the trade-off, give a recommendation
3. **Numeric rules require sources** — max line length, function length, coverage % must be cited
4. **No opinions without evidence** — "I prefer X" is not a valid reason; "Google, Airbnb, and JetBrains all recommend X because Y" is
5. **Backward compatibility** — when changing a rule that existing code may violate, provide a migration path

---

## How to Update Standards

### 1. Always Edit `ai-rules/core/` First

The core files are the single source of truth. All adapter files are generated from them.

```bash
# Edit the relevant core file
vim ai-rules/core/python.md

# Or edit a detailed guide
vim python/style-guide.md
```

### 2. Run the Sync Script

After editing any `ai-rules/core/` file:

```bash
./sync-adapters.sh
```

This regenerates all adapter files (Cursor, Copilot, Windsurf, Continue.dev, Aider, Claude).

### 3. Commit Both Core and Adapters

```bash
git add ai-rules/core/python.md
git add ai-rules/adapters/
git add python/style-guide.md  # if also updated

git commit -m "docs(python): update max line length to 88 (Black default)

PEP 8 specifies 79, but Black's 88-char default is now widely adopted
and avoids constant reformatting conflicts. Sources:
- Black formatter default: https://black.readthedocs.io/
- Google Python Style Guide now recommends Black"
```

### 4. Open a Pull Request

PR title: `docs(<language/topic>): <brief description>`

PR description must include:
- **What changed** — which rule was updated
- **Why** — cite the source (URL, RFC, style guide version)
- **Impact** — does existing code need to change? Is there a migration path?
- **Dissent** — if there are valid opposing views, document them

---

## Proposing a New Language

1. Create the directory: `mkdir -p <language>/examples`
2. Create `<language>/README.md` — use an existing language README as template
3. Create `<language>/style-guide.md` with all required sections (A through I)
4. Create `ai-rules/core/<language>.md` — concise, ≤200 lines distillation
5. Add the language to `sync-adapters.sh` LANGUAGES array
6. Run `./sync-adapters.sh`
7. Add the language to the root `README.md` language coverage table
8. Add examples to `<language>/examples/`

---

## Proposing a New AI Tool Adapter

1. Research the exact format the tool requires (consult official docs)
2. Add a new adapter directory: `ai-rules/adapters/<toolname>/`
3. Add a generation function to `sync-adapters.sh`
4. Document the tool in `ai-rules/README.md` (adapter system section)
5. Document the setup command in the root `README.md` tool table

---

## Review Process

All changes to engineering standards go through peer review:

- **Minor changes** (fixing a typo, clarifying wording): 1 reviewer, 1 business day SLA
- **Rule changes** (changing a specific rule): 2 reviewers including a tech lead, 2 business day SLA
- **New language or section**: 2 reviewers, 3 business day SLA

Reviewers must check:
- [ ] Source citations are present and accurate
- [ ] Adapter files were regenerated (`./sync-adapters.sh` was run)
- [ ] Examples reflect the rule change (if applicable)
- [ ] Root README.md is updated if adding/removing a language

---

## Quarterly Review Process

Standards should be reviewed quarterly:

1. **Identify outdated rules** — check if language/tool versions have changed
2. **Review CVEs** — update security rules if new vulnerabilities have been added to OWASP Top 10
3. **Check tool updates** — did ESLint, Ruff, clippy add new relevant rules?
4. **Gather feedback** — ask engineers which rules they find unclear or unhelpful
5. **Update version** — bump CHANGELOG.md with a new version entry

---

## Code of Conduct for Standards Contributions

- Standards are not personal preferences — cite your sources
- If you disagree with a rule, propose a change through the PR process — don't just ignore it
- Document trade-offs when two valid approaches exist — don't pick one arbitrarily
- Be respectful in PR reviews — focus on the rule, not the person
