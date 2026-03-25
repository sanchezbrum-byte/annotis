# Python Tooling

## Required Tools

| Tool | Purpose | Config File |
|------|---------|------------|
| **Black** | Code formatter | `pyproject.toml` `[tool.black]` |
| **Ruff** | Fast linter (replaces flake8, isort, pyupgrade) | `pyproject.toml` `[tool.ruff]` |
| **mypy** | Static type checker | `pyproject.toml` `[tool.mypy]` |
| **pytest** | Test framework | `pyproject.toml` `[tool.pytest.ini_options]` |
| **pytest-cov** | Coverage reporting | `pyproject.toml` |
| **pre-commit** | Git hook runner | `.pre-commit-config.yaml` |

## Reference pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "pydantic>=2.6.0",
    "sqlalchemy>=2.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "black>=24.0.0",
    "ruff>=0.3.0",
    "mypy>=1.9.0",
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-asyncio>=0.23.0",
    "factory-boy>=3.3.0",
    "testcontainers[postgres]>=4.3.0",
    "pre-commit>=3.7.0",
]

[tool.black]
line-length = 88
target-version = ["py311", "py312"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
    "S",    # bandit security rules
]
ignore = [
    "S101",  # assert in tests is fine
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "S106"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/migrations/*", "*/conftest.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.4
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic
          - sqlalchemy[mypy]
```
