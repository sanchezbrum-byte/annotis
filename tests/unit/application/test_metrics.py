"""Unit tests for annotation statistics computation."""

from __future__ import annotations

from pathlib import Path

from annotis.application.metrics import compute_annotation_stats
from annotis.domain.models import Annotation, BoundingBox, ImageMetadata, ImageRecord


def _record(width: int = 1000, height: int = 1000) -> ImageRecord:
    """Build a minimal ImageRecord with given dimensions."""
    return ImageRecord(
        path=Path("/tmp/img.jpg"),
        metadata=ImageMetadata(width=width, height=height),
    )


class TestComputeAnnotationStats:
    def test_no_annotations_returns_zeroed_stats(self) -> None:
        record = _record()

        stats = compute_annotation_stats(record)

        assert stats.object_count == 0
        assert stats.avg_area_px == 0.0
        assert stats.foreground_ratio == 0.0
        assert stats.class_distribution == {}

    def test_counts_only_annotations_with_bbox(self) -> None:
        record = _record()
        record.annotations = [
            Annotation(class_label="cat", bbox=BoundingBox(0, 0, 100, 100)),
            Annotation(class_label="dog", bbox=None),  # no bbox — skipped
        ]

        stats = compute_annotation_stats(record)

        assert stats.object_count == 1

    def test_average_area_is_mean_of_individual_bbox_areas(self) -> None:
        record = _record()
        record.annotations = [
            Annotation(class_label="x", bbox=BoundingBox(0, 0, 100, 100)),  # 10 000
            Annotation(class_label="x", bbox=BoundingBox(0, 0, 200, 200)),  # 40 000
        ]

        stats = compute_annotation_stats(record)

        assert stats.avg_area_px == 25_000.0

    def test_class_distribution_counts_per_label(self) -> None:
        record = _record()
        record.annotations = [
            Annotation(class_label="cat", bbox=BoundingBox(0, 0, 10, 10)),
            Annotation(class_label="cat", bbox=BoundingBox(0, 0, 10, 10)),
            Annotation(class_label="dog", bbox=BoundingBox(0, 0, 10, 10)),
        ]

        stats = compute_annotation_stats(record)

        assert stats.class_distribution == {"cat": 2, "dog": 1}

    def test_avg_area_pct_reflects_fraction_of_image(self) -> None:
        # 100×100 image; one 100×50 bbox → area = 5000 = 50 %
        record = _record(width=100, height=100)
        record.annotations = [
            Annotation(class_label="x", bbox=BoundingBox(0, 0, 100, 50)),
        ]

        stats = compute_annotation_stats(record)

        assert stats.avg_area_pct == 50.0

    def test_foreground_ratio_is_capped_at_one(self) -> None:
        # Annotation larger than the image itself
        record = _record(width=10, height=10)
        record.annotations = [
            Annotation(class_label="x", bbox=BoundingBox(0, 0, 1000, 1000)),
        ]

        stats = compute_annotation_stats(record)

        assert stats.foreground_ratio <= 1.0

    def test_zero_dimension_image_does_not_divide_by_zero(self) -> None:
        record = _record(width=0, height=0)
        record.annotations = [
            Annotation(class_label="x", bbox=BoundingBox(0, 0, 10, 10)),
        ]

        stats = compute_annotation_stats(record)

        assert stats.avg_area_pct == 0.0
        assert stats.foreground_ratio == 0.0
