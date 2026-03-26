# Annotis — Engineering Blueprint

> Authoritative design reference. Updated as the architecture evolves.
> All decisions follow `.standards/` (the engineering-foundation submodule).

---

## 1. Architecture & Tech Stack

### Overall Architecture

**Clean Architecture** with four concentric layers and inward-only dependencies:

```
┌─────────────────────────────────────────────────────────┐
│  Frameworks & Drivers  (PyQt6, SQLite, OpenCV, Pillow)   │
│  ┌───────────────────────────────────────────────────┐   │
│  │  Interface Adapters  (session_store, canvas, ui)  │   │
│  │  ┌─────────────────────────────────────────────┐  │   │
│  │  │  Application Services  (loader, metrics,    │  │   │
│  │  │                         export)             │  │   │
│  │  │  ┌───────────────────────────────────────┐  │  │   │
│  │  │  │  Domain  (models, errors)              │  │  │   │
│  │  │  └───────────────────────────────────────┘  │  │   │
│  │  └─────────────────────────────────────────────┘  │   │
│  └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Dependency rule**: inner layers import nothing from outer layers.
Domain has zero third-party imports. Application imports only domain.

### UI Approach: Desktop GUI (PyQt6)

Chosen over Streamlit/Gradio because:
- Offline-first: no browser/server process required
- `QGraphicsView` provides pixel-accurate mouse event handling
- Native OS widgets for file dialogs, menus, keyboard shortcuts
- Single process; no IPC latency between drawing and annotation state

### Python Tech Stack

| Library | Role | Why |
|---------|------|-----|
| `PyQt6` | Desktop GUI | Best-in-class annotation UX; `QGraphicsView` for canvas |
| `Pillow` | Image I/O, metadata, EXIF | Broad format support; thin wrapper |
| `opencv-python` | QC metrics (sharpness, noise, saturation) | Vectorised numpy operations |
| `tifffile` | Multi-channel scientific TIFFs | PIL cannot decode 32-bit/multi-page TIFFs |
| `piexif` | Structured EXIF parsing | Pillow only exposes raw bytes |
| `numpy` | Array maths for metrics | Underlying engine for OpenCV |
| `scikit-learn` | Stratified train/val/test split | `StratifiedShuffleSplit` |
| `scipy` | Statistical QC | Distribution analysis (v1) |
| `black` | Code formatter | Line-length 88, PEP 8 compliant |
| `ruff` | Linter (replaces flake8 + isort) | Fast; Rust-backed |
| `mypy --strict` | Type checker | Catches whole classes of bugs |
| `pytest + pytest-cov` | Test runner + coverage | Industry standard |
| `factory-boy` | Test data factories | No magic numbers in tests |
| `pre-commit` | Git hook quality gate | Prevents style regressions |

---

## 2. Folder Structure

```
src/annotis/
├── domain/           # Pure Python — no external imports
│   ├── models.py     # BoundingBox, Annotation, ImageRecord, Session …
│   └── errors.py     # AnnotisError hierarchy
├── application/      # Use-case services — import domain only
│   ├── image_loader.py  # discover_images, extract_metadata, compute_qc_metrics
│   ├── metrics.py       # compute_annotation_stats
│   └── export.py        # export_coco, export_yolo, export_metadata_csv
├── adapters/         # Infrastructure — import domain + stdlib
│   └── session_store.py # SQLite persistence (WAL mode)
└── ui/               # PyQt6 — import everything above
    ├── canvas.py        # AnnotationCanvas (QGraphicsView)
    ├── main_window.py   # MainWindow (three-panel layout)
    └── app.py           # Entry point

tests/
├── conftest.py          # Shared fixtures (tmp_jpeg, tmp_image_folder)
└── unit/
    ├── domain/          # test_models.py
    ├── application/     # test_metrics.py, test_export.py, test_image_loader.py
    └── adapters/        # test_session_store.py
