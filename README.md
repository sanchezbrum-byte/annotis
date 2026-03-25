# Annotis

Domain-agnostic local image annotation and ML-dataset preparation tool.
Fully offline. No cloud dependencies.

**Supported domains**: medical imaging, satellite, industrial inspection, or any image type.

## Status

🚧 Under active development — MVP in progress.

## Quickstart (once released)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
annotis
```

## Quality Gate

```bash
black . && ruff check . && mypy src && pytest
```

## Architecture

Clean Architecture with four layers: `domain` → `application` → `adapters` → `ui`.
See `BLUEPRINT.md` for the full design (added when MVP is complete).
