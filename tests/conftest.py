"""Shared pytest fixtures available to all test modules."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image as PILImage


@pytest.fixture()
def tmp_jpeg(tmp_path: Path) -> Path:
    """Create a minimal 100×100 RGB JPEG for image-loading tests."""
    path = tmp_path / "sample.jpg"
    PILImage.new("RGB", (100, 100), color=(128, 64, 32)).save(str(path))
    return path


@pytest.fixture()
def tmp_image_folder(tmp_path: Path) -> Path:
    """Create a folder with three distinct 50×50 JPEG images."""
    folder = tmp_path / "images"
    folder.mkdir()
    for i in range(3):
        PILImage.new("RGB", (50, 50), color=(i * 80, 100, 200)).save(
            str(folder / f"image_{i:02d}.jpg")
        )
    return folder
