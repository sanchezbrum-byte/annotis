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
    discover_images_recursive,
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
# discover_images_recursive
# ---------------------------------------------------------------------------


class TestDiscoverImagesRecursive:
    """Tests for recursive image discovery across all subfolders."""

    def test_discover_images_recursive_with_root_folder_returns_images_in_root_only(
        self, tmp_image_folder: Path
    ) -> None:
        """Single root folder with images is discovered correctly."""
        # Arrange
        root = tmp_image_folder

        # Act
        paths = discover_images_recursive(root)

        # Assert
        assert len(paths) == 3
        assert all(p.suffix.lower() in {".jpg", ".jpeg"} for p in paths)

    def test_discover_images_recursive_with_subfolders_returns_all_images(
        self, tmp_path: Path
    ) -> None:
        """Images in nested subfolders are discovered recursively."""
        # Arrange: Create nested folder structure with images
        from PIL import Image as PILImage

        subfolder1 = tmp_path / "subfolder1" / "nested"
        subfolder1.mkdir(parents=True)
        subfolder2 = tmp_path / "subfolder2"
        subfolder2.mkdir()

        PILImage.new("RGB", (100, 100)).save(tmp_path / "root.jpg")
        PILImage.new("RGB", (100, 100)).save(subfolder1 / "nested.jpg")
        PILImage.new("RGB", (100, 100)).save(subfolder2 / "sub.jpg")

        # Act
        paths = discover_images_recursive(tmp_path)

        # Assert
        assert len(paths) == 3
        file_names = {p.name for p in paths}
        assert file_names == {"root.jpg", "nested.jpg", "sub.jpg"}

    def test_discover_images_recursive_with_nonimage_files_excludes_them(
        self, tmp_path: Path
    ) -> None:
        """Non-image files are filtered out even in subfolders."""
        # Arrange: Create mixed content in nested structure
        from PIL import Image as PILImage

        subfolder = tmp_path / "subfolder"
        subfolder.mkdir()
        (tmp_path / "notes.txt").write_text("not an image")
        (subfolder / "readme.md").write_text("also not an image")
        (tmp_path / "config.json").write_text("{}")
        PILImage.new("RGB", (100, 100)).save(tmp_path / "image.jpg")
        PILImage.new("RGB", (100, 100)).save(subfolder / "photo.png")

        # Act
        paths = discover_images_recursive(tmp_path)

        # Assert
        assert len(paths) == 2
        file_names = {p.name for p in paths}
        assert file_names == {"image.jpg", "photo.png"}
        assert all(p.suffix.lower() in {".jpg", ".png"} for p in paths)

    def test_discover_images_recursive_with_empty_directory_returns_empty_list(
        self, tmp_path: Path
    ) -> None:
        """Empty directory tree returns no images."""
        # Arrange: Create empty nested structure
        (tmp_path / "subfolder1" / "nested").mkdir(parents=True)
        (tmp_path / "subfolder2").mkdir()

        # Act
        paths = discover_images_recursive(tmp_path)

        # Assert
        assert paths == []

    def test_discover_images_recursive_with_nonexistent_path_raises_error(
        self,
    ) -> None:
        """Nonexistent path raises ValueError with descriptive message."""
        # Arrange
        nonexistent = Path("/nonexistent/path/that/does/not/exist")

        # Act & Assert
        with pytest.raises(ValueError, match="valid directory"):
            discover_images_recursive(nonexistent)

    def test_discover_images_recursive_with_file_path_raises_error(
        self, tmp_jpeg: Path
    ) -> None:
        """File path instead of directory raises ValueError."""
        # Arrange
        file_path = tmp_jpeg

        # Act & Assert
        with pytest.raises(ValueError, match="valid directory"):
            discover_images_recursive(file_path)

    def test_discover_images_recursive_returns_sorted_paths(
        self, tmp_path: Path
    ) -> None:
        """Returned paths are sorted alphabetically."""
        # Arrange: Create images with names that test sorting
        from PIL import Image as PILImage

        PILImage.new("RGB", (100, 100)).save(tmp_path / "zebra.jpg")
        PILImage.new("RGB", (100, 100)).save(tmp_path / "apple.jpg")
        PILImage.new("RGB", (100, 100)).save(tmp_path / "monkey.jpg")

        # Act
        paths = discover_images_recursive(tmp_path)

        # Assert
        assert len(paths) == 3
        names = [p.name for p in paths]
        assert names == ["apple.jpg", "monkey.jpg", "zebra.jpg"]

    def test_discover_images_recursive_with_deeply_nested_folders_finds_all_images(
        self, tmp_path: Path
    ) -> None:
        """Deep nesting of folders does not prevent discovery."""
        # Arrange: Create deeply nested structure
        from PIL import Image as PILImage

        deep_path = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep_path.mkdir(parents=True)
        PILImage.new("RGB", (100, 100)).save(deep_path / "deep.jpg")
        PILImage.new("RGB", (100, 100)).save(tmp_path / "root.jpg")

        # Act
        paths = discover_images_recursive(tmp_path)

        # Assert
        assert len(paths) == 2
        file_names = {p.name for p in paths}
        assert file_names == {"root.jpg", "deep.jpg"}


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
