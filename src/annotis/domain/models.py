"""Core domain models for Annotis.

Dependency rule: this module imports ONLY the Python standard library.
No framework, no database driver, no HTTP client — ever.

All coordinates are in image pixel space (top-left origin) unless
explicitly stated otherwise (e.g. YOLO normalised coordinates).
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class AnnotationType(str, Enum):
    """Supported annotation geometry types."""

    BOUNDING_BOX = "bounding_box"
    POLYGON = "polygon"
    POINT = "point"


@dataclass
class BoundingBox:
    """Axis-aligned bounding box in image pixel coordinates (top-left origin)."""

    x: float
    y: float
    width: float
    height: float

    def area(self) -> float:
        """Return area in pixels². O(1)."""
        return self.width * self.height

    def to_coco(self) -> list[float]:
        """Return [x, y, width, height] per the COCO bbox specification. O(1)."""
        return [self.x, self.y, self.width, self.height]

    def to_yolo(
        self,
        img_width: float,
        img_height: float,
    ) -> tuple[float, float, float, float]:
        """Return centre-normalised (cx, cy, w, h) per the YOLO specification.

        All four values are in the range [0, 1].  O(1).

        Args:
            img_width: Image width in pixels (> 0).
            img_height: Image height in pixels (> 0).

        Returns:
            Tuple of (centre_x, centre_y, width, height), each in [0, 1].
        """
        cx = (self.x + self.width / 2.0) / img_width
        cy = (self.y + self.height / 2.0) / img_height
        w = self.width / img_width
        h = self.height / img_height
        return cx, cy, w, h


@dataclass
class Annotation:
    """Single annotated object instance attached to one image."""

    annotation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    class_label: str = ""
    annotation_type: AnnotationType = AnnotationType.BOUNDING_BOX
    bbox: BoundingBox | None = None
    polygon: list[tuple[float, float]] = field(default_factory=list)
    is_crowd: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ImageMetadata:
    """Technical metadata extracted automatically from an image file on load."""

    width: int = 0
    height: int = 0
    channels: int = 0
    bit_depth: int = 8
    color_space: str = "RGB"
    file_size_bytes: int = 0
    format: str = ""
    creation_date: datetime | None = None
    exif: dict[str, Any] = field(default_factory=dict)


@dataclass
class QCMetrics:
    """Image quality-control metrics computed automatically via OpenCV.

    Attribute names match the column names in dataset_metadata.csv.
    """

    sharpness: float = 0.0  # Laplacian variance — Pech-Pacheco (2000)
    brightness_mean: float = 0.0  # Mean gray intensity in [0, 255]
    brightness_std: float = 0.0  # Std-dev of gray intensities
    contrast: float = 0.0  # RMS contrast = brightness_std
    noise_estimate: float = 0.0  # Immerkaer (1996) σ estimate
    saturation_mean: float = 0.0  # Mean HSV saturation in [0, 255]

    def quality_score(self) -> float:
        """Return a composite quality score in [0.0, 1.0].  O(1).

        Heuristic: 60 % normalised sharpness + 40 % brightness balance.
        Threshold (1000) is a reasonable default; calibrate per domain.
        """
        norm_sharpness = min(self.sharpness / 1000.0, 1.0)
        brightness_balance = 1.0 - abs(self.brightness_mean - 128.0) / 128.0
        return norm_sharpness * 0.6 + brightness_balance * 0.4


@dataclass
class AnnotationStats:
    """Per-image annotation statistics recomputed after every change."""

    object_count: int = 0
    avg_area_px: float = 0.0
    avg_area_pct: float = 0.0
    class_distribution: dict[str, int] = field(default_factory=dict)
    foreground_ratio: float = 0.0


@dataclass
class ImageRecord:
    """Complete record for one image: path + metadata + QC + annotations."""

    image_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path: Path = field(default_factory=Path)
    metadata: ImageMetadata = field(default_factory=ImageMetadata)
    qc_metrics: QCMetrics = field(default_factory=QCMetrics)
    annotations: list[Annotation] = field(default_factory=list)
    annotation_stats: AnnotationStats = field(default_factory=AnnotationStats)
    is_annotated: bool = False
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    # Private undo/redo stacks — not serialised; rebuilt from scratch on load.
    _undo_stack: list[list[Annotation]] = field(default_factory=list, repr=False)
    _redo_stack: list[list[Annotation]] = field(default_factory=list, repr=False)

    def push_undo_snapshot(self) -> None:
        """Capture current annotations for undo.  Clears redo stack.  O(m)."""
        self._undo_stack.append(copy.deepcopy(self.annotations))
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Revert to the previous annotation state.

        Returns:
            True if undo was applied; False when the stack was already empty.
        """
        if not self._undo_stack:
            return False
        self._redo_stack.append(copy.deepcopy(self.annotations))
        self.annotations = self._undo_stack.pop()
        return True

    def redo(self) -> bool:
        """Re-apply the most recently undone annotation state.

        Returns:
            True if redo was applied; False when the redo stack was empty.
        """
        if not self._redo_stack:
            return False
        self._undo_stack.append(copy.deepcopy(self.annotations))
        self.annotations = self._redo_stack.pop()
        return True


@dataclass
class Session:
    """Top-level project session containing all images and project metadata."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str = ""
    image_folder: Path = field(default_factory=Path)
    class_labels: list[str] = field(default_factory=list)
    images: list[ImageRecord] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_saved: datetime | None = None
    domain_context: str = ""
    imaging_modality: str = ""

    @property
    def annotated_count(self) -> int:
        """Number of images that have at least one annotation.  O(n)."""
        return sum(1 for img in self.images if img.is_annotated)

    @property
    def total_count(self) -> int:
        """Total number of images in this session.  O(1)."""
        return len(self.images)
