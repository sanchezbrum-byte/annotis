# Python Standards

Python is used for backend services, data pipelines, ML/AI tooling, and scripting. These standards apply to all Python code regardless of use case.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length (hard limit) | 88 characters | Black formatter default |
| Line length (soft limit) | 79 characters | PEP 8 |
| Indentation | 4 spaces (never tabs) | PEP 8 |
| Max function length | 50 lines | Google Python Style Guide guidance |
| Max file length | 1000 lines | Google Python Style Guide |
| Max parameters | 5 (use dataclass/TypedDict if > 5) | Team convention |
| Min test coverage | 80% business logic, 100% critical paths | Team convention |
| Python version | 3.11+ (3.12 preferred) | Team convention |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full formatting, naming, and code rules |
| [architecture.md](architecture.md) | Project layout, layers, DI patterns |
| [testing.md](testing.md) | pytest conventions, fixtures, mocking |
| [tooling.md](tooling.md) | Black, Ruff, mypy, pytest, pyproject.toml |
| [performance.md](performance.md) | Profiling, async patterns, memory |
| [examples/](examples/) | Good and bad code examples |

## Tooling Summary

```bash
# Format
black .
isort .

# Lint
ruff check .

# Type check
mypy .

# Test
pytest --cov=src --cov-report=term-missing

# All checks (pre-commit / CI)
pre-commit run --all-files
```
