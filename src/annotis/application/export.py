"""Export engine: COCO JSON, YOLO TXT, and dataset metadata CSV.

No UI imports. No database imports. All writers are idempotent — calling
twice with the same session produces the same output.

Dependency rule: this module may only import from annotis.domain.
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from annotis.domain.errors import ExportError, InvalidAnnotationError
from annotis.domain.models import Annotation, ImageRecord, Session

logger = logging.getLogger(__name__)


def export_coco(session: Session, output_dir: Path) -> Path:
    """Export all annotations to a single COCO-format JSON file.

    O(n * m) where n = images, m = annotations per image.

    Args:
        session: Populated Session to export.
        output_dir: Directory in which to write ``annotations.coco.json``.

    Returns:
        Absolute path to the written JSON file.

    Raises:
        ExportError: If the output file cannot be written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    coco = _build_coco_dict(session)
    dest = output_dir / "annotations.coco.json"
    try:
        dest.write_text(json.dumps(coco, indent=2, default=str), encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Cannot write COCO file: {exc}") from exc
    return dest


def export_yolo(session: Session, output_dir: Path) -> Path:
    """Export annotations in YOLO v5+ TXT format (one file per image).

    Writes ``labels/<stem>.txt`` for each image and a ``classes.txt``.
    O(n * m) where n = images, m = annotations per image.

    Args:
        session: Populated Session to export.
        output_dir: Root export directory.

    Returns:
        Absolute path to the ``labels/`` sub-directory.

    Raises:
        ExportError: If any label file cannot be written.
    """
    labels_dir = output_dir / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)
    class_index = {label: i for i, label in enumerate(session.class_labels)}

    for record in session.images:
        lines = _record_to_yolo_lines(record, class_index)
        label_file = labels_dir / (record.path.stem + ".txt")
        try:
            label_file.write_text("\n".join(lines), encoding="utf-8")
        except OSError as exc:
            raise ExportError(f"Cannot write YOLO label {label_file}: {exc}") from exc

    classes_file = output_dir / "classes.txt"
    classes_file.write_text("\n".join(session.class_labels), encoding="utf-8")
    return labels_dir


def export_metadata_csv(session: Session, output_dir: Path) -> Path:
    """Export per-image metadata and QC metrics to a flat CSV file.

    O(n) where n = number of images in the session.

    Args:
        session: Session to export.
        output_dir: Directory in which to write ``dataset_metadata.csv``.

    Returns:
        Absolute path to the written CSV file.

    Raises:
        ExportError: If the session has no images or writing fails.
    """
    if not session.images:
        raise ExportError("No images in session to export.")

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [_record_to_csv_row(r) for r in session.images]
    dest = output_dir / "dataset_metadata.csv"

    try:
        with dest.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        raise ExportError(f"Cannot write CSV: {exc}") from exc
    return dest


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_coco_dict(session: Session) -> dict[str, Any]:
    """Build the full COCO-format dict from a session.  O(n * m)."""
    categories = [
        {"id": i + 1, "name": label, "supercategory": "none"}
        for i, label in enumerate(session.class_labels)
    ]
    class_to_id = {label: i + 1 for i, label in enumerate(session.class_labels)}
    coco_images: list[dict[str, Any]] = []
    coco_annotations: list[dict[str, Any]] = []
    ann_id = 1

    for img_idx, record in enumerate(session.images):
        coco_images.append(
            {
                "id": img_idx + 1,
                "file_name": record.path.name,
                "width": record.metadata.width,
                "height": record.metadata.height,
                "date_captured": str(record.metadata.creation_date or ""),
            }
        )
        for ann in record.annotations:
            coco_annotations.append(
                _annotation_to_coco(ann, img_idx + 1, ann_id, class_to_id)
            )
            ann_id += 1

    return {
        "info": {
            "description": "Annotis export",
            "version": "1.0",
            "year": datetime.now(timezone.utc).year,
            "date_created": datetime.now(timezone.utc).isoformat(),
        },
        "licenses": [],
        "images": coco_images,
        "annotations": coco_annotations,
        "categories": categories,
    }


def _annotation_to_coco(
    ann: Annotation,
    image_id: int,
    ann_id: int,
    class_to_id: dict[str, int],
) -> dict[str, Any]:
    """Convert one Annotation to a COCO annotation dict entry.  O(1).

    Raises:
        InvalidAnnotationError: If the annotation has no bbox.
    """
    if ann.bbox is None:
        raise InvalidAnnotationError(
            f"Annotation {ann.annotation_id} has no bbox; "
            "cannot export to COCO format."
        )
    return {
        "id": ann_id,
        "image_id": image_id,
        "category_id": class_to_id.get(ann.class_label, 0),
        "bbox": ann.bbox.to_coco(),
        "area": ann.bbox.area(),
        "segmentation": [],
        "iscrowd": int(ann.is_crowd),
    }


def _record_to_yolo_lines(
    record: ImageRecord,
    class_index: dict[str, int],
) -> list[str]:
    """Convert one record's bbox annotations to YOLO label lines.  O(m)."""
    img_w = float(record.metadata.width)
    img_h = float(record.metadata.height)
    lines: list[str] = []

    for ann in record.annotations:
        if ann.bbox is None:
            continue
        class_id = class_index.get(ann.class_label, -1)
        if class_id < 0:
            continue
        cx, cy, w, h = ann.bbox.to_yolo(img_w, img_h)
        lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return lines


def _record_to_csv_row(record: ImageRecord) -> dict[str, Any]:
    """Flatten one ImageRecord to a CSV-row dict.  O(1).

    Column schema (24 columns):
        image_id, file_name, file_path, width, height, channels,
        bit_depth, color_space, file_size_bytes, format, creation_date,
        sharpness, brightness_mean, brightness_std, contrast,
        noise_estimate, saturation_mean, quality_score,
        object_count, avg_area_px, avg_area_pct, foreground_ratio,
        class_distribution, is_annotated
    """
    m = record.metadata
    q = record.qc_metrics
    s = record.annotation_stats
    return {
        "image_id": record.image_id,
        "file_name": record.path.name,
        "file_path": str(record.path),
        "width": m.width,
        "height": m.height,
        "channels": m.channels,
        "bit_depth": m.bit_depth,
        "color_space": m.color_space,
        "file_size_bytes": m.file_size_bytes,
        "format": m.format,
        "creation_date": str(m.creation_date or ""),
        "sharpness": round(q.sharpness, 4),
        "brightness_mean": round(q.brightness_mean, 4),
        "brightness_std": round(q.brightness_std, 4),
        "contrast": round(q.contrast, 4),
        "noise_estimate": round(q.noise_estimate, 4),
        "saturation_mean": round(q.saturation_mean, 4),
        "quality_score": round(q.quality_score(), 4),
        "object_count": s.object_count,
        "avg_area_px": round(s.avg_area_px, 4),
        "avg_area_pct": round(s.avg_area_pct, 4),
        "foreground_ratio": round(s.foreground_ratio, 4),
        "class_distribution": json.dumps(s.class_distribution),
        "is_annotated": record.is_annotated,
    }
