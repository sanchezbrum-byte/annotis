"""Unit tests for domain models.

Naming convention: test_<method>_<scenario>_<expected_behaviour>
Pattern: AAA (Arrange – Act – Assert) with one blank line between sections.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from annotis.domain.models import (
    Annotation,
    BoundingBox,
    ImageRecord,
    QCMetrics,
    Session,
)

# ---------------------------------------------------------------------------
# BoundingBox
# ---------------------------------------------------------------------------


class TestBoundingBoxArea:
    def test_area_with_positive_dimensions_returns_product(self) -> None:
        # Arrange
        bbox = BoundingBox(x=0.0, y=0.0, width=50.0, height=30.0)

        # Act
        result = bbox.area()

        # Assert
        assert result == 1500.0

    def test_area_with_zero_width_returns_zero(self) -> None:
        bbox = BoundingBox(x=0.0, y=0.0, width=0.0, height=30.0)

        assert bbox.area() == 0.0

    def test_area_with_zero_height_returns_zero(self) -> None:
        bbox = BoundingBox(x=0.0, y=0.0, width=50.0, height=0.0)

        assert bbox.area() == 0.0


class TestBoundingBoxToCoco:
    def test_to_coco_returns_list_of_four_floats(self) -> None:
        bbox = BoundingBox(x=5.0, y=10.0, width=100.0, height=50.0)

        result = bbox.to_coco()

        assert result == [5.0, 10.0, 100.0, 50.0]

    def test_to_coco_preserves_float_values(self) -> None:
        bbox = BoundingBox(x=1.5, y=2.5, width=3.5, height=4.5)

        assert bbox.to_coco() == [1.5, 2.5, 3.5, 4.5]


class TestBoundingBoxToYolo:
    def test_to_yolo_centre_x_is_correctly_normalised(self) -> None:
        # bbox left=100, width=200 → cx=(100+100)/1000 = 0.2
        bbox = BoundingBox(x=100.0, y=0.0, width=200.0, height=100.0)

        cx, _cy, _w, _h = bbox.to_yolo(img_width=1000.0, img_height=500.0)

        assert cx == pytest.approx(0.2)

    def test_to_yolo_all_values_are_in_unit_range(self) -> None:
        bbox = BoundingBox(x=0.0, y=0.0, width=640.0, height=480.0)

        cx, cy, w, h = bbox.to_yolo(img_width=640.0, img_height=480.0)

        assert all(0.0 <= v <= 1.0 for v in (cx, cy, w, h))

    def test_to_yolo_full_image_bbox_has_centre_at_half_half(self) -> None:
        bbox = BoundingBox(x=0.0, y=0.0, width=100.0, height=100.0)

        cx, cy, w, h = bbox.to_yolo(img_width=100.0, img_height=100.0)

        assert cx == pytest.approx(0.5)
        assert cy == pytest.approx(0.5)
        assert w == pytest.approx(1.0)
        assert h == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# QCMetrics
# ---------------------------------------------------------------------------


class TestQCMetricsQualityScore:
    def test_quality_score_is_within_zero_one_range(self) -> None:
        metrics = QCMetrics(sharpness=500.0, brightness_mean=128.0)

        score = metrics.quality_score()

        assert 0.0 <= score <= 1.0

    def test_quality_score_with_perfect_inputs_returns_one(self) -> None:
        # sharpness >> 1000 → normalised to 1.0; brightness=128 → balance=1.0
        metrics = QCMetrics(sharpness=99_999.0, brightness_mean=128.0)

        assert metrics.quality_score() == pytest.approx(1.0, abs=0.01)

    def test_quality_score_dark_image_is_lower_than_balanced_image(self) -> None:
        balanced = QCMetrics(sharpness=1000.0, brightness_mean=128.0)
        dark = QCMetrics(sharpness=1000.0, brightness_mean=0.0)

        assert balanced.quality_score() > dark.quality_score()


# ---------------------------------------------------------------------------
# ImageRecord — undo / redo stack
# ---------------------------------------------------------------------------


class TestImageRecordUndoRedo:
    def _make_record(self) -> ImageRecord:
        return ImageRecord(path=Path("img.jpg"))

    def test_undo_on_empty_stack_returns_false(self) -> None:
        record = self._make_record()

        result = record.undo()

        assert result is False

    def test_undo_restores_previous_annotation_list(self) -> None:
        record = self._make_record()
        ann = Annotation(class_label="cat")
        record.annotations = [ann]
        record.push_undo_snapshot()
        record.annotations = []

        result = record.undo()

        assert result is True
        assert len(record.annotations) == 1
        assert record.annotations[0].class_label == "cat"

    def test_push_snapshot_captures_deep_copy_so_later_mutations_are_isolated(
        self,
    ) -> None:
        record = self._make_record()
        ann = Annotation(class_label="cat")
        record.annotations = [ann]
        record.push_undo_snapshot()  # deep-copies ["cat"]

        # Mutate AFTER snapshot — must not affect the stored copy
        record.annotations[0].class_label = "mutated"
        record.undo()

        assert record.annotations[0].class_label == "cat"

    def test_redo_on_empty_stack_returns_false(self) -> None:
        record = self._make_record()

        assert record.redo() is False

    def test_redo_reapplies_undone_state(self) -> None:
        record = self._make_record()
        record.annotations = [Annotation(class_label="dog")]
        record.push_undo_snapshot()
        record.annotations = []
        record.undo()

        result = record.redo()

        assert result is True
        assert record.annotations == []

    def test_push_undo_snapshot_clears_redo_stack(self) -> None:
        record = self._make_record()
        record.annotations = [Annotation(class_label="cat")]
        record.push_undo_snapshot()
        record.annotations = []
        record.undo()  # populates redo stack
        record.push_undo_snapshot()  # must clear redo

        assert record.redo() is False


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


class TestSession:
    def test_annotated_count_counts_only_annotated_records(self) -> None:
        r1 = ImageRecord(path=Path("a.jpg"), is_annotated=True)
        r2 = ImageRecord(path=Path("b.jpg"), is_annotated=False)

        session = Session(images=[r1, r2])

        assert session.annotated_count == 1

    def test_total_count_equals_length_of_images_list(self) -> None:
        session = Session(images=[ImageRecord(path=Path("a.jpg"))])

        assert session.total_count == 1

    def test_annotated_count_on_empty_session_returns_zero(self) -> None:
        assert Session().annotated_count == 0