```

---

## 3. Image Loading & Metadata

### Auto-extracted (no user input)

| Field | Source |
|-------|--------|
| Width, height | PIL `img.size` |
| Channels, bit-depth | PIL `mode` → lookup table |
| Colour space | PIL `mode` → human-readable string |
| File size | `Path.stat().st_size` |
| Format | PIL `img.format` |
| Creation date | `Path.stat().st_ctime` (filesystem) |
| EXIF tags | `piexif.load()` on `img.info["exif"]` |

### User-provided (once per session)

- **Project name** — `QInputDialog` on folder open
- **Class labels** — editable list in the right panel
- **Domain context / imaging modality** — free-text (stored in `Session`)

### Internal storage

All metadata and annotations live in Python dataclass instances (`ImageRecord`, `Session`) in memory during the session. Persistence is handled by `SessionStore` (SQLite, WAL mode).

---

## 4. Annotation Engine

### Supported annotation types (MVP)

- **Bounding box** (✅ implemented) — rubber-band mouse draw in `AnnotationCanvas`
- **Polygon** (v1) — click-to-add vertices, close on double-click
- **Point / keypoint** (v1) — single left-click

### Undo / Redo

`ImageRecord.push_undo_snapshot()` deep-copies the current annotation list before each mutation. `undo()` / `redo()` swap between snapshots. Max stack depth is unbounded in memory (typical annotation sessions are small).

### Edge cases

| Case | Handling |
|------|---------|
| Overlapping objects | Stored as separate `Annotation` instances; visually stacked |
| Objects at image border | No clipping — raw coordinates are stored; validation is export-time |
| Very small objects | Boxes < 3×3 px discarded at draw time (`mouseReleaseEvent`) |
| Partially visible objects | Annotate what is visible; `is_crowd` flag available |

---

## 5. Automatic Computation (per image)

### QC Metrics

| Metric | Formula | Library |
|--------|---------|---------|
| Sharpness | `Var(Laplacian(gray))` | `cv2.Laplacian(...).var()` |
| Brightness mean | `mean(gray)` | `ndarray.mean()` |
| Brightness std | `std(gray)` | `ndarray.std()` |
| Contrast | RMS = `std(gray)` | same as brightness std |
| Noise | `√(π/6) · mean(|H★I|)`, H = 3×3 Laplacian | `cv2.filter2D` + Immerkaer (1996) |
| Saturation | `mean(HSV[:,:,1])` | `cv2.cvtColor(BGR→HSV)` |
| Quality score | `0.6·norm_sharpness + 0.4·brightness_balance` | pure Python |

### Annotation Statistics (per image)

| Stat | Computation |
|------|------------|
| Object count | `len(bbox_annotations)` |
| Avg bbox area (px) | `mean([bbox.area()])` |
| Avg bbox area (%) | `avg_px / (W × H) × 100` |
| Class distribution | `Counter(ann.class_label for ann in ...)` |
| Foreground ratio | `sum(areas) / (W × H)`, capped at 1.0 |

### Dataset-level Statistics (live in UI)

- Total images annotated / total images → progress bar + status bar
- Class imbalance ratio → shown in right panel stats label

---

## 6. Export Engine

### COCO JSON (`export_coco`)

Schema: `{ info, licenses, images, annotations, categories }`.
- `images[].id` = sequential 1-based integer
- `annotations[].bbox` = `[x, y, w, h]` (top-left origin, pixels)
- `annotations[].area` = `w * h`
- `annotations[].iscrowd` = 0 or 1

### YOLO TXT (`export_yolo`)

One `.txt` per image in `labels/`. Format per line:
```
<class_id> <cx> <cy> <w> <h>
```
All values normalised to [0, 1]. Also writes `classes.txt`.

### Metadata CSV (`export_metadata_csv`)

24 columns per image row (see `_record_to_csv_row` docstring in `export.py`):
`image_id, file_name, file_path, width, height, channels, bit_depth,
color_space, file_size_bytes, format, creation_date, sharpness,
brightness_mean, brightness_std, contrast, noise_estimate,
saturation_mean, quality_score, object_count, avg_area_px, avg_area_pct,
foreground_ratio, class_distribution, is_annotated`

### Train / Val / Test Split (v1 — not yet implemented)

`sklearn.model_selection.StratifiedShuffleSplit` stratified by class
distribution bucket + quality score decile to prevent data leakage from
same-source tiles (e.g. same patient, same slide, same parent image).

---

## 7. Session Management

- **Autosave**: `QTimer` fires every 60 s → `SessionStore.save(session)`
- **WAL mode**: SQLite `PRAGMA journal_mode=WAL` — a crash mid-write
  leaves the last committed state intact
- **Undo/redo**: per-image, unbounded depth
- **Navigation**: arrow keys (←/→), image list click, status bar shows progress
- **Keyboard shortcuts**: see `MainWindow._setup_shortcuts()`

| Key | Action |
|-----|--------|
| `→` / `←` | Next / previous image |
| `Ctrl+Z` | Undo last annotation |
| `Ctrl+Y` | Redo |
| `Ctrl+S` | Save session now |
| `+` / `-` | Zoom in / out |
| `F` | Fit image to window |

---

## 8. Implementation Roadmap

### MVP (✅ completed)

- Domain models: `BoundingBox`, `Annotation`, `ImageRecord`, `Session`
- Error hierarchy
- Application services: metadata, QC metrics, annotation stats, export
- SQLite session store (WAL, upsert on conflict)
- PyQt6 canvas with bounding-box drawing
- Three-panel `MainWindow` with undo/redo, autosave, keyboard shortcuts
- COCO JSON, YOLO TXT, and CSV export
- Unit tests for all non-UI layers (pytest + factory-boy)

### v1

- Polygon annotation tool (click-to-add vertices)
- Point / keypoint annotation
- SAM2 click-to-segment integration (`sam2` optional dependency)
- Stratified train/val/test split (`scikit-learn`)
- Jump-to-unannotated navigation
- Filter images by QC quality score
- Multi-channel TIFF support (`tifffile`)

### v2

- Dataset-level statistics dashboard (matplotlib embedded in Qt)
- Batch relabelling (rename class across all images)
- Tile-stitching support (link tiles back to parent image)
- ONNX export of lightweight detection head fine-tuned on session data
- REST API server mode for remote annotation over LAN

---

## 9. Common Failure Points

| Risk | Mitigation |
|------|-----------|
| Corrupt JPEG mid-session | WAL SQLite; autosave every 60 s; `load_folder` skips unreadable files |
| OOM with very large TIFFs | Lazy-load with `tifffile`; QC metrics operate on downsampled copy |
| cv2 wheel download speed | Lazy import in `compute_qc_metrics`; module usable without cv2 |
| Overlapping export writes | `export_*` functions are idempotent (same output path on second call) |
| Qt thread safety | All UI mutations happen on the main Qt thread; SessionStore is injected |
| Big-O surprise in export | `_build_coco_dict` is O(n·m); profiled at 10 k images × 100 annotations |
