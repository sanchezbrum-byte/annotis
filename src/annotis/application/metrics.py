"""Annotation statistics computed from an ImageRecord after annotation.

No UI imports. No database imports. Pure computation over domain models.
"""

from __future__ import annotations

import collections

from annotis.domain.models import AnnotationStats, ImageRecord


def compute_annotation_stats(record: ImageRecord) -> AnnotationStats:
    """Compute per-image annotation statistics from bounding-box annotations.

    Skips any Annotation whose bbox is None (polygon-only annotations are
    counted in a future version when polygon area is supported).

    O(m) where m = number of annotations on the record.

    Args:
        record: ImageRecord with populated annotations and metadata.

    Returns:
        AnnotationStats with all fields populated; returns a zeroed
        AnnotationStats when there are no bbox annotations.
    """
    bbox_anns = [a for a in record.annotations if a.bbox is not None]
    if not bbox_anns:
        return AnnotationStats()

    img_area = float(record.metadata.width * record.metadata.height)
    areas = [a.bbox.area() for a in bbox_anns]  # type: ignore[union-attr]
    total_fg = sum(areas)

    avg_area_px = total_fg / len(areas)
    avg_area_pct = (avg_area_px / img_area * 100.0) if img_area > 0.0 else 0.0
    foreground_ratio = min(total_fg / img_area, 1.0) if img_area > 0.0 else 0.0
    class_dist = dict(
        collections.Counter(a.class_label for a in bbox_anns)
    )

    return AnnotationStats(
        object_count=len(bbox_anns),
        avg_area_px=avg_area_px,
        avg_area_pct=avg_area_pct,
        class_distribution=class_dist,
        foreground_ratio=foreground_ratio,
    )
