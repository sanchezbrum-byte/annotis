# Annotis

Domain-agnostic local image annotation and ML-dataset preparation tool.
Fully offline. No cloud dependencies.

**Supported domains**: medical imaging, satellite, industrial inspection, or any image type.

## Status

🚧 Under active development — MVP in progress.

## Quickstart

> **macOS 12 Monterey**: Python 3.13 has no pre-built wheels for OpenCV or
> PyQt6 6.5+. Use Python 3.11 and the pinned versions below.

```bash
# 1. Create a Python 3.11 venv (brew install python@3.11 if needed)
python3.11 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies with pre-built wheels (no compilation)
pip install "opencv-python==4.10.0.84" --only-binary=:all:
pip install "PyQt6==6.4.2" "PyQt6-Qt6==6.4.2" --only-binary=:all:
pip install Pillow piexif numpy scipy scikit-learn
pip install -e ".[dev]"

# 3. Run tests
pytest

# 4. Launch the app
annotis
```

## Quality Gate

```bash
black . && ruff check . && mypy src && pytest
```

## Architecture

Clean Architecture with four layers: `domain` → `application` → `adapters` → `ui`.
See `BLUEPRINT.md` for the full design (added when MVP is complete).
