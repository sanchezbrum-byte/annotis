"""Unit tests for the image loader application service.

Tests that call compute_qc_metrics, load_image_record, or load_folder
use pytest.importorskip("cv2") to skip gracefully when opencv-python
is not installed. Once cv2 is available they run automatically.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from annotis.application.image_loader import (
    compute_qc_metrics,
    discover_images,
    extract_metadata,
    load_folder,
    load_image_record,
)
from annotis.domain.errors import ImageLoadError, UnsupportedFormatError

_CV2_AVAILABLE = importlib.util.find_spec("cv2") is not None
_skip_without_cv2 = pytest.mark.skipif(
    not _CV2_AVAILABLE, reason="opencv-python not installed"
)

# ---------------------------------------------------------------------------
# discover_images
# ---------------------------------------------------------------------------


class TestDiscoverImages:
    def test_returns_sorted_paths_for_supported_files(
        self, tmp_image_folder: Path
    ) -> None:
        # Arrange — tmp_image_folder fixture creates 3 JPEGs
        paths = discover_images(tmp_image_folder)

        assert len(paths) == 3
        assert paths == sorted(paths)

    def test_excludes_non_image_files(self, tmp_image_folder: Path) -> None:
        (tmp_image_folder / "notes.txt").write_text("ignored")

        paths = discover_images(tmp_image_folder)

        assert all(p.suffix.lower() != ".txt" for p in paths)

    def test_empty_folder_returns_empty_list(self, tmp_path: Path) -> None:
        assert discover_images(tmp_path) == []

    def test_raises_value_error_for_nonexistent_path(self) -> None:
        with pytest.raises(ValueError, match="valid directory"):
            discover_images(Path("/nonexistent/path"))

    def test_raises_value_error_when_given_a_file_not_a_directory(
        self, tmp_jpeg: Path
    ) -> None:
        with pytest.raises(ValueError):
            discover_images(tmp_jpeg)


# ---------------------------------------------------------------------------
# extract_metadata
# ---------------------------------------------------------------------------


class TestExtractMetadata:
    def test_reports_correct_width_and_height(self, tmp_jpeg: Path) -> None:
        meta = extract_metadata(tmp_jpeg)

        assert meta.width == 100
        assert meta.height == 100

    def test_reports_rgb_color_space_for_jpeg(self, tmp_jpeg: Path) -> None:
        meta = extract_metadata(tmp_jpeg)

        assert meta.color_space == "RGB"

    def test_reports_nonzero_file_size(self, tmp_jpeg: Path) -> None:
        meta = extract_metadata(tmp_jpeg)

        assert meta.file_size_bytes > 0

    def test_raises_image_load_error_on_corrupted_file(self, tmp_path: Path) -> None:
        corrupt = tmp_path / "bad.jpg"
        corrupt.write_bytes(b"\xff\xd8 not a real jpeg")

        with pytest.raises(ImageLoadError):
            extract_metadata(corrupt)


# ---------------------------------------------------------------------------
# compute_qc_metrics  (requires opencv-python)
# ---------------------------------------------------------------------------


@_skip_without_cv2
class TestComputeQcMetrics:
    def test_sharpness_is_non_negative(self, tmp_jpeg: Path) -> None:
        qc = compute_qc_metrics(tmp_jpeg)

        assert qc.sharpness >= 0.0

    def test_brightness_mean_is_in_valid_pixel_range(self, tmp_jpeg: Path) -> None:
        qc = compute_qc_metrics(tmp_jpeg)

        assert 0.0 <= qc.brightness_mean <= 255.0

    def test_raises_image_load_error_for_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(ImageLoadError):
            compute_qc_metrics(tmp_path / "ghost.jpg")


# ---------------------------------------------------------------------------
# load_image_record  (requires opencv-python)
# ---------------------------------------------------------------------------


@_skip_without_cv2
class TestLoadImageRecord:
    def test_populates_metadata_and_qc_metrics(self, tmp_jpeg: Path) -> None:
        record = load_image_record(tmp_jpeg)

        assert record.metadata.width == 100
        assert record.qc_metrics.brightness_mean >= 0.0
        assert record.annotations == []

    def test_raises_unsupported_format_for_unknown_extension(
        self, tmp_path: Path
    ) -> None:
        bad = tmp_path / "data.xyz"
        bad.write_text("not an image")

        with pytest.raises(UnsupportedFormatError):
            load_image_record(bad)


# ---------------------------------------------------------------------------
# load_folder  (requires opencv-python)
# ---------------------------------------------------------------------------


@_skip_without_cv2
class TestLoadFolder:
    def test_returns_one_record_per_readable_image(
        self, tmp_image_folder: Path
    ) -> None:
        records = load_folder(tmp_image_folder)

        assert len(records) == 3

    def test_skips_unreadable_files_without_raising(self, tmp_path: Path) -> None:
        from PIL import Image as PILImage

        folder = tmp_path / "imgs"
        folder.mkdir()
        PILImage.new("RGB", (50, 50)).save(str(folder / "good.jpg"))
        (folder / "bad.png").write_bytes(b"this is not a png")

        records = load_folder(folder)

        assert len(records) == 1

    def test_returns_empty_list_for_empty_directory(self, tmp_path: Path) -> None:
        assert load_folder(tmp_path) == []
