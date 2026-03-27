"""Image discovery, metadata extraction, and QC metric computation.

No UI imports. No database imports. Pure application logic.

QC metric formulas:
  Sharpness:  Var(Laplacian(gray))         — Pech-Pacheco et al. (2000)
  Brightness: mean and std of gray channel
  Contrast:   RMS = std of gray intensities
  Noise:      sqrt(π/6) * mean(|H * I|)   — Immerkaer (1996)
  Saturation: mean of HSV S-channel

cv2 and numpy are imported lazily (inside compute_qc_metrics and helpers)
so that discover_images, extract_metadata, and their unit tests work
without OpenCV being installed.
"""

from __future__ import annotations

import logging
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np

import piexif
from PIL import Image as PILImage

from annotis.domain.errors import ImageLoadError, UnsupportedFormatError
from annotis.domain.models import ImageMetadata, ImageRecord, QCMetrics

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
)


def discover_images(folder: Path) -> list[Path]:
    """Return a sorted list of supported image paths in *folder*.  O(n log n).

    Args:
        folder: Directory to scan (non-recursive).

    Returns:
        Alphabetically sorted list of absolute image file paths.

    Raises:
        ValueError: If *folder* does not exist or is not a directory.
    """
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Not a valid directory: {folder}")
    paths = [p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    return sorted(paths)


def extract_metadata(path: Path) -> ImageMetadata:
    """Extract technical metadata from *path* without loading full pixels.

    Uses PIL for format/EXIF info; filesystem stat for size and dates.

    Args:
        path: Absolute path to an image file.

    Returns:
        Populated ImageMetadata instance.

    Raises:
        ImageLoadError: If the file cannot be opened by PIL.
    """
    try:
        with PILImage.open(path) as img:
            width, height = img.size
            mode = img.mode
            channels = len(img.getbands())
            fmt = (img.format or path.suffix.lstrip(".")).upper()
            exif_data = _extract_exif(img)
    except (ValueError, KeyError, OSError) as exc:
        raise ImageLoadError(f"Cannot open {path}: {exc}") from exc

    return ImageMetadata(
        width=width,
        height=height,
        channels=channels,
        bit_depth=_bit_depth_from_mode(mode),
        color_space=_color_space_from_mode(mode),
        file_size_bytes=path.stat().st_size,
        format=fmt,
        creation_date=_creation_date(path),
        exif=exif_data,
    )


def compute_qc_metrics(path: Path) -> QCMetrics:
    """Compute image quality metrics using OpenCV.  O(w * h).

    cv2 and numpy are imported here to keep the rest of the module usable
    without OpenCV installed (e.g. during CI runs that only test metadata).

    Args:
        path: Absolute path to the image file.

    Returns:
        Populated QCMetrics instance.

    Raises:
        ImageLoadError: If OpenCV cannot decode the file.
    """
    import cv2  # noqa: PLC0415  lazy import
    import numpy as np  # noqa: PLC0415  lazy import

    bgr = cv2.imread(str(path))
    if bgr is None:
        raise ImageLoadError(f"OpenCV cannot decode: {path}")

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    return QCMetrics(
        sharpness=float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        brightness_mean=float(gray.mean()),
        brightness_std=float(gray.std()),
        contrast=float(gray.std()),
        noise_estimate=_estimate_noise(gray),
        saturation_mean=float(hsv[:, :, 1].mean()),
    )


def load_image_record(path: Path) -> ImageRecord:
    """Create a fully-populated ImageRecord for a single image file.

    Args:
        path: Absolute path to the image file.

    Returns:
        ImageRecord with metadata and QC metrics populated; annotations empty.

    Raises:
        UnsupportedFormatError: If the file extension is not in the supported set.
        ImageLoadError: If the image cannot be read.
    """
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(f"Format not supported: {path.suffix}")
    return ImageRecord(
        path=path,
        metadata=extract_metadata(path),
        qc_metrics=compute_qc_metrics(path),
    )


def load_folder(folder: Path) -> list[ImageRecord]:
    """Load all supported images from *folder*, skipping unreadable files.

    O(n) where n = number of discovered image files.

    Args:
        folder: Directory containing image files.

    Returns:
        List of ImageRecord objects for all loadable images.
    """
    records: list[ImageRecord] = []
    for path in discover_images(folder):
        try:
            records.append(load_image_record(path))
        except (ImageLoadError, UnsupportedFormatError):
            logger.warning("Skipping unreadable image: %s", path)
    return records


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _extract_exif(img: PILImage.Image) -> dict[str, Any]:
    """Extract EXIF tags as a plain string-keyed dict.  O(k)."""
    try:
        raw = img.info.get("exif", b"")
        if not raw:
            return {}
        exif_dict = piexif.load(raw)
        result: dict[str, Any] = {}
        for ifd_name, ifd in exif_dict.items():
            if not isinstance(ifd, dict):
                continue
            for tag, val in ifd.items():
                key = piexif.TAGS.get(ifd_name, {}).get(tag, {}).get("name", str(tag))
                result[key] = (
                    val.decode("utf-8", errors="replace")
                    if isinstance(val, bytes)
                    else val
                )
        return result
    except (ValueError, KeyError, struct.error):
        return {}


def _bit_depth_from_mode(mode: str) -> int:
    """Map a PIL image mode string to bits-per-channel.  O(1)."""
    mapping: dict[str, int] = {
        "1": 1,
        "L": 8,
        "P": 8,
        "RGB": 8,
        "RGBA": 8,
        "CMYK": 8,
        "YCbCr": 8,
        "LAB": 8,
        "HSV": 8,
        "I": 32,
        "F": 32,
        "I;16": 16,
        "I;16B": 16,
    }
    return mapping.get(mode, 8)


def _color_space_from_mode(mode: str) -> str:
    """Map a PIL image mode string to a human-readable colour-space name.  O(1)."""
    mapping: dict[str, str] = {
        "1": "BINARY",
        "L": "GRAYSCALE",
        "P": "PALETTE",
        "RGB": "RGB",
        "RGBA": "RGBA",
        "CMYK": "CMYK",
        "YCbCr": "YCBCR",
        "LAB": "LAB",
        "F": "FLOAT32",
        "I": "INT32",
    }
    return mapping.get(mode, mode)


def _creation_date(path: Path) -> datetime | None:
    """Return the filesystem creation timestamp for *path*.  O(1)."""
    try:
        return datetime.fromtimestamp(path.stat().st_ctime, tz=timezone.utc)
    except OSError:
        return None


def _estimate_noise(gray: np.ndarray) -> float:  # type: ignore[type-arg]
    """Estimate noise via the Immerkaer (1996) Laplacian method.  O(w*h).

    σ ≈ sqrt(π/6) * mean(|H * I|)  where H is the 3×3 Laplacian kernel.
    Returns 0.0 for images smaller than 3×3.

    cv2 and numpy are assumed to already be imported by the caller.
    """
    import cv2  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    _noise_kernel = np.array(
        [[1.0, -2.0, 1.0], [-2.0, 4.0, -2.0], [1.0, -2.0, 1.0]],
        dtype=np.float64,
    )
    h, w = gray.shape
    if h <= 2 or w <= 2:
        return 0.0
    filtered = cv2.filter2D(gray, -1, _noise_kernel)
    return float(np.sqrt(np.pi / 6.0) * np.abs(filtered).mean())
