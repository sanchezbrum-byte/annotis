# Bash/Shell Standards

Shell scripts are used for CI/CD pipelines, system automation, build tooling, and DevOps scripts.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Shell | `bash` (specify explicitly) | Google Shell Style Guide |
| Shebang | `#!/usr/bin/env bash` | Google Shell Style Guide |
| Indentation | 2 spaces | Google Shell Style Guide |
| Line length | 80 characters | Google Shell Style Guide |
| `set` flags | `set -euo pipefail` always | Google Shell Style Guide |
| Variables | Quote all variable expansions: `"${var}"` | Google Shell Style Guide |
| Functions | `snake_case` | Google Shell Style Guide |
| Constants | `UPPER_SNAKE_CASE` | Google Shell Style Guide |
| ShellCheck | All scripts must pass ShellCheck | Team convention |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full Bash formatting and safety rules |
| [safety-patterns.md](safety-patterns.md) | Safe scripting, error handling, traps |
| [testing.md](testing.md) | BATS testing framework |
| [examples/](examples/) | Good and bad shell script examples |

## Tooling Summary

```bash
shellcheck myscript.sh      # lint (mandatory)
shfmt -i 2 -w myscript.sh  # format (2-space indent)
bats tests/                 # run tests
```
