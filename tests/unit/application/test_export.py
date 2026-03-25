"""Unit tests for the export application service."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from annotis.application.export import export_coco, export_metadata_csv, export_yolo
from annotis.domain.errors import ExportError, InvalidAnnotationError
from annotis.domain.models import (
    Annotation,
    BoundingBox,
    ImageMetadata,
    ImageRecord,
    Session,
)


def _make_session(with_annotation: bool = True) -> Session:
    """Build a minimal single-image Session for export tests."""
    annotations: list[Annotation] = []
    if with_annotation:
        annotations = [
            Annotation(
                class_label="cat",
                bbox=BoundingBox(x=10.0, y=20.0, width=100.0, height=80.0),
            )
        ]
    record = ImageRecord(
        path=Path("/tmp/test.jpg"),
        metadata=ImageMetadata(width=800, height=600, channels=3),
        is_annotated=with_annotation,
        annotations=annotations,
    )
    return Session(
        project_name="test",
        image_folder=Path("/tmp"),
        class_labels=["cat", "dog"],
        images=[record],
    )


class TestExportCoco:
    def test_produces_valid_json_with_required_top_level_keys(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            path = export_coco(session, Path(tmp))
            data = json.loads(path.read_text())

        for key in ("info", "images", "annotations", "categories", "licenses"):
            assert key in data

    def test_image_count_matches_session(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            path = export_coco(session, Path(tmp))
            data = json.loads(path.read_text())

        assert len(data["images"]) == 1

    def test_annotation_bbox_matches_source_values(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            path = export_coco(session, Path(tmp))
            data = json.loads(path.read_text())

        assert data["annotations"][0]["bbox"] == [10.0, 20.0, 100.0, 80.0]

    def test_annotation_area_equals_width_times_height(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            path = export_coco(session, Path(tmp))
            data = json.loads(path.read_text())

        assert data["annotations"][0]["area"] == 100.0 * 80.0

    def test_categories_contain_all_session_labels(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            path = export_coco(session, Path(tmp))
            data = json.loads(path.read_text())

        names = {c["name"] for c in data["categories"]}
        assert names == {"cat", "dog"}

    def test_annotation_without_bbox_raises_invalid_annotation_error(self) -> None:
        session = _make_session(with_annotation=False)
        session.images[0].annotations = [
            Annotation(class_label="cat", bbox=None)
        ]

        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(InvalidAnnotationError):
                export_coco(session, Path(tmp))

    def test_is_idempotent_when_called_twice(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            path1 = export_coco(session, Path(tmp))
            path2 = export_coco(session, Path(tmp))

        assert path1.name == path2.name


class TestExportYolo:
    def test_creates_label_file_for_each_image(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            labels_dir = export_yolo(session, Path(tmp))
            assert (labels_dir / "test.txt").exists()

    def test_class_id_matches_index_in_session_labels(self) -> None:
        # "cat" is index 0 in ["cat", "dog"]
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            labels_dir = export_yolo(session, Path(tmp))
            line = (labels_dir / "test.txt").read_text().strip()

        assert int(line.split()[0]) == 0

    def test_all_bbox_values_are_normalised_to_unit_range(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            labels_dir = export_yolo(session, Path(tmp))
            parts = (labels_dir / "test.txt").read_text().strip().split()

        assert all(0.0 <= float(v) <= 1.0 for v in parts[1:])

    def test_creates_classes_txt_listing_all_labels(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            export_yolo(session, Path(tmp))
            classes = Path(tmp, "classes.txt").read_text().splitlines()

        assert classes == ["cat", "dog"]

    def test_image_with_no_annotations_produces_empty_label_file(self) -> None:
        session = _make_session(with_annotation=False)

        with tempfile.TemporaryDirectory() as tmp:
            labels_dir = export_yolo(session, Path(tmp))
            content = (labels_dir / "test.txt").read_text()

        assert content == ""


class TestExportMetadataCsv:
    def test_csv_contains_all_required_columns(self) -> None:
        session = _make_session()
        required = {
            "image_id", "file_name", "sharpness",
            "object_count", "quality_score", "is_annotated",
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = export_metadata_csv(session, Path(tmp))
            header = set(path.read_text().splitlines()[0].split(","))

        assert required.issubset(header)

    def test_has_one_data_row_per_image(self) -> None:
        session = _make_session()

        with tempfile.TemporaryDirectory() as tmp:
            path = export_metadata_csv(session, Path(tmp))
            lines = path.read_text().splitlines()

        assert len(lines) == 2  # header + 1 data row

    def test_raises_export_error_on_empty_session(self) -> None:
        session = Session(
            project_name="empty",
            image_folder=Path("/tmp"),
            images=[],
        )

        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(ExportError, match="No images"):
                export_metadata_csv(session, Path(tmp))
