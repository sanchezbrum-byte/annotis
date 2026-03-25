# AI Rules — Adapter System

This directory contains engineering standards formatted for every major AI coding tool.

## The Adapter System

```
ai-rules/
  core/           ← THE SOURCE OF TRUTH — edit ONLY these files
  adapters/
    cursor/       ← generated from core/
    github-copilot/ ← generated from core/
    windsurf/     ← generated from core/
    continue/     ← generated from core/
    aider/        ← generated from core/
    claude/       ← generated from core/
```

**Rule:** Never edit adapter files directly. Edit `core/` then run `sync-adapters.sh`.

## Core Files

| File | Language/Topic | Globs |
|------|---------------|-------|
| `universal.md` | All files | `**/*` |
| `python.md` | Python | `**/*.py` |
| `javascript.md` | JavaScript | `**/*.js`, `**/*.mjs` |
| `typescript.md` | TypeScript | `**/*.ts`, `**/*.tsx` |
| `java.md` | Java | `**/*.java` |
| `cpp.md` | C/C++ | `**/*.cc`, `**/*.cpp`, `**/*.h` |
| `rust.md` | Rust | `**/*.rs` |
| `go.md` | Go | `**/*.go` |
| `sql.md` | SQL | `**/*.sql` |
| `swift.md` | Swift | `**/*.swift` |
| `kotlin.md` | Kotlin | `**/*.kt`, `**/*.kts` |
| `bash.md` | Bash/Shell | `**/*.sh` |
| `git-workflow.md` | Git | `.git*` |
| `testing.md` | All tests | `**/*test*`, `**/*spec*` |
| `security.md` | All files | `**/*` |
| `architecture.md` | All files | `**/*` |

---

## Deploying to a New Project

### Cursor

```bash
# Option A: copy rules to your project
cp -r ai-rules/adapters/cursor/.cursor /path/to/your/project/

# Option B: symlink (stays in sync with this repo)
ln -s /path/to/engineering-foundation/ai-rules/adapters/cursor/.cursor \
    /path/to/your/project/.cursor
```

Rules in `.cursor/rules/*.mdc` are automatically picked up by Cursor.

### GitHub Copilot

```bash
cp ai-rules/adapters/github-copilot/.github/copilot-instructions.md \
    /path/to/your/project/.github/copilot-instructions.md
```

GitHub Copilot reads `.github/copilot-instructions.md` automatically.

### Windsurf

```bash
cp -r ai-rules/adapters/windsurf/.windsurf /path/to/your/project/
```

### Continue.dev

```bash
cp ai-rules/adapters/continue/.continue/config.json \
    ~/.continue/config.json  # or your project's .continue/config.json
```

### Aider

```bash
cp ai-rules/adapters/aider/CONVENTIONS.md /path/to/your/project/CONVENTIONS.md
```

Aider reads `CONVENTIONS.md` from the repo root automatically.

### Claude

```bash
cp ai-rules/adapters/claude/CLAUDE.md /path/to/your/project/CLAUDE.md
```

Claude reads `CLAUDE.md` as a project memory file.

### Zed

In Zed, open Settings → Assistant → add a system prompt. Copy the contents of `ai-rules/adapters/claude/CLAUDE.md` into the system prompt field.

---

## Keeping Adapters in Sync

When you update a `core/` file, run the sync script to regenerate all adapters:

```bash
./sync-adapters.sh
```

The script is in the repository root. It regenerates all adapter files from the `core/` source files.

---

## Adding a New Language

1. Create `ai-rules/core/<language>.md` with the rules
2. Add a section in `sync-adapters.sh` for the new language
3. Run `./sync-adapters.sh` to generate all adapter files
4. Create `<language>/style-guide.md` with the detailed guide
5. Add examples in `<language>/examples/`
6. Update the root `README.md` language coverage table
